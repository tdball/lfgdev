import argparse
import asyncio
from asyncio import StreamReader, StreamWriter
import logging
import sys

from lfgdev.messages import Header, Response, Message, MessageKind, NoHello
from lfgdev.types import Username
from pathlib import Path
from lfgdev.server.db import Database
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class RequestHandler:
    db: Database

    async def route(self, header: Header, request: Message) -> Message:
        # Middleware?
        if self.db.find_by_username(header.sent_by) is None:
            self.db.save(header.sent_by)
        else:
            self.db.update(header.sent_by)

        match request.kind:
            case MessageKind.HELLO:
                return NoHello()
            case MessageKind.NO_HELLO:
                return request
            case _:
                raise NotImplementedError("Ohhhh how did we get here.")

    async def handle(self, reader: StreamReader, writer: StreamWriter) -> None:
        logger.debug("Incoming request")
        try:
            header = await Header.from_stream(stream=reader)
            logger.debug(f"Request header: {header}")

            # I'm not sure Response is the right name for this class
            response = await Response.deserialize(header=header, stream=reader)
            logger.debug(f"Request body: {response}")

            # Absolutely needs a better data structure overall
            message = await self.route(header=header, request=response.body)
            # Whoops, forgot to build a header and send with response.
            # Think of a way to logically prevent this from happening
            header = Header(
                identifier=header.identifier,
                kind=message.kind,
                sent_by=Username("SERVER"),
            )
            logger.debug(f"Response header: {header}")
            await header.to_stream(stream=writer)
            logger.debug(f"Response body: {response}")
            await message.to_stream(stream=writer)

        finally:
            logger.debug("Closing stream")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            logger.debug("Stream closed")


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

    try:
        hostname = "localhost" if args.local_only else "0.0.0.0"
        logger.info("Starting server...")
        with Database.init(path=Path("/tmp/lfg.db")) as db:
            logger.info(f"Listening on {hostname}:{args.port}...")
            asyncio.run(serve(host=hostname, port=args.port, db=db))
    except KeyboardInterrupt:
        logger.info("Shutting down...")
