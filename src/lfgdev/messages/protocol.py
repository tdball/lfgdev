from __future__ import annotations
from asyncio import StreamReader, StreamWriter
from typing import Self, Protocol, ClassVar
from lfgdev.messages.kind import MessageKind
from lfgdev.messages.header import Header
from lfgdev.types import immutable
import logging

LOG = logging.getLogger(__name__)


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


def serialize(message: type[Message]) -> type[Message]:
    if message.kind in Outgoing.serializers:
        raise ValueError(
            f"Serializer for MessageKind.{message.kind.name} already registered"
        )
    Outgoing.register_serializer(message=message)
    return message


@immutable
class Outgoing:
    header: Header
    message: Message

    serializers: ClassVar[dict[MessageKind, type[Message]]] = dict()

    @classmethod
    def register_serializer(cls, message: type[Message]) -> None:
        cls.serializers.update({message.kind: message})

    async def send(self, stream: StreamWriter) -> None:
        if message := self.serializers.get(self.header.kind):
            LOG.debug(f"Sending message: {self.header.kind.name}")
            await self.header.to_stream(stream)
            await message().to_stream(stream)
            await stream.drain()
        else:
            raise NotImplementedError(
                f"No Serializer registered for: MessageKind.{self.header.kind.name}"
            )


def deserialize(message: type[Message]) -> type[Message]:
    if message.kind in Incoming.deserializers:
        raise ValueError(
            f"Deserializer for MessageKind.{message.kind.name} already registered"
        )
    Incoming.register_deserializer(message=message)
    return message


@immutable
class Incoming:
    header: Header
    body: Message

    deserializers: ClassVar[dict[MessageKind, type[Message]]] = dict()

    @classmethod
    def register_deserializer(cls, message: type[Message]) -> None:
        cls.deserializers.update({message.kind: message})

    @staticmethod
    async def get(stream: StreamReader) -> Incoming:
        LOG.debug("Receiving message")
        header = await Header.from_stream(stream=stream)
        LOG.debug(f"Message kind: {header.kind.name}")
        if deserializer := Incoming.deserializers.get(header.kind):
            message = Incoming(
                header=header, body=await deserializer.from_stream(stream)
            )
            LOG.debug(f"Received message: {message}")
            return message
        else:
            raise NotImplementedError(
                f"No Deserializer registered for: MessageKind.{header.kind.name}"
            )
