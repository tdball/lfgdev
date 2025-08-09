from __future__ import annotations
from enum import IntEnum, auto
from typing import cast


class MessageKind(IntEnum):
    @staticmethod
    def for_name(name: str) -> MessageKind | None:
        # Maybe a more elegant way to handle this, but
        # _member_map_ returns `Enum` not `MessageKind`
        return cast(MessageKind, MessageKind._member_map_.get(name))

    HELLO = auto()
    NO_HELLO = auto()

    # Error responses
    MALFORMED = auto()
    TIMEOUT = auto()
