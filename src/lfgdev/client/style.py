# Expose a list of message types
# Expose a list of commands
# Send that message type to the server

import logging

logger = logging.getLogger(__name__)


def input(string: str) -> str:
    return f"\033[95;1;4m{string}\033[0m: "


def response(string: str) -> str:
    return f"\033[34;1;4mResponse\033[0m: {string}"


def header(string: str) -> str:
    return f"\033[34;5;4m{string}\033[0m"
