from __future__ import annotations
from struct import Struct
from typing import Self, ClassVar, ByteString

from lfgdev.protocol import deserialize, serialize, Message, MessageKind
from lfgdev.types import immutable


@serialize
@deserialize
@immutable
class LastSeen(Message):
    kind: ClassVar[MessageKind] = MessageKind.LAST_SEEN
    _STRUCT: ClassVar[Struct] = Struct("!xI")

    last_seen: int

    def encode(self) -> bytes:
        return self._STRUCT.pack(self.last_seen)

    @classmethod
    def decode(cls, bytes: ByteString) -> Self:
        decoded = cls._STRUCT.unpack(bytes)
        # TODO: Validation?
        return cls(last_seen=decoded[0])
