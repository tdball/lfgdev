from __future__ import annotations

import logging
import sys
from socketserver import BaseRequestHandler, TCPServer

from lfgpy.config import HOST
from lfgpy.message import Message, MessageKind, MessageValue
from lfgpy.router import Router

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


class RequestHandler(BaseRequestHandler):
    def handle(self) -> None:
        logger.debug(
            f"Incoming Message from {self.client_address[0]}:{self.client_address[1]}"
        )
        if message := Message.from_socket(self.request):
            router = Router.for_message_kind(message.kind)
            message = router.apply(message)
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
