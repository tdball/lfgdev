import io
import logging
from socket import socket

from lfgpy.message import TERMINATING_SYMBOL, Message

logger = logging.getLogger(__name__)

CHUNK_SIZE = 64


def _terminated(data: bytes) -> bool:
    is_terminated = TERMINATING_SYMBOL in data
    logger.debug(f"bytes: {data!r}")
    logger.debug(f"Terminated: {is_terminated}")
    return is_terminated


# Does this belong on the Message class?
def message_parser(sock: socket) -> Message | None:
    with io.BytesIO() as buffer:
        chunk: bytes = sock.recv(CHUNK_SIZE)
        buffer.write(chunk)
        while not _terminated(chunk):
            piece: bytes = sock.recv(CHUNK_SIZE)
            buffer.write(piece)
        else:
            data = buffer.getvalue()
            logger.debug(f"{data=}")
            return Message.from_bytes(data)
