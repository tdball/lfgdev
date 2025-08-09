import argparse
import asyncio
from asyncio import StreamReader, StreamWriter
import logging
import sys

from lfgdev.protocol import Header, Incoming, Outgoing, MessageKind
from lfgdev.messages import NoHello, LastSeen
from lfgdev.types import Username, immutable
from pathlib import Path
from lfgdev.server.db import Database
from dataclasses import replace

LOG = logging.getLogger(__name__)


@immutable
class RequestHandler:
    db: Database

    async def route(self, request: Incoming) -> Outgoing:
        # Middleware?
        if self.db.find_by_username(request.header.sent_by) is None:
            self.db.save(request.header.sent_by)
        else:
            self.db.update(request.header.sent_by)

        match request.message.kind:
            case MessageKind.HELLO | MessageKind.NO_HELLO:
                # Not sure how ergonomic this will be as more messages are added
                response_header = Header(
                    identifier=request.header.identifier,
                    sent_by=Username("SERVER"),
                    content_type=MessageKind.NO_HELLO,
                )
                return Outgoing(header=response_header, message=NoHello())

            case MessageKind.LAST_SEEN:
                response_header = replace(request.header, sent_by=Username("SERVER"))
                if player := self.db.find_by_username(request.header.sent_by):
                    return Outgoing(
                        header=response_header,
                        message=LastSeen(last_seen=player.last_seen),
                    )
                else:
                    return Outgoing(
                        header=response_header, message=LastSeen(last_seen=0)
                    )

            case _:
                response_header = replace(
                    request.header,
                    content_type=MessageKind.CLIENT_ERROR,
                    sent_by=Username("SERVER"),
                )
                return Outgoing(header=response_header, message=NoHello())

    async def handle(self, reader: StreamReader, writer: StreamWriter) -> None:
        try:
            request = await Incoming.get(stream=reader)
            response = await self.route(request=request)
            await response.send(stream=writer)
        except TimeoutError:
            LOG.error("TimeoutError occurred")
        finally:
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
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        server_logger.setLevel(logging.DEBUG)
    else:
        server_logger.setLevel(logging.INFO)

    try:
        hostname = "localhost" if args.local_only else "0.0.0.0"
        LOG.info("Starting server...")
        with Database.init(path=Path("/tmp/lfg.db")) as db:
            LOG.info(f"Listening on {hostname}:{args.port}...")
            asyncio.run(serve(host=hostname, port=args.port, db=db))
    except KeyboardInterrupt:
        LOG.info("Shutting down...")
