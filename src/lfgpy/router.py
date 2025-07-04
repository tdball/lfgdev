from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import ClassVar

from lfgpy.message import HelloValue, Message, MessageKind

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class Router:
    # Do I need this if handle has the routes built in?
    _KIND_TO_VALUE: ClassVar[dict[MessageKind, type[IntEnum]]] = {
        MessageKind.HELLO: HelloValue
    }

    def authenticate_message(self, message) -> Message:
        # Should this raise an exception? Or just return None?
        logger.debug("Authenticating...? Go implement this at some point you donut")
        return message

    def handle_message(self, message) -> Message:
        match message.kind:
            case MessageKind.HELLO:
                logger.debug("HELLO Message")
                return message.with_value(HelloValue.COMPUTER_SAYS_NO)
            case MessageKind.LFG:
                logger.debug("LFG Message")
            case _:
                logger.debug("No Route Defined")

        return message
