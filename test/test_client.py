import pytest

from lfgdev import Client
from lfgdev.types import Username
from lfgdev.messages import MessageKind, Hello

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_server_client_message_passing(client: Client) -> None:
    response = await client.send(message=Hello())
    assert response.header.sent_by == Username("SERVER")
    assert response.body.kind == MessageKind.NO_HELLO


async def test_client_metadata_persistence(client: Client) -> None:
    await client.send(message=Hello())
    await client.send(message=Hello())
    assert client.metadata.messages_sent == 2
