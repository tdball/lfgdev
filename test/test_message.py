import pytest

from lfgpy.message import Message, MessageKind, MessageValue


@pytest.fixture
def message() -> Message:
    return Message(kind=MessageKind.HELLO, value=MessageValue.UNSET)


def test_conversion(message: Message) -> None:
    bytes = message.encode()
    assert Message.decode(bytes) == message
