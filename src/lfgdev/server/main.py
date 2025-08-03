import argparse
import asyncio
import logging
import sys

from lfgdev.server import router
from lfgdev.message import Message
from lfgdev.types import MessageKind, Username
from pathlib import Path
from lfgdev.server.db import Database
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class RequestHandler:
    db: Database

    async def handle(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        message = Message(sent_by=Username("Server"), kind=MessageKind.MALFORMED)
        try:
            if message := await Message.from_stream(stream=reader):
                message = await router.authenticate_message(message)
                message = await router.handle_message(message, self.db)
        except TimeoutError:
            message = Message(
                sent_by=Username("Server"),
                kind=MessageKind.TIMEOUT,
            )
        finally:
            logger.debug(f"Response: {message}")
            writer.write(message.encode())
            writer.close()
            await writer.wait_closed()


async def serve(host: str, port: int, db: Database) -> None:
    request_handler = RequestHandler(db=db)
    server = await asyncio.start_server(
        client_connected_cb=request_handler.handle,
        host=host,
        port=port,
        reuse_port=True,
        reuse_address=True,
        start_serving=False,
    )
    async with server:
        await server.serve_forever()


def main() -> None:
    server_logger = logging.getLogger("lfgdev")
    server_logger.addHandler(logging.StreamHandler(sys.stdout))
    server_logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=1337)
    parser.add_argument("--local-only", action="store_true")
    args = parser.parse_args()

    hostname = "localhost" if args.local_only else "0.0.0.0"
    logger.info("Starting server...")
    logger.info(f"Listening on {hostname}:{args.port}...")
    try:
        with Database.init(path=Path("/tmp/lfg.db")) as db:
            asyncio.run(serve(host=hostname, port=args.port, db=db))
    except KeyboardInterrupt:
        logger.info("Shutting down...")
