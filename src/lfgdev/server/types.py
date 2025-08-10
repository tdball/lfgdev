from typing import Callable, NewType, TypeAlias

from lfgdev.messages import Message
from lfgdev.server.db import Database

Middleware: TypeAlias = Callable[[Database, Message], Message]
Order = NewType("Order", int)
