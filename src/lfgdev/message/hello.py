from __future__ import annotations

from struct import Struct
from typing import ClassVar, Self

from lfgdev.message.body import Body
from lfgdev.message.decoder import register_decoder
from lfgdev.types import ContentType, immutable


@immutable
@register_decoder(ContentType.HELLO)
class Hello(Body):
    STRUCT: ClassVar[Struct] = Struct("!xI")
    content: None = None

    def encode(self) -> bytes:
        return self.STRUCT.pack(0)

    @classmethod
    def decode(cls, data: bytes) -> Self:
        return cls()


@immutable
@register_decoder(ContentType.NO_HELLO)
class NoHello(Body):
    STRUCT: ClassVar[Struct] = Struct("!xI")
    content: None = None

    def encode(self) -> bytes:
        return self.STRUCT.pack(0)

    @classmethod
    def decode(cls, data: bytes) -> Self:
        return cls()
