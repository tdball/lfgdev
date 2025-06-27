from __future__ import annotations
from dataclasses import dataclass, asdict
import json
from uuid import UUID
from enum import IntEnum


class MessageType(IntEnum):
    HELLO = 0


def json_serializer(item: object) -> str | None:
    if isinstance(item, UUID):
        return item.hex


@dataclass(frozen=True, kw_only=True)
class Message:
    identifier: UUID
    type: MessageType

    def to_bytes(self) -> bytes:
        return json.dumps(asdict(self), default=json_serializer).encode("UTF-8")

    @staticmethod
    def from_bytes(payload: bytes) -> Message:
        data = json.loads(payload.decode("UTF-8"))
        # TODO: Maybe figure out a less explicit way to do this
        return Message(identifier=UUID(data["identifier"]), type=data["type"])
