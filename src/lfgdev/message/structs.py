from struct import Struct

from lfgdev.types import immutable


@immutable
class MessageStructs:
    UUID = Struct("!16s")
    USERNAME = Struct("!24s")
    ERROR = Struct("!100s")
