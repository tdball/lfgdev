import pytest

from lfgdev import Client
from lfgdev.types import Username
from lfgdev.messages import MessageKind, Hello

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_server_client_message_passing(client: Client) -> None:
    # TODO I think Response should encapsulate header + message
    # so we don't have to parse a tuple
    header, response = await client.send(message=Hello())
    assert header.sent_by == Username("SERVER")
    assert response.kind == MessageKind.NO_HELLO


async def test_user_persistence(client: Client) -> None:
    await client.send(message=Hello())
    header, response = await client.send(message=Hello())
    assert client.metadata.messages_sent == 2
