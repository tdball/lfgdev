from __future__ import annotations

import logging

from lfgpy.server.db import Database
from lfgpy.message import Message, MessageKind

logger = logging.getLogger(__name__)


def authenticate_message(message: Message) -> Message:
    # Should this raise an exception? Or just return None?
    # Probably None, no need to crash server threads
    logger.debug("Authenticating...? Go implement this at some point you donut")
    return message


def handle_message(message: Message, db: Database) -> Message:
    if db.get_player(message.sent_by) is None:
        db.add_player(message.sent_by)
    else:
        # TODO: Add an "update" method
        pass

    match message.kind:
        case MessageKind.HELLO:
            return message.with_kind(MessageKind.COMPUTER_SAYS_NO)
        case MessageKind.LFG:
            return message
        case _:
            logger.debug("No Route Defined")

    return message
