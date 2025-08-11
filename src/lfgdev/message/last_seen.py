from __future__ import annotations

from struct import Struct
from typing import ClassVar, Self

from lfgdev.message.body import Body
from lfgdev.message.decoder import register_decoder
from lfgdev.types import ContentType, immutable, mutable


@mutable
class LastSeenModel:
    last_seen: int | None = None


@immutable
@register_decoder
class LastSeen(Body):
    content_type: ClassVar[ContentType] = ContentType.LAST_SEEN
    STRUCT: ClassVar[Struct] = Struct("!xI")
    model: LastSeenModel

    def encode(self) -> bytes:
        if self.model.last_seen is not None:
            bytes = self.STRUCT.pack(self.model.last_seen)
        else:
            bytes = self.STRUCT.pack(0)

        return bytes

    @classmethod
    def decode(cls, data: bytes) -> Self:
        decoded = cls.STRUCT.unpack(data)[0]
        model = LastSeenModel(last_seen=decoded)
        return cls(model=model)
