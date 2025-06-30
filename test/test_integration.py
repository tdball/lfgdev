import logging
import time
from threading import Thread
from typing import Generator

import pytest
import json

from lfgpy.client import Client
from lfgpy.config import HOST
from lfgpy.message import MessageKind
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


@pytest.mark.profiling
def test_throughput() -> None:
    server_logger = logging.getLogger("lfgpy.server")
    client_logger = logging.getLogger("lfgpy.client")
    server_logger.setLevel(logging.WARN)
    client_logger.setLevel(logging.WARN)
    results: dict[int, float] = {}
    for attempt_count in [1, 10, 100, 1_000, 10_000, 100_000]:
        start = time.time()
        for _ in range(attempt_count):
            client = Client()
            client.say_hello()
        results.update({attempt_count: (time.time() - start) * 1000})

    with open(f"profiling-results-{time.time()}.json", "w") as f:
        json.dump(results, f)
