from typing import NewType, TypeVar
from typing import dataclass_transform
from dataclasses import dataclass

_T = TypeVar("_T")

Username = NewType("Username", str)


@dataclass_transform(kw_only_default=True, frozen_default=True)
def immutable(cls: type[_T]) -> type[_T]:
    return dataclass(frozen=True, slots=True, kw_only=True)(cls)


@dataclass_transform(kw_only_default=True, frozen_default=True)
def mutable(cls: type[_T]) -> type[_T]:
    return dataclass(frozen=False, slots=True, kw_only=True)(cls)
