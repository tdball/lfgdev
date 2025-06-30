from __future__ import annotations

import io
import logging
import struct
from dataclasses import dataclass, field
from enum import IntEnum
from socket import socket
from typing import ClassVar
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class MessageKind(IntEnum):
    HELLO = 0
    NO_HELLO = 1
    MALFORMED = 2
    LFG = 3


@dataclass(frozen=True, slots=True, kw_only=True)
class Message:
    terminating_symbol: ClassVar[bytes] = b"\n"
    header_struct: ClassVar[struct.Struct] = struct.Struct(format="!16sxI")
    body_struct: ClassVar[struct.Struct] = struct.Struct(format="!140s")
    identifier: UUID = field(default_factory=uuid4)
    kind: MessageKind
    body: bytes = field(default_factory=lambda: b"0" * Message.body_struct.size)

    def encode(self) -> bytes:
        data = Message.header_struct.pack(self.identifier.bytes, self.kind)
        data += Message.body_struct.pack(self.body)
        data += Message.terminating_symbol
        return data

    @staticmethod
    def decode(data: bytes) -> Message | None:
        logger.debug(f"Converting to Message from bytes: {data=}")
        try:
            header = Message.header_struct.unpack_from(data, offset=0)
            body = Message.body_struct.unpack_from(
                data, offset=Message.header_struct.size
            )
            return Message(
                identifier=UUID(bytes=header[0]),
                kind=MessageKind(header[1]),
                body=body[0],
            )
        except Exception as e:
            logger.exception(e)
            return None


def terminated(data: bytes) -> bool:
    is_terminated = Message.terminating_symbol in data
    logger.debug(f"bytes: {data!r}")
    logger.debug(f"Terminated: {is_terminated}")
    return is_terminated


def get_message(dest: socket) -> Message | None:
    chunk = Message.header_struct.size + Message.body_struct.size
    with io.BytesIO() as buffer:
        data: bytes = dest.recv(chunk)
        buffer.write(data)
        while not terminated(data):
            data = dest.recv(chunk)
            buffer.write(data)
        else:
            data = buffer.getvalue()
            logger.debug(f"{data=}")
            return Message.decode(data)
