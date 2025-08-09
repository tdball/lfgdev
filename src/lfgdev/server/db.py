from __future__ import annotations
from contextlib import contextmanager
import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from lfgdev.types import Username

LOG = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class Player:
    """Ideally this maps to the record in sqlite"""

    username: Username
    last_seen: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Database:
    """Only intended to have a single table, lfg"""

    path: Path

    @contextmanager
    @staticmethod
    def init(path: Path) -> Iterator[Database]:
        connection = sqlite3.connect(path)
        LOG.debug(f"Initializing database at {path}")
        try:
            statement = """
            CREATE TABLE IF NOT EXISTS lfg (
                username TEXT PRIMARY KEY UNIQUE,
                last_seen INTEGER
            )
            """
            cursor = connection.cursor()
            cursor.execute(statement)
            yield Database(path=path)
        finally:
            connection.close()

    def find_by_username(self, username: Username) -> Player | None:
        statement = "SELECT * from lfg where username is :username"
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            response = cursor.execute(statement, {"username": username})
            data = response.fetchone()
        try:
            return Player(username=data[0], last_seen=data[1])
        except Exception:
            LOG.debug(f"Player {username} not found")
            return None

    def save(self, username: Username) -> None:
        statement = """
            INSERT INTO lfg VALUES(
                :username,
                :last_seen
            )
        """
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(statement, {"username": username, "last_seen": time.time()})

    def update(self, username: Username) -> None:
        last_seen = time.time()
        statement = """
            UPDATE lfg SET last_seen = :last_seen WHERE username = :username
        """
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(statement, {"username": username, "last_seen": last_seen})

    def remove(self, username: Username) -> None:
        statement = """
            DELETE FROM lfg WHERE username IS :username
        """
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(statement, {"username": username})
