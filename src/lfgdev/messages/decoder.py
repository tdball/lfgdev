from lfgdev.types import Body, ContentType
from asyncio import StreamReader


_registered_decoders: dict[ContentType, type[Body]] = {}


def register(body: type[Body]) -> type[Body]:
    if body.content_type in _registered_decoders:
        raise Exception(f"Decoder for {body.content_type.name} already registered")
    _registered_decoders.update({body.content_type: body})
    return body


async def decode(content_type: ContentType, reader: StreamReader) -> Body:
    if content_type not in _registered_decoders:
        raise Exception(f"Decoder for {content_type.name} not registered")

    body = _registered_decoders[content_type]
    data = await reader.readexactly(body.STRUCT.size)
    return body.decode(data)
