import logging
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from lfgpy.types import Username

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class Database:
    path: Path

    def create(self) -> None:
        logger.debug("Creating player table")
        with sqlite3.connect(self.path) as conn:
            statement = """
            CREATE TABLE IF NOT EXISTS player (
                username TEXT PRIMARY KEY UNIQUE
            )
            """
            cursor = conn.cursor()
            cursor.execute(statement)

    def save_player(self, username: Username) -> None:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO player VALUES(:username)", {"username": username}
            )

    def remove_player(self, username: Username) -> None:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM player WHERE username IS :username", {"username": username}
            )
