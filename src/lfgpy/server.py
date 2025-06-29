import logging
import sys
from dataclasses import dataclass
from socketserver import BaseRequestHandler, TCPServer
from threading import Thread

from lfgpy.config import HOST
from lfgpy.message import TERMINATING_SYMBOL, Message

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


@dataclass(frozen=True, slots=True)
class Server:
    def __enter__(self) -> None:
        pass

    def __exit__(self) -> None:
        pass


class RequestHandler(BaseRequestHandler):
    def handle(self) -> None:
        total = 0
        chunk = 10_000
        packet = 2_000
        pending_data = total < chunk

        pieces = [b""]
        terminated = TERMINATING_SYMBOL in pieces[-1]
        while not terminated and pending_data:
            logger.debug("Processing packet")
            logger.debug(f"Terminating byte present {terminated}")
            piece = self.request.recv(packet)
            logger.debug(piece)
            pieces.append(piece)
            total += len(pieces[-1])

            # This is why it was in the while loop
            terminated = TERMINATING_SYMBOL in pieces[-1]
            pending_data = total < chunk

        logger.debug(f"{pieces=}")
        self.data = b"".join(pieces)
        logger.debug(f"{self.data=}")
        if message := Message.from_bytes(self.data):
            logger.debug(f"Received from {self.client_address[0]}: {message}")
            self.request.sendall(message.to_bytes(terminate=True))
        else:
            self.request.sendall(TERMINATING_SYMBOL)


def main() -> None:
    server = TCPServer(
        server_address=HOST, RequestHandlerClass=RequestHandler, bind_and_activate=True
    )
    logger.info(f"Server started on {HOST}")
    server_thread = Thread(target=server.serve_forever, daemon=False)
    try:
        server_thread.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.shutdown()
