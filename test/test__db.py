import pytest

from lfgpy._db import Database
from lfgpy.types import Username


@pytest.mark.integration
def test_save_player(db: Database) -> None:
    username = Username("TestCilantro")
    db.add_player(username=username)
    if player := db.get_player(username=username):
        assert player.username == username
    else:
        raise Exception("Player not found")
    db.remove_player(username)
    assert db.get_player(username=username) is None
