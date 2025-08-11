from __future__ import annotations

from struct import Struct
from typing import ClassVar, Self

from lfgdev.message.body import Body
from lfgdev.message.decoder import register_decoder
from lfgdev.types import ContentType, immutable


@register_decoder
@immutable
class Hello(Body):
    content_type: ClassVar[ContentType] = ContentType.HELLO
    STRUCT: ClassVar[Struct] = Struct("!xI")
    model: None

    def encode(self) -> bytes:
        return self.STRUCT.pack(0)

    @classmethod
    def decode(cls, data: bytes) -> Hello:
        return cls(model=None)


@register_decoder
@immutable
class NoHello(Body):
    content_type: ClassVar[ContentType] = ContentType.NO_HELLO
    STRUCT: ClassVar[Struct] = Struct("!xI")
    model: None

    def encode(self) -> bytes:
        return self.STRUCT.pack(0)

    @classmethod
    def decode(cls, data: bytes) -> Self:
        return cls(model=None)
