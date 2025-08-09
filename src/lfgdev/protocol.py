from __future__ import annotations
from asyncio import StreamReader, StreamWriter
from typing import Self, ClassVar, ByteString
from abc import ABC, abstractmethod
from lfgdev.types import immutable
from struct import Struct
import logging
from dataclasses import field
from typing import Any, Callable
from uuid import UUID, uuid4

from enum import IntEnum, auto
from typing import cast

from lfgdev.types import Username

LOG = logging.getLogger(__name__)


class MessageKind(IntEnum):
    @staticmethod
    def from_name(name: str) -> MessageKind | None:
        # Maybe a more elegant way to handle this, but
        # _member_map_ returns `Enum` not `MessageKind`
        return cast(MessageKind, MessageKind._member_map_.get(name))

    HEADER = auto()
    CLIENT_ERROR = auto()
    SERVER_ERROR = auto()

    HELLO = auto()
    NO_HELLO = auto()
    LAST_SEEN = auto()


def to_bytes(value: Any) -> int | bytes:
    match value:
        case UUID():
            return value.bytes
        case MessageKind() | int():
            return value
        case str():
            return value.encode("UTF-8")
        case _:
            raise ValueError(f"Unsupported type for encoding: {type(value)}")


class Message(ABC):
    # FIXME: This causes anything inheriting from Message to hide it's parameters
    # from the LSP
    #
    # I'm sure some type shenanigans fix this
    _STRUCT: ClassVar[Struct]
    kind: ClassVar[MessageKind]
    encoder: ClassVar[Callable[[Any], int | bytes]] = field(default=to_bytes)

    @classmethod
    @abstractmethod
    def decode(cls, bytes: ByteString) -> Self: ...

    @abstractmethod
    def encode(self) -> bytes: ...

    async def to_stream(self, stream: StreamWriter) -> None:
        stream.write(self.encode())

    @classmethod
    async def from_stream(cls, stream: StreamReader) -> Self:
        data = await stream.readexactly(cls._STRUCT.size)
        return cls.decode(data)


def serialize(message: type[Message]) -> type[Message]:
    if message.kind in Outgoing.serializers:
        raise ValueError(
            f"Serializer for MessageKind.{message.kind.name} already registered"
        )
    Outgoing.register_serializer(message=message)
    return message


def deserialize(message: type[Message]) -> type[Message]:
    if message.kind in Incoming.deserializers:
        raise ValueError(
            f"Deserializer for MessageKind.{message.kind.name} already registered"
        )
    Incoming.register_deserializer(message=message)
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
            # FIXME: this needs to know the contents, maybe Generics?
            await message().to_stream(stream)
            await stream.drain()
        else:
            raise NotImplementedError(
                f"No Serializer registered for: MessageKind.{self.header.kind.name}"
            )


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


@serialize
@deserialize
@immutable
class Header(Message):
    kind: ClassVar[MessageKind] = MessageKind.HEADER
    encoder: ClassVar[Callable[[Any], int | bytes]] = field(default=to_bytes)
    _STRUCT: ClassVar[Struct] = Struct(format="!16sx24sxI")

    identifier: UUID = field(default_factory=uuid4)
    sent_by: Username
    content_type: MessageKind

    def encode(self) -> bytes:
        message = Header._STRUCT.pack(
            Header.encoder(self.identifier),
            Header.encoder(self.sent_by),
            Header.encoder(self.content_type),
        )
        return message

    @classmethod
    def decode(cls, bytes: ByteString) -> Self:
        data = cls._STRUCT.unpack_from(bytes, offset=0)
        identifier = UUID(bytes=data[0])
        # Username has a max length of 24, strip the 0s
        username = Username(data[1].decode("UTF-8").strip("\x00"))
        kind = MessageKind(data[2])
        return cls(identifier=identifier, sent_by=username, content_type=kind)
