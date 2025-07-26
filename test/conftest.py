from pathlib import Path
from threading import Thread
from typing import Generator
import pytest

from lfgpy import Client, serve
from lfgpy.server.db import Database
from lfgpy.types import Username


@pytest.fixture(scope="session")
def db() -> Generator[Database, None, None]:
    database = Database(path=Path("/tmp/lfg-test.db"))
    database.init()
    yield database
    database.path.unlink()


@pytest.fixture(autouse=True, scope="session")
def server(db: Database) -> Generator[None, None, None]:
    thread = Thread(
        target=serve, kwargs={"host": "localhost", "port": 3117, "db": db}, daemon=True
    )
    thread.start()
    yield


@pytest.fixture
def client(server: None) -> Client:
    return Client(address="localhost", port=3117, username=Username("TestUser"))
