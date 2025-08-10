from lfgdev.types import immutable, Username
from lfgdev.server.db import Database
from typing import ClassVar
from lfgdev.server.types import Middleware
from asyncio import StreamReader, StreamWriter
from lfgdev.messages import Message
from dataclasses import replace


# Probably should hook this into server startup
from lfgdev.server.middleware import log_message, update_last_seen


@immutable
class RequestHandler:
    db: Database
    middleware: ClassVar[list[Middleware]] = [log_message, update_last_seen]

    def apply_middleware(self, message: Message) -> Message:
        for middleware in self.middleware:
            message = middleware(self.db, message)
        return message

    async def handle(self, reader: StreamReader, writer: StreamWriter) -> None:
        try:
            message = await Message.receive(reader)
            self.apply_middleware(message)

            # Just an echo for now, placeholder
            reply = Message(
                header=replace(message.header, sender=Username("SERVER")),
                body=message.body,
            )
            await reply.send(stream=writer)

        finally:
            writer.close()
            await writer.wait_closed()
