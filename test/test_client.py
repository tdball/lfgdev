import pytest

from lfgdev.client import Client
from lfgdev.messages import Header, Hello, Message
from lfgdev.types import ContentType, Username

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_server_client_message_passing(client: Client) -> None:
    # Maybe message should be body?
    header = Header(sender=Username("TestUser"), content_type=ContentType.HELLO)
    if response := await client.send(Message(header=header, body=Hello())):
        assert response.header.sender == Username("SERVER")
        assert response.body is not None
        assert response.body.content_type == ContentType.NO_HELLO
    else:
        raise AssertionError("Expected response, none recieved")


async def test_client_metadata_persistence(client: Client) -> None:
    header = Header(sender=Username("TestUser"), content_type=ContentType.HELLO)
    await client.send(Message(header=header, body=Hello()))
    await client.send(Message(header=header, body=Hello()))
    assert client.metadata.messages_sent == 2
