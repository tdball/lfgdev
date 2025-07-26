import pytest

from lfgpy import Client
from lfgpy.types import MessageKind


@pytest.mark.integration
def test_server_client_message_passing(client: Client) -> None:
    response = client.send(kind=MessageKind.HELLO)
    assert response.kind == MessageKind.COMPUTER_SAYS_NO


@pytest.mark.integration
def test_user_persistence(client: Client) -> None:
    client.send(MessageKind.LFG)
    response = client.send(MessageKind.LFG)
    assert response.sent_by == client.username
    assert client.metadata.messages_sent == 2
