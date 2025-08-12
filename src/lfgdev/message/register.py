from __future__ import annotations

from typing import Self

from lfgdev.message.body import Body
from lfgdev.message.decoder import register_decoder
from lfgdev.message.structs import MessageStructs
from lfgdev.types import ContentType, Username, immutable


@immutable
@register_decoder(ContentType.REGISTER)
class Register(Body):
    STRUCT = MessageStructs.USERNAME
    content: Username

    def encode(self) -> bytes:
        # TODO: Testing out no struct on the class
        bytes = MessageStructs.USERNAME.pack(self.content.encode("UTF-8"))
        return bytes

    @classmethod
    def decode(cls, data: bytes) -> Self:
        decoded = MessageStructs.USERNAME.unpack(data)[0]
        return cls(content=decoded)
