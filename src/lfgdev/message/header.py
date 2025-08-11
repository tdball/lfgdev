from __future__ import annotations

from dataclasses import field
from struct import Struct
from typing import ClassVar
from uuid import UUID, uuid4

from lfgdev.types import ContentType, Username, immutable


@immutable
class Header:
    STRUCT: ClassVar[Struct] = Struct("!16sx24sxI")
    identifier: UUID = field(default_factory=uuid4)
    content_type: ContentType
    sender: Username

    @staticmethod
    def decode(data: bytes) -> Header:
        identifier, sender, content_type = Header.STRUCT.unpack(data)

        sender = sender.decode("UTF-8").strip("\x00")
        sender = Username(sender)

        return Header(
            identifier=UUID(bytes=identifier),
            sender=Username(sender),
            content_type=ContentType(content_type),
        )

    def encode(self) -> bytes:
        return Header.STRUCT.pack(
            self.identifier.bytes,
            self.sender.encode("UTF-8"),
            self.content_type,
        )
