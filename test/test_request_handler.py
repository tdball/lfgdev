from asyncio import StreamReader, StreamWriter
from unittest.mock import AsyncMock, Mock

import pytest

from lfgdev.message import Header, Hello, Message
from lfgdev.server.db import Database
from lfgdev.server.request_handler import RequestHandler
from lfgdev.types import ContentType, Username


@pytest.fixture
def header() -> Header:
    return Header(
        sender=Username("TestUser"),
        content_type=ContentType.HELLO,
    )


@pytest.fixture
def message(header: Header) -> Message:
    return Message(header=header, body=Hello(model=None))


@pytest.fixture
def reader(message: Message) -> StreamReader:
    readexactly = AsyncMock(
        side_effect=[message.header.encode(), message.body.encode()]
    )
    return Mock(spec=StreamReader, readexactly=readexactly)


@pytest.fixture
def writer(message: Message) -> StreamWriter:
    return Mock(spec=StreamWriter)


@pytest.mark.asyncio
async def test_request_handler(
    db: Database, message: Message, reader: StreamReader, writer: StreamWriter
):
    request_handler = RequestHandler(db=db)
    await request_handler.handle(reader=reader, writer=writer)
