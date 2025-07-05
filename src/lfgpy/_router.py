from __future__ import annotations

import logging
from pathlib import Path

from lfgpy._db import Database
from lfgpy._message import Message, MessageKind

logger = logging.getLogger(__name__)


def authenticate_message(message: Message) -> Message:
    # Should this raise an exception? Or just return None?
    # Probably None, no need to crash server threads
    logger.debug("Authenticating...? Go implement this at some point you donut")
    return message


def handle_message(message: Message) -> Message:
    # Definitely not the place to do this
    db = Database(path=Path("/tmp/lfg-test.db"))
    db.setup()

    db.add_player(message.sent_by)
    match message.kind:
        case MessageKind.HELLO:
            logger.debug("HELLO Message")
            return message.with_kind(MessageKind.COMPUTER_SAYS_NO)
        case MessageKind.LFG:
            logger.debug("LFG Message")
        case _:
            logger.debug("No Route Defined")

    return message
