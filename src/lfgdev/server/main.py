import argparse
import asyncio
import logging
import sys

from pathlib import Path
from lfgdev.server.db import Database
from lfgdev.server.request_handler import RequestHandler

LOG = logging.getLogger(__name__)


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
