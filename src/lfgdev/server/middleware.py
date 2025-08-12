import logging

from lfgdev.message import Message
from lfgdev.server.main import Database

LOG = logging.getLogger(__name__)


def update_last_seen(db: Database, message: Message) -> Message:
    if db.find_by_username(message.header.sender) is not None:
        db.update(message.header.sender)
    # TODO: Another need for a status code of some sort
    return message


def log_message(db: Database, message: Message) -> Message:
    LOG.info(f"Received message from {message.header.sender}: {message.body}")
    return message
