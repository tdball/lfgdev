import json
import logging
import time
import asyncio
import pytest

from lfgpy import Client
from lfgpy.types import MessageKind


@pytest.mark.profiling
@pytest.mark.asyncio
async def test_throughput(client: Client) -> None:
    # TODO: Capure commit id and append it to the filename
    logger = logging.getLogger("lfgpy")
    logger.setLevel(logging.WARN)
    results: dict[int, float] = {}
    # Something about 100k causes async to blow up, OOH, port exhaustion?
    # Also a huge spike in processing time at 50k
    # Looks to be something along those lines looking at strace.
    # TODO: Is this worth solving? This test is a bit ridiculous
    # I also think this tests e2e performance, and not server throughput
    for attempt_count in [1, 10, 100, 1_000, 10_000]:  # , 100_000]:
        start = time.time()
        async with asyncio.TaskGroup() as tg:
            for _ in range(attempt_count):
                tg.create_task(client.send(kind=MessageKind.HELLO))
                tg.create_task(client.send(kind=MessageKind.LFG))
                tg.create_task(client.send(kind=MessageKind.LFG))

        results.update({attempt_count: (time.time() - start) * 1000})

    with open(f".profiling/{time.time():.0f}.json", "w") as f:
        json.dump(results, f)
