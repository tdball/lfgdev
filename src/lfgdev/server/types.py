from lfgdev.server.db import Database
from typing import Callable, TypeAlias, NewType
from lfgdev.messages import Message

Middleware: TypeAlias = Callable[[Database, Message], Message]
Order = NewType("Order", int)
