from __future__ import annotations

import logging
from dataclasses import dataclass, field

from lfgpy.message import Message, MessageHandler, MessageKind

logger = logging.getLogger(__name__)


def say_hello(message: Message) -> Message:
    return Message(kind=MessageKind.NO_HELLO)


def lfg(message: Message) -> Message:
    logger.debug("LETS FRIGGEN GOOOOO")
    return message


@dataclass(frozen=True, slots=True, kw_only=True)
class Router:
    middleware: list[MessageHandler] = field(default_factory=list)

    # Consider, auth should be an explicit middleware so types
    # can guard unauthenticated vs authenticated messages
    # AuthenticatedMessage = NewType('AuthenticatedMessage', Message)
    # OR
    # UnauthenticatedMessage = NewType('UnauthenticatedMessage', Message)
    # could be a better approach since hopefully more calls deal with authenticated messages
    # specify when they aren't authenticated? maybe both?? Change the Message type
    # to BaseMessage?

    @staticmethod
    def for_message_kind(kind: MessageKind) -> Router:
        router = Router()
        # Apply any "global" middleware above the match
        match kind:
            case MessageKind.HELLO:
                # FIXME: Don't love how implicit say_hello is the handler in the middleware, revisit this
                router.add_middleware(say_hello)
            case MessageKind.LFG:

                def lfg(message: Message):
                    logger.debug("LETS FRIGGEN GOOOOO")
                    return message

                router.add_middleware(lfg)
            case _:
                router.add_middleware(
                    lambda message: Message(kind=MessageKind.MALFORMED)
                )

        return router

    def add_middleware(self, handler: MessageHandler) -> None:
        self.middleware.append(handler)

    def apply(self, message: Message) -> Message:
        for middleware in self.middleware:
            message = middleware(message)
        return message
