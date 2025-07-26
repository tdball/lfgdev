import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from lfgpy.types import Username

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class Player:
    """Ideally this maps to the record in sqlite"""

    username: Username
    last_seen: int


@dataclass(frozen=True, slots=True, kw_only=True)
class Database:
    """Only intended to have a single table, lfg"""

    # TODO: Enable connection pool for async writes and reads

    path: Path

    def init(self) -> None:
        logger.debug(f"Initializing database at {self.path}")
        with sqlite3.connect(self.path) as conn:
            statement = """
            CREATE TABLE IF NOT EXISTS lfg (
                username TEXT PRIMARY KEY UNIQUE,
                last_seen INTEGER
            )
            """
            cursor = conn.cursor()
            cursor.execute(statement)

    def add_player(self, username: Username) -> None:
        with sqlite3.connect(self.path) as conn:
            statement = """
                INSERT INTO lfg VALUES(
                    :username,
                    :last_seen
                )
            """
            cursor = conn.cursor()
            cursor.execute(statement, {"username": username, "last_seen": time.time()})

    def get_player(self, username: Username) -> Player | None:
        with sqlite3.connect(self.path) as conn:
            statement = "SELECT * from lfg where username is :username"
            cursor = conn.cursor()
            response = cursor.execute(statement, {"username": username})
            data = response.fetchall()
            if len(data) == 1:
                data = data[0]
                return Player(username=data[0], last_seen=data[1])
            logger.debug(f"Player query returned {len(data)} results: {data}")
            return None

    def remove_player(self, username: Username) -> None:
        with sqlite3.connect(self.path) as conn:
            statement = """
                DELETE FROM lfg WHERE username IS :username
            """
            cursor = conn.cursor()
            cursor.execute(statement, {"username": username})
