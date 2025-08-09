from dataclasses import FrozenInstanceError
import pytest
from lfgdev.types import immutable


def test_mutability():
    @immutable
    class Container:
        value: list[str]

    container = Container(value=["test"])
    with pytest.raises(FrozenInstanceError):
        container.value = ["should not work"]

    container.value.append("New")
    assert container.value == ["test", "New"]
