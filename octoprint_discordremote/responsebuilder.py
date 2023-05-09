from typing import Optional

from proto.messages_pb2 import EmbedContent, ProtoFile, Response

COLOR_SUCCESS = 0x00AE86
COLOR_ERROR = 0xE84A4A
COLOR_INFO = 0xF2E82B


def embed_simple(author: str,
                 description: str,
                 title: Optional[str] = None,
                 color: Optional[int] = None,
                 snapshot: Optional[ProtoFile] = None) -> Response:
    content = EmbedContent()
    content.author = author
    content.description = description
    if title:
        content.title = title
    if color:
        content.color = color
    if snapshot:
        content.snapshot.data = snapshot.data
        content.snapshot.filename = snapshot.filename
    return Response(embed=content)


def success_embed(author: str,
                  title: Optional[str] = None,
                  description: Optional[str] = None,
                  snapshot: Optional[ProtoFile] = None) -> Response:
    return embed_simple(author, title, description, COLOR_SUCCESS, snapshot)


def error_embed(author: str,
                title: Optional[str] = None,
                description: Optional[str] = None,
                snapshot: Optional[ProtoFile] = None) -> Response:
    return embed_simple(author, title, description, COLOR_ERROR, snapshot)


def info_embed(author: str,
               title: Optional[str] = None,
               description: Optional[str] = None,
               snapshot: Optional[ProtoFile] = None) -> Response:
    return embed_simple(author, title, description, COLOR_INFO, snapshot)
