from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from uuid import UUID, uuid4


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

    def to_bytes(self) -> bytes:
        return json.dumps(asdict(self), default=json_serializer).encode("UTF-8")

    @staticmethod
    def from_bytes(payload: bytes) -> Message:
        data = json.loads(payload.decode("UTF-8"))
        # TODO: Maybe figure out a less explicit way to do this
        return Message(identifier=UUID(data["identifier"]), type=data["type"])
