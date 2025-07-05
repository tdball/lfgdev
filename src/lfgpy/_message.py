from __future__ import annotations

import io
import logging
from dataclasses import dataclass, field
from socket import socket
from struct import Struct
from typing import Any, ByteString, Callable, ClassVar
from uuid import UUID, uuid4

from lfgpy.types import MessageKind, Username

logger = logging.getLogger(__name__)

# We're all just integers


def _to_bytes(value: Any) -> int | bytes:
    match value:
        case UUID():
            return value.bytes
        case MessageKind() | int():
            return value
        case str():
            return value.encode("UTF-8")
        case _:
            raise ValueError(f"Unsupported type for encoding: {type(value)}")


@dataclass(slots=True, frozen=True, kw_only=True)
class Message:
    _TERMINATING_SYMBOL: ClassVar[bytes] = b"\n"
    _STRUCT: ClassVar[Struct] = Struct(format="!16sx24sxIx")
    _CHUNK_SIZE: ClassVar[int] = _STRUCT.size + len(_TERMINATING_SYMBOL)
    _encoder: ClassVar[Callable[[Any], int | bytes]] = field(default=_to_bytes)

    # Consider, how do I tag a message as from a specific client?
    # maybe ssh public keys?, gonna defer the heck outta that
    identifier: UUID = field(default_factory=uuid4)
    username: Username
    kind: MessageKind

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

    @classmethod
    def decode(cls, bytes: ByteString) -> Message:
        message = Message._STRUCT.unpack_from(bytes, offset=0)
        identifier = UUID(bytes=message[0])

        # Username has a max length of 24, strip the 0s
        username = Username(message[1].decode("UTF-8").strip("\x00"))

        kind = MessageKind(message[2])
        return Message(identifier=identifier, username=Username(username), kind=kind)

    def encode(self) -> bytes:
        message = Message._STRUCT.pack(
            Message._encoder(self.identifier),
            Message._encoder(self.username),
            Message._encoder(self.kind),
        )
        return message + Message._TERMINATING_SYMBOL

    def with_kind(self, kind: MessageKind) -> Message:
        """
        Messages are immutable, this generates a new message
        from the existing one, with a value override
        """
        return Message(
            identifier=self.identifier,
            username=self.username,
            kind=kind,
        )
