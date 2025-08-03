from __future__ import annotations
from contextlib import contextmanager
import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
import asyncio
from typing import TYPE_CHECKING, Iterator
from lfgdev.types import Username
from concurrent.futures import ThreadPoolExecutor

if TYPE_CHECKING:
    from sqlite3 import _Parameters as Parameters
else:
    Parameters = object

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class Player:
    """Ideally this maps to the record in sqlite"""

    username: Username
    last_seen: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ConnectionPool:
    executor: ThreadPoolExecutor
    loop: asyncio.AbstractEventLoop

    @staticmethod
    def with_workers(n: int) -> ConnectionPool:
        loop = asyncio.new_event_loop()
        return ConnectionPool(executor=ThreadPoolExecutor(n), loop=loop)

    def close(self) -> None:
        self.loop.close()


@dataclass(frozen=True, slots=True, kw_only=True)
class Database:
    """Only intended to have a single table, lfg"""

    path: Path
    connection_pool: ConnectionPool

    @contextmanager
    @staticmethod
    def init(path: Path) -> Iterator[Database]:
        pool = ConnectionPool.with_workers(1)
        try:
            logger.debug(f"Initializing database at {path}")
            with sqlite3.connect(path) as conn:
                statement = """
                CREATE TABLE IF NOT EXISTS lfg (
                    username TEXT PRIMARY KEY UNIQUE,
                    last_seen INTEGER
                )
                """
                cursor = conn.cursor()
                cursor.execute(statement)
            yield Database(path=path, connection_pool=pool)
        finally:
            pool.close()

    # I think the following might belong on Player
    # Also I'm seeing a decorator pattern form here
    async def find_by_username(self, username: Username) -> Player | None:
        def command() -> Player | None:
            with sqlite3.connect(self.path) as conn:
                statement = "SELECT * from lfg where username is :username"
                cursor = conn.cursor()
                response = cursor.execute(statement, {"username": username})
                data = response.fetchone()
                try:
                    return Player(username=data[0], last_seen=data[1])
                except Exception:
                    # TODO: Handle this more gracefully?
                    return None

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.connection_pool.executor, command)

    async def save(self, username: Username) -> None:
        def command() -> None:
            with sqlite3.connect(self.path) as conn:
                statement = """
                    INSERT INTO lfg VALUES(
                        :username,
                        :last_seen
                    )
                """
                cursor = conn.cursor()
                cursor.execute(
                    statement, {"username": username, "last_seen": time.time()}
                )

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.connection_pool.executor, command)

    async def remove(self, username: Username) -> None:
        def command() -> None:
            with sqlite3.connect(self.path) as conn:
                statement = """
                    DELETE FROM lfg WHERE username IS :username
                """
                cursor = conn.cursor()
                cursor.execute(statement, {"username": username})

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.connection_pool.executor, command)
