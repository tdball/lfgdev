import sqlite3
from os import PathLike
from pathlib import Path
from typing import Generator

import pytest

from lfgpy._db import Database
from lfgpy.types import Username


@pytest.fixture(scope="session")
def db() -> Generator[Database, None, None]:
    db_path = Path("/tmp/lfg-test.db")
    database = Database(path=db_path)
    database.create()
    yield database
    db_path.unlink()


def _get_player_count(path: PathLike, username: Username) -> int:
    with sqlite3.connect(path) as conn:
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
    assert _get_player_count(db.path, username) == 1
    db.remove_player(username)
    assert _get_player_count(db.path, username) == 0
