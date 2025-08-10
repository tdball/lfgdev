from __future__ import annotations

from struct import Struct
from typing import ClassVar, Self

from lfgdev.messages import decoder
from lfgdev.types import ContentType, immutable


@decoder.register
@immutable
class LastSeen:
    content_type: ClassVar[ContentType] = ContentType.LAST_SEEN
    STRUCT: ClassVar[Struct] = Struct("!xI")

    last_seen: int | None = None

    def encode(self) -> bytes:
        if self.last_seen is not None:
            bytes = self.STRUCT.pack(self.last_seen)
        else:
            bytes = self.STRUCT.pack(0)

        return bytes

    @classmethod
    def decode(cls, data: bytes) -> Self:
        decoded = cls.STRUCT.unpack(data)[0]
        # TODO: Validation?
        return cls(last_seen=decoded)
