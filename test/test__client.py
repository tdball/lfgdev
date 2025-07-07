import json
import logging
import time
from threading import Thread
from typing import Generator

import pytest

from lfgpy import Client, serve
from lfgpy.types import MessageKind, Username


@pytest.fixture(autouse=True, scope="session")
def server() -> Generator[None, None, None]:
    thread = Thread(
        target=serve, kwargs={"host": "localhost", "port": 3117}, daemon=True
    )
    thread.start()
    yield


@pytest.fixture
def client() -> Client:
    return Client(address="localhost", port=3117, username=Username("TestUser"))


@pytest.mark.integration
def test_server_client_message_passing(client: Client) -> None:
    response = client.send_message(kind=MessageKind.HELLO)
    assert response.kind == MessageKind.COMPUTER_SAYS_NO


@pytest.mark.integration
def test_user_persistence(client: Client) -> None:
    client.send_message(MessageKind.LFG)
    response = client.send_message(MessageKind.LFG)
    assert response.sent_by == client.username
    assert client.metadata.messages_sent == 2


@pytest.mark.profiling
def test_throughput(client: Client) -> None:
    logger = logging.getLogger("lfgpy")
    logger.setLevel(logging.WARN)
    results: dict[int, float] = {}
    for attempt_count in [1, 10, 100, 1_000, 10_000, 100_000]:
        start = time.time()
        for _ in range(attempt_count):
            client.say_hello()
        results.update({attempt_count: (time.time() - start) * 1000})

    with open(f"profiling-results-{time.time()}.json", "w") as f:
        json.dump(results, f)
