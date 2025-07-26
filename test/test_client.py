import pytest

from lfgpy import Client
from lfgpy.types import MessageKind

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_server_client_message_passing(client: Client) -> None:
    response = await client.send(kind=MessageKind.HELLO)
    assert response.kind == MessageKind.COMPUTER_SAYS_NO


async def test_user_persistence(client: Client) -> None:
    await client.send(MessageKind.LFG)
    response = await client.send(MessageKind.LFG)
    assert response.sent_by == client.username
    assert client.metadata.messages_sent == 2
