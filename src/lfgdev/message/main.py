from __future__ import annotations

from asyncio import StreamReader, StreamWriter

from lfgdev.message.body import Body
from lfgdev.message.decoder import decode
from lfgdev.message.header import Header
from lfgdev.types import immutable


@immutable
class Message:
    header: Header
    body: Body

    @staticmethod
    async def parse_header(reader: StreamReader) -> Header:
        header_data = await reader.readexactly(Header.STRUCT.size)
        header = Header.decode(header_data)
        return header

    async def send(self, stream: StreamWriter) -> None:
        stream.write(self.header.encode())
        if self.body is not None:
            stream.write(self.body.encode())
        await stream.drain()

    @staticmethod
    async def receive(stream: StreamReader) -> Message:
        header = await Message.parse_header(stream)
        body = await decode(header.content_type, reader=stream)
        return Message(header=header, body=body)
