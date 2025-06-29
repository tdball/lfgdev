from __future__ import annotations

import logging
import struct
from dataclasses import dataclass, field
from enum import IntEnum
from socket import socket
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

TERMINATING_SYMBOL = b"\n"
HEADER_STRUCT_FORMAT = "@Ix16sxI"
HEADER_STRUCT_SIZE = struct.calcsize(HEADER_STRUCT_FORMAT)


class MessageKind(IntEnum):
    HELLO = 0
    MALFORMED = 1


class MessageVersion(IntEnum):
    V1 = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class Message:
    version: MessageVersion = field(default=MessageVersion.V1)
    identifier: UUID = field(default_factory=uuid4)
    kind: MessageKind

    def send(self, socket: socket, terminate: bool = False) -> None:
        payload = bytes(self)
        if terminate:
            payload += TERMINATING_SYMBOL
        socket.sendall(payload)

    def __bytes__(self) -> bytes:
        return struct.pack(
            HEADER_STRUCT_FORMAT, self.version, self.identifier.bytes, self.kind
        )

    @staticmethod
    def from_bytes(payload: bytes) -> Message | None:
        logger.debug(f"Converting to Message from bytes: {payload=}")
        try:
            payload = payload[:HEADER_STRUCT_SIZE]
            data = struct.unpack(HEADER_STRUCT_FORMAT, payload)
            return Message(
                version=MessageVersion(data[0]),
                identifier=UUID(bytes=data[1]),
                kind=MessageKind(data[2]),
            )
        except Exception as e:
            logger.exception(e)
            return None
