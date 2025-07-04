from uuid import uuid4

import pytest

from lfgpy.message import Message, MessageKind, MessageValue


@pytest.fixture
def message() -> Message:
    return Message(kind=MessageKind.HELLO, user_id=uuid4(), value=MessageValue.UNSET)


def test_conversion(message: Message) -> None:
    bytes = message.encode()
    assert Message.decode(bytes) == message
