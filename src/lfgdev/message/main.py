from __future__ import annotations

from asyncio import StreamReader, StreamWriter

from lfgdev.message import decoder

# Exports
from lfgdev.message.body import Body
from lfgdev.message.header import Header
from lfgdev.message.hello import Hello as Hello
from lfgdev.message.hello import NoHello as NoHello
from lfgdev.message.last_seen import LastSeen as LastSeen
from lfgdev.types import ContentType, immutable


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
