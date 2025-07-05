from __future__ import annotations

import logging
import sys
from os import PathLike
from pathlib import Path
from socketserver import BaseRequestHandler, TCPServer
from typing import Self

import lfgpy._router as router
from lfgpy._db import Database
from lfgpy._message import Message, MessageKind
from lfgpy.config import HOST
from lfgpy.types import Username

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

DB = Database(path=Path("/tmp/lfg.db"))


class ServerMessageHandler(BaseRequestHandler):
    def handle(self) -> None:
        if not DB.path.exists():
            raise Exception(f"Expected database at {DB.path} to exist")
        db = Database(path=Path("/tmp/lfg.db"))
        if message := Message.from_socket(self.request):
            db.save_player(message.username)
            message = router.authenticate_message(message)
            message = router.handle_message(message)
        else:
            message = Message(
                username=Username("Server"),
                kind=MessageKind.MALFORMED,
            )

        logger.debug(f"Response: {message}")
        self.request.sendall(message.encode())


class Server(TCPServer):
    allow_reuse_address = True
    allow_reuse_port = True

    # Added for mypyc support
    def __enter__(self) -> Self:
        return super().__enter__()


def main() -> None:
    DB.create()
    with Server(HOST, ServerMessageHandler) as server:
        try:
            logger.info("Starting server...")
            logger.info(f"Listening on {HOST}...")
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    main()
