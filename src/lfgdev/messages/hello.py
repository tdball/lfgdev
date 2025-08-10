from __future__ import annotations
from struct import Struct
from typing import Self, ClassVar

from lfgdev.types import immutable, ContentType
from lfgdev.messages import decoder


@decoder.register
@immutable
class Hello:
    content_type: ClassVar[ContentType] = ContentType.HELLO
    STRUCT: ClassVar[Struct] = Struct("!xI")

    def encode(self) -> bytes:
        return self.STRUCT.pack(0)

    @classmethod
    def decode(cls, data: bytes) -> Hello:
        return cls()


@decoder.register
@immutable
class NoHello:
    content_type: ClassVar[ContentType] = ContentType.NO_HELLO
    STRUCT: ClassVar[Struct] = Struct("!xI")

    def encode(self) -> bytes:
        return self.STRUCT.pack(0)

    @classmethod
    def decode(cls, data: bytes) -> Self:
        return cls()
