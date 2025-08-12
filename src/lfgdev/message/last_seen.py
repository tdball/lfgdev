from __future__ import annotations

from struct import Struct
from typing import ClassVar, Self

from lfgdev.message.body import Body
from lfgdev.message.decoder import register_decoder
from lfgdev.types import ContentType, immutable


@immutable
@register_decoder(ContentType.LAST_SEEN)
class LastSeen(Body):
    STRUCT: ClassVar[Struct] = Struct("!xI")
    content: int | None

    def encode(self) -> bytes:
        if self.content is not None:
            bytes = self.STRUCT.pack(self.content)
        else:
            bytes = self.STRUCT.pack(0)

        return bytes

    @classmethod
    def decode(cls, data: bytes) -> Self:
        decoded = cls.STRUCT.unpack(data)[0]
        return cls(content=decoded)
