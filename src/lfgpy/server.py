from __future__ import annotations

import logging
import sys
from socketserver import BaseRequestHandler, TCPServer

from lfgpy.config import HOST
from lfgpy.message import Message, MessageKind, get_message

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


class RequestHandler(BaseRequestHandler):
    def echo(self, message: Message) -> Message:
        logger.debug(f"From {self.client_address}: {message}")
        logger.debug("Response: ECHO")
        return message

    def lfg(self, message: Message) -> Message:
        logger.debug("LETS FRIGGEN GOOOOO")
        return message

    def say_no_hello(self) -> Message:
        return Message(kind=MessageKind.NO_HELLO)

    # Middleware?
    def route_message(self, message: Message) -> Message:
        # TODO: Find out how to return the 'match'
        match message.kind:
            case MessageKind.HELLO:
                return self.say_no_hello()
            case MessageKind.LFG:
                return self.lfg(message)
            case _:
                return Message(kind=MessageKind.MALFORMED)

    def handle(self) -> None:
        logger.debug(
            f"Incoming Message from {self.client_address[0]}:{self.client_address[1]}"
        )
        if message := get_message(self.request):
            message = self.route_message(message)
        else:
            message = Message(kind=MessageKind.MALFORMED)
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
