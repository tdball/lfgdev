from __future__ import annotations

import logging
import struct
from dataclasses import dataclass, field
from enum import IntEnum
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

TERMINATING_SYMBOL = b"\n"
# TODO: if adding base64 encoded data, is the next addition to the format 64s?
# Should we always use null byte separators?!
MESSAGE_STRUCT_FORMAT = "@Ix16sxI"


class MessageType(IntEnum):
    HELLO = 0


class MessageVersion(IntEnum):
    V1 = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class Message:
    version: MessageVersion = field(default=MessageVersion.V1)
    identifier: UUID = field(default_factory=uuid4)
    type: MessageType
    # Consider using a protocol to extend objects that match
    # expected struct shape for messages inner data

    def to_bytes(self, terminate: bool = False) -> bytes:
        if terminate:
            return bytes(self) + TERMINATING_SYMBOL
        return bytes(self)

    def __bytes__(self) -> bytes:
        return struct.pack(
            MESSAGE_STRUCT_FORMAT, self.version, self.identifier.bytes, self.type
        )

    @staticmethod
    def byte_count() -> int:
        # if high volume of messages this is probably dumb
        return len(bytes(Message(type=MessageType.HELLO)))

    @staticmethod
    def from_bytes(payload: bytes) -> Message | None:
        # Metadata being the first 24 bytes, maybe variable length content until \n char?
        # I guess I'm not sure I could struct unpack that, it's likely I would need to
        # define all messages that might be sent, further how do I turn the remaining bytes into their message?
        # Maybe I have a fixed length type to point to which format to unpack???
        try:
            payload = payload[: Message.byte_count()]
            data = struct.unpack(MESSAGE_STRUCT_FORMAT, payload)
            return Message(
                version=MessageVersion(data[0]),
                identifier=UUID(bytes=data[1]),
                type=MessageType(data[2]),
            )
        except Exception as e:
            logger.exception(e)
            return None
