import pytest

from lfgdev.server.db import Database
from lfgdev.types import Username


@pytest.mark.integration
@pytest.mark.asyncio
async def test_save_player(db: Database) -> None:
    username = Username("TestCilantro")
    db.save(username=username)
    if player := db.find_by_username(username=username):
        assert player.username == username
    else:
        raise Exception("Player not found")
    db.remove(username)
    assert db.find_by_username(username=username) is None
