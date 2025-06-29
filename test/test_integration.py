from multiprocessing import Process
from typing import Generator

import pytest

from lfgpy.client import Client
from lfgpy.config import HOST
from lfgpy.message import Message, MessageKind
from lfgpy.server import RequestHandler, Server


@pytest.fixture
def client() -> Generator[Client, None, None]:
    with Client() as client:
        yield client


@pytest.fixture
def server() -> Generator[Server, None, None]:
    with Server(HOST, RequestHandler, bind_and_activate=True) as server:
        yield server


@pytest.mark.integration
def test_server_client_message_passing(server: Server, client: Client) -> None:
    message = Message(kind=MessageKind.HELLO)
    client_process = Process(target=client.send, args=(message,))
    server_process = Process(target=server.serve_forever)
    # How do I get events out?
    server_process.start()
    client_process.start()

    client_process.kill()
    server_process.kill()
