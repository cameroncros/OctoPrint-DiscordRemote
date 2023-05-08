from typing import Optional, Tuple, io

from proto.messages_pb2 import EmbedContent, File

COLOR_SUCCESS = 0x00AE86
COLOR_ERROR = 0xE84A4A
COLOR_INFO = 0xF2E82B


def embed_simple(author: str,
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 color: Optional[int] = None,
                 snapshot: Optional[File] = None) -> EmbedContent:
    content = EmbedContent()
    content.author = author
    content.title = title
    content.description = description
    content.color = color
    if snapshot:
        content.snapshot = snapshot
    return content


def success_embed(author: str,
                  title: Optional[str] = None,
                  description: Optional[str] = None,
                  snapshot: Optional[File] = None) -> EmbedContent:
    return embed_simple(author, title, description, COLOR_SUCCESS, snapshot)


def error_embed(author: str,
                title: Optional[str] = None,
                description: Optional[str] = None,
                snapshot: Optional[File] = None) -> EmbedContent:
    return embed_simple(author, title, description, COLOR_ERROR, snapshot)


def info_embed(author: str,
               title: Optional[str] = None,
               description: Optional[str] = None,
               snapshot: Optional[File] = None) -> EmbedContent:
    return embed_simple(author, title, description, COLOR_INFO, snapshot)
