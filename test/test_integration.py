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


@pytest.fixture
def server() -> Generator[Server, None, None]:
    with Server(HOST, RequestHandler, bind_and_activate=True) as server:
        yield server


@pytest.mark.integration
def test_server_client_message_passing(server: Server, client: Client) -> None:
    server_thread = Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    if response := client.say_hello():
        assert response.kind == MessageKind.NO_HELLO
