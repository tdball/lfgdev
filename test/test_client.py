import pytest

from lfgdev.client import Client
from lfgdev.message import Header, Hello, Message
from lfgdev.types import ContentType, Username

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_server_client_message_passing(client: Client) -> None:
    header = Header(sender=Username("TestUser"), content_type=ContentType.HELLO)
    if response := await client.send(Message(header=header, body=Hello(content=None))):
        assert response.header.sender == Username("SERVER")
        assert response.header.content_type == ContentType.NO_HELLO
        assert response.body.content is None
    else:
        raise AssertionError("Expected response, none recieved")


async def test_client_metadata_persistence(client: Client) -> None:
    header = Header(sender=Username("TestUser"), content_type=ContentType.HELLO)
    body = Hello(content=None)
    message = Message(header=header, body=body)
    await client.send(message)
    await client.send(message)
    assert client.metadata.messages_sent == 2
