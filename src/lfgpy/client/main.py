from __future__ import annotations

import argparse
import logging
import socket
import sys
from dataclasses import dataclass, field

from lfgpy.message import Message, MessageKind
from lfgpy.types import Username

logger = logging.getLogger(__name__)


@dataclass(frozen=False, slots=True, kw_only=True)
class ClientMetadata:
    messages_sent: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class Client:
    username: Username
    metadata: ClientMetadata = field(default_factory=ClientMetadata)
    address: str
    port: int

    def __post__init__(self) -> None:
        if len(self.username) > 24:
            raise ValueError("Username too long; Must be less than 24 characters")

    def connect(self) -> socket.socket:
        sock = socket.socket()
        sock.connect((self.address, self.port))
        return sock

    def send(self, kind: MessageKind) -> Message:
        with self.connect() as sock:
            message = Message(kind=kind, sent_by=self.username)
            host, port = sock.getpeername()
            logger.debug(f"Request: {message}")
            sock.sendall(message.encode())
            self.metadata.messages_sent += 1
            if response := Message.from_socket(sock):
                logger.debug(f"Response from {host}:{port} - {response}")
                return response
            else:
                raise Exception(f"Empty or Invalid response from - {host}:{port}")


def cli() -> None:
    client_logger = logging.getLogger("lfgpy")
    client_logger.addHandler(logging.StreamHandler(sys.stdout))
    client_logger.setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser(prog="LFG Client CLI")

    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Server hostname to connect to",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=1337, help="Port to connect to"
    )
    parser.add_argument(
        "-u", "--username", type=Username, help="Username to log in with"
    )
    parser.add_argument(
        "-v", "--debug", action="store_true", help="Enable verbose/debug logging"
    )

    subparser = parser.add_subparsers()
    send = subparser.add_parser("send")
    send.add_argument("-k", "--kind", choices=MessageKind._member_names_)
    args = parser.parse_args()

    client = Client(username=args.username, address=args.host, port=args.port)
    if args.kind:
        client.send(kind=MessageKind[args.kind])
