from __future__ import annotations
from struct import Struct
from typing import Self, ClassVar, ByteString

from lfgdev.protocol import deserialize, serialize, Message, MessageKind
from lfgdev.types import immutable


@serialize
@deserialize
@immutable
class Hello(Message):
    _STRUCT = Struct("!xI")
    kind: ClassVar[MessageKind] = MessageKind.HELLO

    def encode(self) -> bytes:
        return self._STRUCT.pack(self.kind)

    @classmethod
    def decode(cls, bytes: ByteString) -> Self:
        # kind = cls._STRUCT.unpack(data)[0]
        return cls()


@serialize
@deserialize
@immutable
class NoHello(Message):
    kind: ClassVar[MessageKind] = MessageKind.NO_HELLO
    _STRUCT = Struct("!xI")

    def encode(self) -> bytes:
        return self._STRUCT.pack(self.kind)

    @classmethod
    def decode(cls, bytes: ByteString) -> Self:
        # kind = cls._STRUCT.unpack(data)[0]
        return cls()
