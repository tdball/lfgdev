import json
import logging
import time

import pytest

from lfgpy import Client
from lfgpy.types import MessageKind


@pytest.mark.profiling
def test_throughput(client: Client) -> None:
    logger = logging.getLogger("lfgpy")
    logger.setLevel(logging.WARN)
    results: dict[int, float] = {}
    for attempt_count in [1, 10, 100, 1_000, 10_000, 100_000]:
        start = time.time()
        for _ in range(attempt_count):
            client.send_message(kind=MessageKind.HELLO)
        results.update({attempt_count: (time.time() - start) * 1000})

    with open(f"profiling-results-{time.time()}.json", "w") as f:
        json.dump(results, f)
