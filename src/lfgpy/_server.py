from __future__ import annotations

import logging
import sys
from socketserver import BaseRequestHandler, TCPServer
from typing import Self

import lfgpy._router as router
from lfgpy._message import Message, MessageKind
from lfgpy.config import HOST
from lfgpy.types import Username

logger = logging.getLogger(__name__)


class ServerMessageHandler(BaseRequestHandler):
    def handle(self) -> None:
        # Default message, presume error, will override
        # if successful
        message = Message(
            sent_by=Username("Server"),
            kind=MessageKind.MALFORMED,
        )
        try:
            if message := Message.from_socket(self.request):
                message = router.authenticate_message(message)
                message = router.handle_message(message)
        finally:
            logger.debug(f"Response: {message}")
            self.request.sendall(message.encode())


class Server(TCPServer):
    # This almost definitely needs to be threaded
    allow_reuse_address = True
    allow_reuse_port = True

    # Added for mypyc support
    def __enter__(self) -> Self:
        return super().__enter__()


def main() -> None:
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)
    with Server(HOST, ServerMessageHandler) as server:
        server.socket.settimeout(5)
        try:
            logger.info("Starting server...")
            logger.info(f"Listening on {HOST}...")
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    main()
