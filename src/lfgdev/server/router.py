from __future__ import annotations

import logging
from lfgdev.server.db import Database
from lfgdev.message import Message, MessageKind

logger = logging.getLogger(__name__)


def authenticate_message(message: Message) -> Message:
    # TODO: This
    return message


def handle_message(message: Message, db: Database) -> Message:
    if db.find_by_username(message.sent_by) is None:
        db.save(message.sent_by)
    else:
        db.update(message.sent_by)

    match message.kind:
        case MessageKind.HELLO:
            return message.reply(MessageKind.COMPUTER_SAYS_NO)
        case MessageKind.LFG:
            return message
        case _:
            logger.debug("No Route Defined")

    return message
