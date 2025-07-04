from __future__ import annotations

import logging

from lfgpy.message import HelloValue, Message, MessageKind

logger = logging.getLogger(__name__)


def authenticate_message(message) -> Message:
    # Should this raise an exception? Or just return None?
    logger.debug("Authenticating...? Go implement this at some point you donut")
    return message


def handle_message(message) -> Message:
    match message.kind:
        case MessageKind.HELLO:
            logger.debug("HELLO Message")
            return message.with_value(HelloValue.COMPUTER_SAYS_NO)
        case MessageKind.LFG:
            logger.debug("LFG Message")
        case _:
            logger.debug("No Route Defined")

    return message
