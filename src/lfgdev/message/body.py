from __future__ import annotations

from abc import ABC, abstractmethod
from struct import Struct
from typing import Any, ClassVar, Self

from lfgdev.types import ContentType, immutable


@immutable
class Body(ABC):
    content_type: ClassVar[ContentType]
    STRUCT: ClassVar[Struct]
    model: Any

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes) -> Self: ...

    @abstractmethod
    def encode(self) -> bytes: ...
