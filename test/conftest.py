from pathlib import Path
from threading import Thread
from typing import Generator
import pytest
import time
import asyncio
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
    def test_server():
        asyncio.run(serve(host="localhost", port=3117, db=db))

    thread = Thread(target=test_server, daemon=True)
    thread.start()
    # TODO: This is some duct tape to wait for the server to come up
    time.sleep(0.5)
    yield


@pytest.fixture
def client(server: None) -> Client:
    return Client(address="localhost", port=3117, username=Username("TestUser"))
