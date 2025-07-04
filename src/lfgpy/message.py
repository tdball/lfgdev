from __future__ import annotations

import io
import logging
from collections.abc import Buffer
from dataclasses import dataclass, field
from enum import IntEnum, auto
from socket import socket
from struct import Struct
from typing import Any, Callable, ClassVar, TypeAlias
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

# We're all just integers


class MessageKind(IntEnum):
    HEADER = auto()
    HELLO = auto()
    NO_HELLO = auto()
    MALFORMED = auto()
    LFG = auto()


class MessageValue(IntEnum):
    UNSET = auto()
    COMPUTER_SAYS_NO = auto()


# str is out of scope, gonna keep life simple with integers for now
def _to_bytes(value: Any) -> int | bytes:
    match value:
        case UUID():
            return value.bytes
        case MessageKind() | int():
            return value
        case _:
            raise ValueError(f"Unsupported type for encoding: {type(value)}")


@dataclass(slots=True, frozen=True, kw_only=True)
class Message:
    TERMINATING_SYMBOL: ClassVar[bytes] = b"\n"
    STRUCT: ClassVar[Struct] = Struct(format="!16sxIxI")
    _encoder: ClassVar[Callable[[Any], int | bytes]] = field(default=_to_bytes)

    identifier: UUID = field(default_factory=uuid4)
    kind: MessageKind
    value: MessageValue = field(default=MessageValue.UNSET)

    def encode(self) -> bytes:
        message = Message.STRUCT.pack(
            Message._encoder(self.identifier),
            Message._encoder(self.kind),
            Message._encoder(self.value),
        )
        return message + Message.TERMINATING_SYMBOL

    @classmethod
    def decode(cls, bytes: Buffer) -> Message:
        message = Message.STRUCT.unpack_from(bytes, offset=0)
        identifier = UUID(bytes=message[0])
        kind = MessageKind(message[1])
        # Only handling HELLO for now, but this should be pulled out
        match kind:
            case MessageKind.HELLO:
                return Message(
                    identifier=identifier, kind=kind, value=MessageValue.UNSET
                )
            case MessageKind.NO_HELLO:
                return Message(
                    identifier=identifier,
                    kind=kind,
                    value=MessageValue.COMPUTER_SAYS_NO,
                )
            case _:
                raise NotImplementedError(
                    f"No decoding implemented for message kind: {kind}"
                )

    @staticmethod
    def from_socket(dest: socket) -> Message | None:
        chunk = Message.STRUCT.size + len(Message.TERMINATING_SYMBOL)
        with io.BytesIO() as buffer:
            data: bytes = dest.recv(chunk)
            buffer.write(data)
            while not Message.TERMINATING_SYMBOL in data:
                data = dest.recv(chunk)
                buffer.write(data)
            else:
                data = buffer.getvalue()
                logger.debug(f"{data=}")
                return Message.decode(data)


MessageHandler: TypeAlias = Callable[[Message], Message]
