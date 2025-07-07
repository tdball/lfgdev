from pathlib import Path
from threading import Thread
from typing import Generator

import pytest

from lfgpy import Client, serve
from lfgpy._db import Database
from lfgpy.types import Username


@pytest.fixture(autouse=True, scope="module")
def server() -> Generator[None, None, None]:
    thread = Thread(
        target=serve, kwargs={"host": "localhost", "port": 3117}, daemon=True
    )
    thread.start()
    yield


@pytest.fixture
def client() -> Client:
    return Client(address="localhost", port=3117, username=Username("TestUser"))


@pytest.fixture(scope="session")
def db() -> Generator[Database, None, None]:
    database = Database(path=Path("/tmp/lfg-test.db"))
    database.setup()
    yield database
    database.path.unlink()
