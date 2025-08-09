from __future__ import annotations
from asyncio import StreamReader, StreamWriter
from struct import Struct
from typing import Self, ClassVar, ByteString

from lfgdev.messages.kind import MessageKind
from lfgdev.messages.protocol import deserialize, serialize
from lfgdev.types import immutable


@serialize
@deserialize
@immutable
class Hello:
    _STRUCT = Struct("!xI")
    kind: ClassVar[MessageKind] = MessageKind.HELLO

    def encode(self) -> bytes:
        return self._STRUCT.pack(self.kind)

    @classmethod
    def decode(cls, data: ByteString) -> Self:
        # kind = cls._STRUCT.unpack(data)[0]
        return cls()

    @classmethod
    async def from_stream(cls, stream: StreamReader) -> Self:
        await stream.readexactly(cls._STRUCT.size)
        # Silly, but leaving for now, a pattern has to emerge
        # data = cls._STRUCT.unpack(bytes)
        return cls()

    async def to_stream(self, stream: StreamWriter) -> None:
        stream.write(self.encode())


@serialize
@deserialize
@immutable
class NoHello:
    kind: ClassVar[MessageKind] = MessageKind.NO_HELLO
    _STRUCT = Struct("!xI")

    def encode(self) -> bytes:
        return self._STRUCT.pack(self.kind)

    @classmethod
    def decode(cls, data: ByteString) -> Self:
        # kind = cls._STRUCT.unpack(data)[0]
        return cls()

    @classmethod
    async def from_stream(cls, stream: StreamReader) -> Self:
        await stream.readexactly(cls._STRUCT.size)
        # Silly, but leaving for now, a pattern has to emerge
        # data = cls._STRUCT.unpack(bytes)
        return cls()

    async def to_stream(self, stream: StreamWriter) -> None:
        stream.write(self.encode())
