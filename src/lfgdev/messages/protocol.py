from __future__ import annotations
from asyncio import StreamReader, StreamWriter
from typing import Self, Protocol, ClassVar
from lfgdev.messages.kind import MessageKind
from lfgdev.messages.header import Header
from dataclasses import dataclass


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


def deserialize(message: type[Message]) -> type[Message]:
    if message.kind in Response.deserializers:
        raise ValueError(
            f"Deserializer for MessageKind.{message.kind.name} already registered"
        )
    Response.register_deserializer(kind=message.kind, message=message)
    return message


@dataclass(frozen=True, slots=True, repr=False)
class Response:
    header: Header
    body: Message

    # request_header: Header
    # request: Message
    # response_header: Header
    # response: Message

    # should this have a param for body decoders?
    # since this logic is really shared between client and server
    # there's bound to be some duplication
    deserializers: ClassVar[dict[MessageKind, type[Message]]] = dict()

    @classmethod
    def register_deserializer(cls, kind: MessageKind, message: type[Message]) -> None:
        # Scrappy logic, store a map of decoders of message kind their decoder
        cls.deserializers.update({kind: message})

    @staticmethod
    async def deserialize(header: Header, stream: StreamReader) -> Response:
        # Should ideally return anything matching the Message protocol based on the header
        if deserializer := Response.deserializers.get(header.kind):
            # Should we swap out the header here? Since it's the response, maybe
            # the whole SERVER sent_by thing is weird. Maybe both the request and response
            # headers should be stored
            return Response(header=header, body=await deserializer.from_stream(stream))
        else:
            raise NotImplementedError(
                f"No Deserializer registered for: MessageKind.{header.kind.name}"
            )
