from __future__ import annotations
from struct import Struct
from typing import Self, ClassVar, ByteString

from lfgdev.protocol import streamable, Message, MessageKind
from lfgdev.types import immutable


# Maybe define request/response? A Request has no data, a response does.
# Instead maybe just make the data optional? Seems like that could
# leave all the code to deal with optional all over
@streamable
@immutable
class LastSeen(Message):
    kind: ClassVar[MessageKind] = MessageKind.LAST_SEEN
    _STRUCT: ClassVar[Struct] = Struct("!xI")

    last_seen: int | None = None

    def encode(self) -> bytes:
        if self.last_seen is not None:
            bytes = self._STRUCT.pack(self.last_seen)
        else:
            bytes = self._STRUCT.pack(0)

        return bytes

    @classmethod
    def decode(cls, bytes: ByteString) -> Self:
        decoded = cls._STRUCT.unpack(bytes)
        # TODO: Validation?
        return cls(last_seen=decoded[0])
