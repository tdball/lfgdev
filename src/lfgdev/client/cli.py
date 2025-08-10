import argparse
import logging
import sys

from lfgdev.types import ContentType, Username


def cli() -> argparse.Namespace:
    client_logger = logging.getLogger("lfgdev")
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
        "-p",
        "--port",
        type=int,
        default=1337,
        help="Port to connect to",
    )
    parser.add_argument(
        "-u",
        "--username",
        type=Username,
        help="Username to log in with",
    )
    parser.add_argument(
        "-v",
        "--debug",
        action="store_true",
        help="Enable verbose/debug logging",
    )

    # `send` command
    subparser = parser.add_subparsers(dest="command")
    send = subparser.add_parser("send")
    send.add_argument("-k", "--kind", choices=ContentType._member_names_)

    return parser.parse_args()
