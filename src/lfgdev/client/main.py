from __future__ import annotations

import asyncio
import logging
from asyncio import StreamReader, StreamWriter
from contextlib import asynccontextmanager
from dataclasses import field
from typing import AsyncGenerator

from lfgdev.client.cli import cli
from lfgdev.messages import Header, Hello, LastSeen, Message
from lfgdev.types import ContentType, Username, immutable, mutable

LOG = logging.getLogger(__name__)


@mutable
class ClientMetadata:
    messages_sent: int = 0


@immutable
class Client:
    username: Username
    metadata: ClientMetadata = field(default_factory=ClientMetadata)
    address: str
    port: int

    def __post__init__(self) -> None:
        if len(self.username) > 24:
            raise ValueError("Username too long; Must be less than 24 characters")

    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[tuple[StreamReader, StreamWriter], None]:
        reader: StreamReader | None = None
        writer: StreamWriter | None = None
        for _ in range(10):
            try:
                reader, writer = await asyncio.open_connection(
                    host=self.address, port=self.port
                )
                break
            except OSError as error:
                LOG.error(error)
                if "Connect call failed" in error.args[0]:
                    await asyncio.sleep(0.1)
                raise

        if reader is None or writer is None:
            raise ConnectionError(
                f"Unable to establish connection to {self.address}:{self.port}"
            )
        try:
            yield reader, writer
        finally:
            writer.close()
            await writer.wait_closed()

    async def send(self, message: Message) -> Message | None:
        async with self.connect() as conn:
            reader, writer = conn
            try:
                await message.send(writer)
                self.metadata.messages_sent += 1
                reply = await Message.receive(stream=reader)
                LOG.debug(f"Received reply: {reply}")
                return reply
            except TimeoutError:
                LOG.error("Request timed out")
        return None


def main() -> None:
    args = cli()
    client = Client(
        username=args.username,
        address=args.host,
        port=args.port,
    )

    if args.command == "send":
        message_kind = ContentType.from_name(args.kind)
        header = Header(sender=client.username, content_type=message_kind)

        match message_kind:
            case ContentType.HELLO:
                message = Message(header=header, body=Hello())
            case ContentType.LAST_SEEN:
                message = Message(header=header, body=LastSeen())
            case _:
                raise NotImplementedError("Unsupported message type")

        asyncio.run(client.send(message))
