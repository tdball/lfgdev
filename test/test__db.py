from pathlib import Path
from typing import Generator

import pytest

from lfgpy._db import Database
from lfgpy.types import Username


@pytest.fixture(scope="session")
def db() -> Generator[Database, None, None]:
    database = Database(path=Path("/tmp/lfg-test.db"))
    database.setup()
    yield database
    database.path.unlink()


@pytest.mark.integration
def test_save_player(db: Database) -> None:
    username = Username("TestCilantro")
    db.add_player(username=username)
    if player := db.get_player(username=username):
        assert player.username == username
    else:
        raise Exception("Player not found")
    db.remove_player(username)
    assert db.get_player(username=username) is None
