from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from socketserver import BaseRequestHandler, TCPServer
from threading import Thread
from typing import Self

from lfgpy.config import HOST
from lfgpy.message import TERMINATING_SYMBOL, Message

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


@dataclass(frozen=True, slots=True)
class Server:
    tcp: TCPServer

    def __enter__(self) -> Self:
        # self.tcp.server_bind()
        # self.tcp.server_activate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.tcp.server_close()
        self.tcp.shutdown()

    @staticmethod
    def with_address(host: str, port: int) -> Server:
        tcp = TCPServer(
            server_address=(host, port),
            RequestHandlerClass=RequestHandler,
            bind_and_activate=True,
        )
        return Server(tcp=tcp)

    def serve(self) -> None:
        logger.info("Starting server...")
        thread = Thread(target=self.tcp.serve_forever, daemon=False)
        thread.start()
        logger.info(f"Listening on {HOST}")
        thread.join()


class RequestHandler(BaseRequestHandler):
    @staticmethod
    def terminated(data: bytes) -> bool:
        _terminated = TERMINATING_SYMBOL in data
        logger.debug(f"Terminating byte present?: {_terminated}")
        return _terminated

    def handle(self) -> None:
        total = 0
        chunk = 10_000
        packet = 2_000
        pending_data = total < chunk

        pieces = [b""]
        while not RequestHandler.terminated(pieces[-1]) and pending_data:
            logger.debug("Processing packet")
            piece = self.request.recv(packet)
            pieces.append(piece)
            total += len(pieces[-1])
            pending_data = total < chunk

        self.data = b"".join(pieces)
        if message := Message.from_bytes(self.data):
            logger.debug(f"Received from {self.client_address[0]}: {message}")
            message.send(socket=self.request, terminate=True)
        else:
            self.request.sendall(TERMINATING_SYMBOL)


def main() -> None:
    with Server.with_address(host=HOST[0], port=HOST[1]) as server:
        try:
            server.serve()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
