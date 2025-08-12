from __future__ import annotations

import logging
from typing import Self

from lfgdev.message.body import Body
from lfgdev.message.decoder import register_decoder
from lfgdev.message.structs import MessageStructs
from lfgdev.types import ContentType, immutable

LOG = logging.getLogger(__name__)


@immutable
@register_decoder(ContentType.ERROR)
class Error(Body):
    STRUCT = MessageStructs.ERROR
    content: str

    def encode(self) -> bytes:
        # TODO: Testing out no struct on the class
        bytes = MessageStructs.ERROR.pack(self.content.encode("UTF-8"))
        if len(self.content) > MessageStructs.ERROR.size:
            LOG.warning(
                f"Error content too long: {self.content}, truncating to {MessageStructs.ERROR.size} characters"
            )

        return bytes

    @classmethod
    def decode(cls, data: bytes) -> Self:
        decoded = MessageStructs.ERROR.unpack(data)[0]
        return cls(content=decoded)
