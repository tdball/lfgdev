from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from json.decoder import JSONDecodeError
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

TERMINATING_SYMBOL = b"\n"


class MessageType(IntEnum):
    HELLO = 0


def json_serializer(item: object) -> str | None:
    if isinstance(item, UUID):
        return item.hex

    return None


@dataclass(frozen=True, slots=True, kw_only=True)
class Message:
    identifier: UUID = field(default_factory=uuid4)
    type: MessageType

    def to_bytes(self, terminate: bool = False) -> bytes:
        data = json.dumps(asdict(self), default=json_serializer).encode("UTF-8")
        if terminate:
            data = data + TERMINATING_SYMBOL
        return data

    @staticmethod
    def from_bytes(payload: bytes) -> Message | None:
        try:
            data = json.loads(payload.decode("UTF-8"))
            # TODO: Maybe figure out a less explicit way to do this
            return Message(identifier=UUID(data["identifier"]), type=data["type"])
        except JSONDecodeError as e:
            logger.exception(e)
            return None
