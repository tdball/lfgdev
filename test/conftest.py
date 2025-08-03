from pathlib import Path
from threading import Thread
from typing import Generator
import pytest
import time
import asyncio
from lfgdev import Client, serve
from lfgdev.server.db import Database
from lfgdev.types import Username


@pytest.fixture(scope="session")
def db() -> Generator[Database, None, None]:
    with Database.init(path=Path("/tmp/lfg-test.db")) as db:
        yield db
        db.path.unlink()


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
