import logging
from dataclasses import replace
from typing import Callable, ClassVar

from lfgdev.messages import LastSeen, Message, NoHello
from lfgdev.server.db import Database
from lfgdev.types import ContentType, Username, immutable

LOG = logging.getLogger(__name__)

# Just give handling Hello a shot
# When a HELLO is received, send back a NO_HELLO


def handle_hello(db: Database, message: Message) -> Message:
    # Sounds like ContentType should really
    # only be at the beginning of a body, so this isn't duplicated
    # use something like readexactly(CONTENT_TYPE_LENGTH) and then another readexactly at
    # offset=content length -> end
    # for now just deal with it

    header = replace(message.header, content_type=ContentType.NO_HELLO)
    return Message(header=header, body=NoHello())


def handle_last_seen(db: Database, message: Message) -> Message:
    # Should validation and error happen at the beginning?
    if user := db.find_by_username(message.header.sender):
        message = Message(
            header=message.header,
            body=LastSeen(
                # Unsure how to resolve this at the moment
                last_seen=user.last_seen,
            ),
        )

    return message


# This is starting to feel a little like the request_handler
# maybe this is more a "body handler"? And should we be passing in
# the db? It can be unused... although I'm not sure what messages would
# not use it outside of the hello one
@immutable
class Router:
    _routes: ClassVar[dict[ContentType, Callable[[Database, Message], Message]]] = {
        ContentType.HELLO: handle_hello,
        ContentType.LAST_SEEN: handle_last_seen,
    }
    db: Database

    def route(self, message: Message) -> Message:
        # Ideally this takes a message, inspects its content type and
        # routes to the appropriate handler.
        #
        # Maybe the same decorator pattern works here?
        # or that's overkill, just throw a dict on the class itself
        if handler := self._routes.get(message.header.content_type):
            message = handler(self.db, message)

        # Maybe this isn't so ideal
        header = replace(message.header, sender=Username("SERVER"))
        message = replace(message, header=header)

        LOG.warning(f"No handler for {message.body.content_type}")
        return message
