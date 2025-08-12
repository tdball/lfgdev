import asyncio
import json
import logging
import time

import pytest

from lfgdev.client import Client
from lfgdev.message import Header, Hello, Message
from lfgdev.types import ContentType, Username


@pytest.mark.profiling
@pytest.mark.asyncio
async def test_throughput(client: Client) -> None:
    # TODO: Capure commit id and append it to the filename
    logger = logging.getLogger("lfgdev")
    logger.setLevel(logging.WARN)
    results: dict[int, float] = {}
    header = Header(sender=Username("Profiling"), content_type=ContentType.HELLO)
    outgoing = Message(header=header, body=Hello(content=None))
    for attempt_count in [1, 10, 100, 1_000]:
        start = time.time()
        async with asyncio.TaskGroup() as tg:
            # I think as long as the client makes it's own socket, this doesn't scale up
            for _ in range(attempt_count):
                tg.create_task(client.send(outgoing))

        results.update({attempt_count: (time.time() - start) * 1000})

    with open(f".profiling/{time.time():.0f}.json", "w") as f:
        json.dump(results, f)
