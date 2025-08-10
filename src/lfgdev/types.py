from __future__ import annotations
from typing import NewType, TypeVar, Callable, TypeAlias, Self, Protocol, ClassVar
from typing import dataclass_transform
from dataclasses import dataclass

from enum import IntEnum, auto
from struct import Struct


_T = TypeVar("_T")

Username = NewType("Username", str)


class ContentType(IntEnum):
    @staticmethod
    def from_name(name: str) -> ContentType:
        try:
            return ContentType[name.upper()]
        except KeyError:
            raise ValueError(f"Unknown content type: {name}")

    HELLO = auto()
    NO_HELLO = auto()
    LAST_SEEN = auto()


@dataclass_transform(kw_only_default=True, frozen_default=True)
def immutable(cls: type[_T]) -> type[_T]:
    return dataclass(frozen=True, slots=True, kw_only=True)(cls)


@dataclass_transform(kw_only_default=True, frozen_default=True)
def mutable(cls: type[_T]) -> type[_T]:
    return dataclass(frozen=False, slots=True, kw_only=True)(cls)


class Body(Protocol):
    """
    I think the mistake here was to include the whole message read from stream etc.

    A body should be able to encode/decode itself from a given set of bytes

    Consider: how does the db interface work here? Should I expect each Message handler
    to have a db instance to allow queries?
    """

    content_type: ClassVar[ContentType]
    STRUCT: ClassVar[Struct]

    @classmethod
    def decode(cls, data: bytes) -> Self: ...
    def encode(self) -> bytes: ...


Deserializer: TypeAlias = Callable[[bytes], Body]
