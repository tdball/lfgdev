from lfgdev.message import Header
from lfgdev.types import ContentType, Username


def test_encode_decode() -> None:
    header = Header(content_type=ContentType.HELLO, sender=Username("TestUser"))
    bytes = header.encode()
    assert Header.decode(bytes) == header
