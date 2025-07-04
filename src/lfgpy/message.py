from __future__ import annotations

import io
import logging
from collections.abc import Buffer
from dataclasses import dataclass, field
from enum import IntEnum, auto
from socket import socket
from struct import Struct
from typing import Any, Callable, ClassVar
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

# We're all just integers


class MessageKind(IntEnum):
    HELLO = auto()
    NO_HELLO = auto()
    MALFORMED = auto()
    LFG = auto()


class MessageValue(IntEnum):
    UNSET = auto()


class HelloValue(IntEnum):
    UNSET = auto()
    COMPUTER_SAYS_NO = auto()


def _to_bytes(value: Any) -> int | bytes:
    match value:
        case UUID():
            return value.bytes
        case MessageKind() | int():
            return value
        case _:
            raise ValueError(f"Unsupported type for encoding: {type(value)}")


@dataclass(slots=True, frozen=True, kw_only=True)
class Message:
    _TERMINATING_SYMBOL: ClassVar[bytes] = b"\n"
    _STRUCT: ClassVar[Struct] = Struct(format="!16sxIxI")
    _CHUNK_SIZE: ClassVar[int] = _STRUCT.size + len(_TERMINATING_SYMBOL)
    _encoder: ClassVar[Callable[[Any], int | bytes]] = field(default=_to_bytes)

    identifier: UUID = field(default_factory=uuid4)
    kind: MessageKind
    value: int = field(default=MessageValue.UNSET)

    def encode(self) -> bytes:
        message = Message._STRUCT.pack(
            Message._encoder(self.identifier),
            Message._encoder(self.kind),
            Message._encoder(self.value),
        )
        return message + Message._TERMINATING_SYMBOL

    @classmethod
    def decode(cls, bytes: Buffer) -> Message:
        message = Message._STRUCT.unpack_from(bytes, offset=0)
        identifier = UUID(bytes=message[0])
        kind = MessageKind(message[1])
        # Consider handling the lookup here. Maybe that map belongs here
        # instead of router?
        value = message[2]
        return Message(identifier=identifier, kind=kind, value=value)

    @staticmethod
    def from_socket(dest: socket) -> Message | None:
        with io.BytesIO() as buffer:
            data: bytes = dest.recv(Message._CHUNK_SIZE)
            buffer.write(data)
            while not Message._TERMINATING_SYMBOL in data:
                data = dest.recv(Message._CHUNK_SIZE)
                buffer.write(data)
            else:
                data = buffer.getvalue()
                logger.debug(f"{data=}")
                return Message.decode(data)

    def with_value(self, value: int) -> Message:
        return Message(identifier=self.identifier, kind=self.kind, value=value)
