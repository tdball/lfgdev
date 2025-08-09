from asyncio import StreamReader, StreamWriter
from typing import Self, Protocol, ClassVar
from lfgdev.messages.kind import MessageKind


class Serializable(Protocol):
    async def to_stream(self, stream: StreamWriter) -> None: ...
    def encode(self) -> bytes: ...


class Deserializable(Protocol):
    @classmethod
    async def from_stream(cls, stream: StreamReader) -> Self: ...
    @classmethod
    def decode(cls, data: bytes) -> Self: ...


class Message(Serializable, Deserializable, Protocol):
    kind: ClassVar[MessageKind]
