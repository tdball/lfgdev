from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, field
import asyncio
from asyncio import StreamReader, StreamWriter
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from lfgdev.messages import MessageKind, Hello, Header, Incoming, Outgoing
from lfgdev.types import Username

logger = logging.getLogger(__name__)


@dataclass(frozen=False, slots=True, kw_only=True)
class ClientMetadata:
    messages_sent: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
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
                logger.error(error)
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

    async def send(self, request: Outgoing) -> Incoming:
        async with self.connect() as conn:
            reader, writer = conn
            await request.send(writer)
            self.metadata.messages_sent += 1
            return await Incoming.get(stream=reader)


def cli() -> None:
    client_logger = logging.getLogger("lfgdev")
    client_logger.addHandler(logging.StreamHandler(sys.stdout))
    client_logger.setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser(prog="LFG Client CLI")

    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Server hostname to connect to",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=1337, help="Port to connect to"
    )
    parser.add_argument(
        "-u", "--username", type=Username, help="Username to log in with"
    )
    parser.add_argument(
        "-v", "--debug", action="store_true", help="Enable verbose/debug logging"
    )

    # `send` command
    subparser = parser.add_subparsers(dest="command")
    send = subparser.add_parser("send")
    send.add_argument("-k", "--kind", choices=MessageKind._member_names_)

    args = parser.parse_args()

    client = Client(username=args.username, address=args.host, port=args.port)

    if args.command == "send":
        message_kind = MessageKind.from_name(args.kind)
        if message_kind is None:
            raise ValueError("Unknown message type")

        header = Header(sent_by=client.username, kind=message_kind)
        match message_kind:
            case MessageKind.HELLO:
                message = Outgoing(header=header, message=Hello())
                asyncio.run(client.send(request=message))
            case _:
                raise NotImplementedError("Unsupported message type")
