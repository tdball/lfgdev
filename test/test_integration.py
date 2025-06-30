from typing import Generator
from threading import Thread

import pytest

from lfgpy.client import Client
from lfgpy.message import MessageKind
from lfgpy.config import HOST
from lfgpy.server import RequestHandler, Server


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture(autouse=True)
def server() -> Generator[None, None, None]:
    with Server(HOST, RequestHandler, bind_and_activate=True) as server:
        Thread(target=server.serve_forever, daemon=True).start()
        yield


@pytest.mark.integration
def test_server_client_message_passing(client: Client) -> None:
    if response := client.say_hello():
        assert response.kind == MessageKind.NO_HELLO
