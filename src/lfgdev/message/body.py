from __future__ import annotations

from abc import ABC, abstractmethod
from struct import Struct
from typing import Any, ClassVar, Self

from lfgdev.types import immutable


@immutable
class Body(ABC):
    STRUCT: ClassVar[Struct]
    content: Any

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes) -> Self: ...

    @abstractmethod
    def encode(self) -> bytes: ...
