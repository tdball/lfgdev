from __future__ import annotations

import logging
from lfgdev.server.db import Database
from asyncio import StreamReader
from lfgdev.messages.kind import MessageKind
from lfgdev.messages.header import Header
from lfgdev.messages.hello import Hello, NoHello
from lfgdev.messages.protocol import Message


logger = logging.getLogger(__name__)


async def parse_request(kind: MessageKind, reader: StreamReader) -> Message:
    match kind:
        case MessageKind.HELLO:
            return await Hello.from_stream(reader)
        case _:
            raise NotImplementedError("No Route Defined")


def handle_message(header: Header, request: Message, db: Database) -> Message:
    # Middleware?
    if db.find_by_username(header.sent_by) is None:
        db.save(header.sent_by)
    else:
        db.update(header.sent_by)

    match request.kind:
        case MessageKind.HELLO:
            return NoHello()
        case _:
            raise NotImplementedError("Ohhhh how did we get here.")
