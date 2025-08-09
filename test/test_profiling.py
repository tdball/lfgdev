import json
import logging
import time
import asyncio
import pytest

from lfgdev import Client
from lfgdev.messages import Hello


@pytest.mark.profiling
@pytest.mark.asyncio
async def test_throughput(client: Client) -> None:
    # TODO: Capure commit id and append it to the filename
    logger = logging.getLogger("lfgdev")
    logger.setLevel(logging.WARN)
    results: dict[int, float] = {}
    message = Hello()
    for attempt_count in [1, 10, 100, 1_000]:
        start = time.time()
        async with asyncio.TaskGroup() as tg:
            # I think as long as the client makes it's own socket, this doesn't scale up
            for _ in range(attempt_count):
                tg.create_task(client.send(message))

        results.update({attempt_count: (time.time() - start) * 1000})

    with open(f".profiling/{time.time():.0f}.json", "w") as f:
        json.dump(results, f)
