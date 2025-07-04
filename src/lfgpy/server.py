from __future__ import annotations

import logging
import sys
from socketserver import BaseRequestHandler, TCPServer
from typing import Self

from lfgpy.config import HOST
from lfgpy.message import Message, MessageKind, MessageValue
from lfgpy.router import Router

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

router = Router()


class RequestHandler(BaseRequestHandler):
    def handle(self) -> None:
        logger.debug(
            f"Incoming Message from {self.client_address[0]}:{self.client_address[1]}"
        )
        if message := Message.from_socket(self.request):
            message = router.authenticate_message(message)
            message = router.handle_message(message)
        else:
            message = Message(
                kind=MessageKind.MALFORMED, value=MessageValue.COMPUTER_SAYS_NO
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
