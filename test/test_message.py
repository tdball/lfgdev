from lfgdev.messages import MessageKind, Header
from lfgdev.types import Username


def test_encode_decode() -> None:
    header = Header(kind=MessageKind.HELLO, sent_by=Username("TestUser"))
    bytes = header.encode()
    assert Header.decode(bytes) == header
