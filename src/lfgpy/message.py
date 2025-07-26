from __future__ import annotations
import asyncio
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
    _STRUCT: ClassVar[Struct] = Struct(format="!16sx24sxIx")
    _encoder: ClassVar[Callable[[Any], int | bytes]] = field(default=_to_bytes)

    # TODO: Maybe SSH keys for user id/registration?
    identifier: UUID = field(default_factory=uuid4)
    sent_by: Username
    kind: MessageKind

    @staticmethod
    def from_socket(dest: socket, timeout: float = 0.5) -> Message:
        dest.settimeout(timeout)
        # Probably naive, doesn't handle messages it doesn't expect
        data: bytes = dest.recv(Message._STRUCT.size)
        logger.debug(f"Bytes: {data!r}")
        return Message.decode(data)

    @staticmethod
    async def from_stream(stream: asyncio.StreamReader) -> Message:
        data: bytes = await stream.readexactly(Message._STRUCT.size)
        logger.debug(f"Bytes: {data!r}")
        return Message.decode(data)

    @classmethod
    def decode(cls, bytes: ByteString) -> Message:
        message = Message._STRUCT.unpack_from(bytes, offset=0)
        identifier = UUID(bytes=message[0])
        # Username has a max length of 24, strip the 0s
        username = Username(message[1].decode("UTF-8").strip("\x00"))
        kind = MessageKind(message[2])

        return Message(identifier=identifier, sent_by=Username(username), kind=kind)

    def encode(self) -> bytes:
        message = Message._STRUCT.pack(
            Message._encoder(self.identifier),
            Message._encoder(self.sent_by),
            Message._encoder(self.kind),
        )
        return message

    def with_kind(self, kind: MessageKind) -> Message:
        """
        Messages are immutable, this generates a new message
        from the existing one, with a value override
        """
        return Message(
            identifier=self.identifier,
            sent_by=self.sent_by,
            kind=kind,
        )
