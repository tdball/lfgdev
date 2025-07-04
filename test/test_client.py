import json
import logging
import time
from threading import Thread
from typing import Generator
from uuid import uuid4

import pytest

from lfgpy.client import Client
from lfgpy.config import HOST
from lfgpy.message import MessageKind, MessageValue
from lfgpy.server import RequestHandler, Server


@pytest.fixture
def client() -> Client:
    return Client(user_id=uuid4())


@pytest.fixture(autouse=True)
def server() -> Generator[None, None, None]:
    with Server(HOST, RequestHandler, bind_and_activate=True) as server:
        # I think this has a bug, repeated pytest invocations cause failures
        # Maybe a bug with cleanup after shutting down?
        #
        # ConnectionResetError: [Errno 104] Connection reset by peer
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        yield


@pytest.mark.integration
def test_server_client_message_passing(client: Client) -> None:
    response = client.say_hello()
    assert response.identifier == client.sent_messages[0]
    assert response.kind == MessageKind.HELLO
    assert response.value == MessageValue.COMPUTER_SAYS_NO


@pytest.mark.integration
def test_user_persistence(client: Client) -> None:
    response = client.login()
    response = client.login()
    assert response.user_id == client.user_id
    assert len(client.sent_messages) == 2


@pytest.mark.profiling
def test_throughput(client: Client) -> None:
    server_logger = logging.getLogger("lfgpy.server")
    client_logger = logging.getLogger("lfgpy.client")
    server_logger.setLevel(logging.WARN)
    client_logger.setLevel(logging.WARN)
    results: dict[int, float] = {}
    for attempt_count in [1, 10, 100, 1_000, 10_000, 100_000]:
        start = time.time()
        for _ in range(attempt_count):
            client.say_hello()
        results.update({attempt_count: (time.time() - start) * 1000})

    with open(f"profiling-results-{time.time()}.json", "w") as f:
        json.dump(results, f)
