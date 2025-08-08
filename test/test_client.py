import pytest

from lfgdev import Client
from lfgdev.types import MessageKind, Username

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_server_client_message_passing(client: Client) -> None:
    response = await client.send(kind=MessageKind.HELLO)
    assert response.sent_by == Username("SERVER")


async def test_user_persistence(client: Client) -> None:
    await client.send(MessageKind.LFG)
    response = await client.send(MessageKind.LFG)
    assert response.sent_by == client.username
    assert client.metadata.messages_sent == 2
