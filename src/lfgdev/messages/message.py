from __future__ import annotations

from asyncio import StreamReader, StreamWriter
from dataclasses import field
from struct import Struct
from typing import ClassVar
from uuid import UUID, uuid4

from lfgdev.messages import decoder
from lfgdev.types import Body, ContentType, Username, immutable


@immutable
class Header:
    STRUCT: ClassVar[Struct] = Struct("!16sx24sxI")
    identifier: UUID = field(default_factory=uuid4)
    content_type: ContentType
    sender: Username

    @staticmethod
    def decode(data: bytes) -> Header:
        identifier, sender, content_type = Header.STRUCT.unpack(data)

        sender = sender.decode("UTF-8").strip("\x00")
        sender = Username(sender)

        return Header(
            identifier=UUID(bytes=identifier),
            sender=Username(sender),
            content_type=ContentType(content_type),
        )

    def encode(self) -> bytes:
        return Header.STRUCT.pack(
            self.identifier.bytes,
            self.sender.encode("UTF-8"),
            self.content_type,
        )


@immutable
class Message:
    header: Header
    body: Body

    @staticmethod
    async def parse_header(reader: StreamReader) -> Header:
        header_data = await reader.readexactly(Header.STRUCT.size)
        header = Header.decode(header_data)
        return header

    @staticmethod
    async def parse_body(reader: StreamReader, content_type: ContentType) -> Body:
        """
        Feels like the db access might happen here?
        Also how to keep this from just growing... it's gonna be a long one I think
        Maybe this should only handle deserializing data into particular message types
        and later route logic based on the message itself
        """

        return await decoder.decode(content_type, reader=reader)

    async def send(self, stream: StreamWriter) -> None:
        stream.write(self.header.encode())
        if self.body is not None:
            stream.write(self.body.encode())
        await stream.drain()

    @staticmethod
    async def receive(stream: StreamReader) -> Message:
        header = await Message.parse_header(stream)
        body = await Message.parse_body(stream, header.content_type)
        return Message(header=header, body=body)
