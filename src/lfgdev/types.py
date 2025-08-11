from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, auto
from typing import (
    NewType,
    TypeVar,
    dataclass_transform,
)

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


@dataclass_transform(kw_only_default=True, frozen_default=False)
def mutable(cls: type[_T]) -> type[_T]:
    return dataclass(frozen=False, slots=True, kw_only=True)(cls)
