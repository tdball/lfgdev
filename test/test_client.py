import pytest

from lfgdev.client import Client
from lfgdev.types import Username
from lfgdev.messages import MessageKind, Hello, Header, Outgoing

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_server_client_message_passing(client: Client) -> None:
    # Maybe message should be body?
    message = Hello()
    header = Header(sent_by=Username("TestUser"), kind=message.kind)
    response = await client.send(request=Outgoing(header=header, message=message))
    assert response.header.sent_by == Username("SERVER")
    assert response.body.kind == MessageKind.NO_HELLO


async def test_client_metadata_persistence(client: Client) -> None:
    message = Hello()
    header = Header(sent_by=Username("TestUser"), kind=message.kind)
    await client.send(request=Outgoing(header=header, message=message))
    await client.send(request=Outgoing(header=header, message=message))
    assert client.metadata.messages_sent == 2
