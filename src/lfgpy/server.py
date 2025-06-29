from __future__ import annotations

import logging
import sys
from socketserver import BaseRequestHandler, TCPServer
from threading import Thread

from lfgpy.config import HOST
from lfgpy.message import Message, MessageKind
from lfgpy.parser import message_parser

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


class RequestHandler(BaseRequestHandler):
    def echo(self, message: Message) -> None:
        logger.debug(f"From {self.client_address}: {message}")
        logger.debug("Response: ECHO")
        message.send(socket=self.request, terminate=True)

    def route_message(self, message: Message) -> None:
        match message.kind:
            case MessageKind.HELLO:
                self.echo(message)

    def handle(self) -> None:
        if message := message_parser(sock=self.request):
            self.route_message(message)
        else:
            message = Message(kind=MessageKind.MALFORMED)
            logger.debug(f"From {self.client_address}: Malformed message receieved")
            logger.debug(f"Response: {message}")
            message.send(socket=self.request, terminate=True)


class Server(TCPServer):
    # TODO: Refactor this to use socket and frozen slotted dataclasses
    allow_reuse_address = True
    allow_reuse_port = True


def main() -> None:
    with Server(HOST, RequestHandler, bind_and_activate=True) as server:
        try:
            logger.info("Starting server...")
            logger.info(f"Listening on {HOST}...")
            server.serve_forever()
            # thread = Thread(target=server.serve_forever, daemon=True)
            # thread.start()
            # logger.info(f"Listening on {HOST}")
            # thread.join()
        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    main()
