from enum import IntEnum, auto


class MessageKind(IntEnum):
    HELLO = auto()
    NO_HELLO = auto()

    # Error responses
    MALFORMED = auto()
    TIMEOUT = auto()
