import pytest

from lfgpy.server.db import Database
from lfgpy.types import Username


@pytest.mark.integration
@pytest.mark.asyncio
async def test_save_player(db: Database) -> None:
    username = Username("TestCilantro")
    await db.save(username=username)
    if player := await db.find_by_username(username=username):
        assert player.username == username
    else:
        raise Exception("Player not found")
    await db.remove(username)
    assert await db.find_by_username(username=username) is None
