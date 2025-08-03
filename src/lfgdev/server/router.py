from __future__ import annotations

import logging

from lfgdev.server.db import Database
from lfgdev.message import Message, MessageKind

logger = logging.getLogger(__name__)


async def authenticate_message(message: Message) -> Message:
    # Should this raise an exception? Or just return None?
    # Probably None, no need to crash server threads
    logger.debug("Authenticating...? Go implement this at some point you donut")
    return message


async def handle_message(message: Message, db: Database) -> Message:
    if await db.find_by_username(message.sent_by) is None:
        await db.save(message.sent_by)
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
