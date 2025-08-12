from typing import Callable, NewType, TypeAlias

from lfgdev.message import Message
from lfgdev.server.db import Database
from lfgdev.types import ContentType

Middleware: TypeAlias = Callable[[Database, Message], Message]
# Middleware probably doesn't describe this right
MessageRoute: TypeAlias = dict[ContentType, Middleware]

Order = NewType("Order", int)
