import sqlite3
from pathlib import Path
from typing import Generator

import pytest

from lfgpy._db import Database
from lfgpy.types import Username


@pytest.fixture(scope="session")
def db() -> Generator[Database, None, None]:
    database = Database(path=Path("/tmp/lfg-test.db"))
    database.create()
    yield database
    database.path.unlink()


def _get_player_count(db: Database, username: Username) -> int:
    with sqlite3.connect(db.path) as conn:
        cursor = conn.cursor()
        response = cursor.execute(
            "SELECT COUNT(*) FROM player WHERE username IS :username",
            {"username": username},
        )
        count = response.fetchall()
        return count[0][0]


@pytest.mark.integration
def test_save_player(db: Database) -> None:
    username = Username("TestCilantro")
    db.save_player(username=username)
    assert _get_player_count(db, username) == 1
    db.remove_player(username)
    assert _get_player_count(db, username) == 0
