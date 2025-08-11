from asyncio import StreamReader, StreamWriter
from typing import ClassVar

from lfgdev.message import Message
from lfgdev.server.db import Database
from lfgdev.server.message_handler import MessageHandler
from lfgdev.server.middleware import log_message, update_last_seen
from lfgdev.server.types import Middleware
from lfgdev.types import immutable


@immutable
class RequestHandler:
    _middleware: ClassVar[list[Middleware]] = [log_message, update_last_seen]
    db: Database

    def apply_middleware(self, message: Message) -> Message:
        for middleware in self._middleware:
            message = middleware(self.db, message)
        return message

    async def handle(self, reader: StreamReader, writer: StreamWriter) -> None:
        try:
            message = await Message.receive(reader)
            self.apply_middleware(message)
            router = MessageHandler(db=self.db)
            reply = router.route(message)
            await reply.send(stream=writer)

        finally:
            writer.close()
            await writer.wait_closed()
