from __future__ import annotations

import logging
import sys
from socketserver import BaseRequestHandler, TCPServer
from typing import Self
from uuid import uuid4

import lfgpy.router as router
from lfgpy.config import HOST
from lfgpy.message import Message, MessageKind

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


class RequestHandler(BaseRequestHandler):
    def handle(self) -> None:
        client, port = self.client_address
        logger.debug(f"Message from {client}:{port}")
        if message := Message.from_socket(self.request):
            message = router.authenticate_message(message)
            message = router.handle_message(message)
        else:
            # Weird case? Should I instead just throw an exception?
            # I'm not sure it makes sense for the user to have a UUID
            message = Message(
                user_id=uuid4(),
                kind=MessageKind.MALFORMED,
            )
            logger.debug(f"From {self.client_address}: Malformed message receieved")

        logger.debug(f"Response: {message}")
        self.request.sendall(message.encode())


class Server(TCPServer):
    allow_reuse_address = True
    allow_reuse_port = True

    # Added for mypyc support
    def __enter__(self) -> Self:
        return super().__enter__()


def main() -> None:
    with Server(HOST, RequestHandler, bind_and_activate=True) as server:
        try:
            logger.info("Starting server...")
            logger.info(f"Listening on {HOST}...")
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    main()
