import argparse
import logging
import socket
import sys

from lfgpy import _router as router
from lfgpy._message import Message
from lfgpy.types import MessageKind, Username

logger = logging.getLogger(__name__)


def handle_request(client: socket.socket) -> None:
    message = Message(
        sent_by=Username("Server"),
        kind=MessageKind.MALFORMED,
    )
    try:
        if message := Message.from_socket(client):
            message = router.authenticate_message(message)
            message = router.handle_message(message)
    except TimeoutError:
        addr, port = client.getsockname()
        logger.debug(f"Timeout from client - {addr}:{port}")
        message = Message(
            sent_by=Username("Server"),
            kind=MessageKind.TIMEOUT,
        )

    finally:
        logger.debug(f"Response: {message}")
        client.sendall(message.encode())


def serve(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind((host, port))
        sock.listen(1)
        while True:
            connection, client = sock.accept()
            handle_request(connection)
            connection.close()


def main() -> None:
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=1337)
    parser.add_argument("--local-only", action="store_true")
    args = parser.parse_args()

    hostname = "localhost" if args.local_only else "0.0.0.0"
    logger.info("Starting server...")
    logger.info(f"Listening on {hostname}:{args.port}...")
    try:
        serve(host=hostname, port=args.port)
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == "__main__":
    main()
