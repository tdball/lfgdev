from __future__ import annotations
from asyncio import StreamReader, StreamWriter
from typing import Self, ClassVar, ByteString, Protocol, runtime_checkable
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
        return cast(MessageKind, MessageKind._member_map_.get(name))

    HEADER = auto()
    CLIENT_ERROR = auto()
    SERVER_ERROR = auto()

    HELLO = auto()
    NO_HELLO = auto()
    LAST_SEEN = auto()


@runtime_checkable
class MessageProtocol(Protocol):
    _STRUCT: ClassVar[Struct]
    kind: ClassVar[MessageKind]
    encoder: ClassVar[Callable[[Any], int | bytes]]

    @classmethod
    def decode(cls, bytes: ByteString) -> Self: ...
    def encode(self) -> bytes: ...
    async def to_stream(self, stream: StreamWriter) -> None: ...
    @classmethod
    async def from_stream(cls, stream: StreamReader) -> Self: ...


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


def streamable(message: type[MessageProtocol]) -> type[MessageProtocol]:
    if message.kind in Incoming.deserializers:
        raise ValueError(
            f"Deserializer for MessageKind.{message.kind.name} already registered"
        )
    Incoming.register_deserializer(message=message)
    return message


@immutable
class Outgoing:
    header: Header
    message: MessageProtocol

    async def send(self, stream: StreamWriter) -> None:
        LOG.debug(f"Sending message: {self.message.kind.name}")
        await self.header.to_stream(stream)
        await self.message.to_stream(stream)
        await stream.drain()


@immutable
class Incoming:
    header: Header
    message: MessageProtocol

    deserializers: ClassVar[dict[MessageKind, type[MessageProtocol]]] = dict()

    @classmethod
    def register_deserializer(cls, message: type[MessageProtocol]) -> None:
        cls.deserializers.update({message.kind: message})

    @staticmethod
    async def get(stream: StreamReader) -> Incoming:
        LOG.debug("Receiving message")
        header = await Header.from_stream(stream=stream)
        LOG.debug(f"Message kind: {header.content_type.name}")
        if deserializer := Incoming.deserializers.get(header.content_type):
            message = Incoming(
                header=header, message=await deserializer.from_stream(stream)
            )
            LOG.debug(f"Received message: {message}")
            return message
        else:
            raise NotImplementedError(
                f"No Deserializer registered for: MessageKind.{header.kind.name}"
            )


@streamable
@immutable
class Header(Message):
    _STRUCT: ClassVar[Struct] = Struct(format="!16sx24sxI")
    kind: ClassVar[MessageKind] = MessageKind.HEADER
    encoder: ClassVar[Callable[[Any], int | bytes]] = field(default=to_bytes)

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
