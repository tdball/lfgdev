import logging
from dataclasses import replace
from typing import Callable, ClassVar

from lfgdev.message import LastSeen, Message, NoHello
from lfgdev.message.last_seen import LastSeenModel
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
    return Message(header=header, body=NoHello(model=None))


def handle_last_seen(db: Database, message: Message) -> Message:
    if user := db.find_by_username(message.header.sender):
        model = LastSeenModel(last_seen=user.last_seen)
        body = LastSeen(model=model)
        message = Message(header=message.header, body=body)
    return message


@immutable
class MessageHandler:
    _message_handlers: ClassVar[
        dict[ContentType, Callable[[Database, Message], Message]]
    ] = {
        ContentType.HELLO: handle_hello,
        ContentType.LAST_SEEN: handle_last_seen,
    }
    db: Database

    def route(self, message: Message) -> Message:
        if handler := self._message_handlers.get(message.header.content_type):
            reply = handler(self.db, message)
        else:
            LOG.warning(f"No handler for {message.body.content_type}")
            reply = message

        header = replace(reply.header, sender=Username("SERVER"))
        return replace(reply, header=header)
