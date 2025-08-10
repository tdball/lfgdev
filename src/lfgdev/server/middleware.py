from lfgdev.server.main import Database
from lfgdev.messages import Message

import logging

LOG = logging.getLogger(__name__)


def update_last_seen(db: Database, message: Message) -> Message:
    if db.find_by_username(message.header.sender) is None:
        db.save(message.header.sender)
    else:
        db.update(message.header.sender)
    return message


def log_message(db: Database, message: Message) -> Message:
    print(f"Received message from {message.header.sender}: {message.body}")
    return message
