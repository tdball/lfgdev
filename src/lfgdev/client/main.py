from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, field
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from lfgdev.message import Message, MessageKind
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
    async def connect(
        self,
    ) -> AsyncGenerator[tuple[asyncio.StreamReader, asyncio.StreamWriter], None]:
        reader: asyncio.StreamReader | None = None
        writer: asyncio.StreamWriter | None = None
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

    async def send(self, kind: MessageKind) -> Message:
        async with self.connect() as conn:
            reader, writer = conn
            message = Message(kind=kind, sent_by=self.username)
            logger.debug(f"Request: {message}")
            writer.write(message.encode())
            await writer.drain()
            self.metadata.messages_sent += 1

            if response := await Message.from_stream(stream=reader):
                logger.debug(f"Response from {self.address}:{self.port} - {response}")
                return response
            else:
                raise Exception(
                    f"Empty or Invalid response from - {self.address}:{self.port}"
                )


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

    subparser = parser.add_subparsers()
    send = subparser.add_parser("send")
    send.add_argument("-k", "--kind", choices=MessageKind._member_names_)
    args = parser.parse_args()

    client = Client(username=args.username, address=args.host, port=args.port)
    if args.kind:
        asyncio.run(client.send(kind=MessageKind[args.kind]))
