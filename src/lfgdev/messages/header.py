from __future__ import annotations
import asyncio
from dataclasses import field
from typing import Any, Callable, ClassVar, ByteString, Self
from uuid import UUID, uuid4
from struct import Struct
from lfgdev.messages.kind import MessageKind

from lfgdev.types import Username, immutable


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


@immutable
class Header:
    encoder: ClassVar[Callable[[Any], int | bytes]] = field(default=_to_bytes)
    STRUCT: ClassVar[Struct] = Struct(format="!16sx24sxI")

    identifier: UUID = field(default_factory=uuid4)
    sent_by: Username
    kind: MessageKind

    def encode(self) -> bytes:
        message = Header.STRUCT.pack(
            Header.encoder(self.identifier),
            Header.encoder(self.sent_by),
            Header.encoder(self.kind),
        )
        return message

    @classmethod
    def decode(cls, bytes: ByteString) -> Self:
        data = cls.STRUCT.unpack_from(bytes, offset=0)
        identifier = UUID(bytes=data[0])
        # Username has a max length of 24, strip the 0s
        username = Username(data[1].decode("UTF-8").strip("\x00"))
        kind = MessageKind(data[2])
        return cls(identifier=identifier, sent_by=username, kind=kind)

    @classmethod
    async def from_stream(cls, stream: asyncio.StreamReader) -> Header:
        data = await stream.readexactly(cls.STRUCT.size)
        return cls.decode(data)

    async def to_stream(self, stream: asyncio.StreamWriter) -> None:
        stream.write(self.encode())
