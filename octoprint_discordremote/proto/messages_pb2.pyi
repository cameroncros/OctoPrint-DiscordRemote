from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EmbedContent(_message.Message):
    __slots__ = ["author", "color", "description", "snapshot", "textfield", "title"]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    TEXTFIELD_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    author: str
    color: int
    description: str
    snapshot: ProtoFile
    textfield: _containers.RepeatedCompositeFieldContainer[TextField]
    title: str
    def __init__(self, title: _Optional[str] = ..., description: _Optional[str] = ..., author: _Optional[str] = ..., color: _Optional[int] = ..., snapshot: _Optional[_Union[ProtoFile, _Mapping]] = ..., textfield: _Optional[_Iterable[_Union[TextField, _Mapping]]] = ...) -> None: ...

class Presence(_message.Message):
    __slots__ = ["presence"]
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    presence: str
    def __init__(self, presence: _Optional[str] = ...) -> None: ...

class ProtoFile(_message.Message):
    __slots__ = ["data", "filename"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    filename: str
    def __init__(self, data: _Optional[bytes] = ..., filename: _Optional[str] = ...) -> None: ...

class Request(_message.Message):
    __slots__ = ["command", "file", "user"]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    command: str
    file: ProtoFile
    user: int
    def __init__(self, user: _Optional[int] = ..., command: _Optional[str] = ..., file: _Optional[_Union[ProtoFile, _Mapping]] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ["embed", "file", "presence", "settings"]
    EMBED_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    embed: EmbedContent
    file: ProtoFile
    presence: Presence
    settings: Settings
    def __init__(self, embed: _Optional[_Union[EmbedContent, _Mapping]] = ..., presence: _Optional[_Union[Presence, _Mapping]] = ..., file: _Optional[_Union[ProtoFile, _Mapping]] = ..., settings: _Optional[_Union[Settings, _Mapping]] = ...) -> None: ...

class Settings(_message.Message):
    __slots__ = ["channel_id", "command_prefix", "cycle_time", "presence_enabled"]
    CHANNEL_ID_FIELD_NUMBER: _ClassVar[int]
    COMMAND_PREFIX_FIELD_NUMBER: _ClassVar[int]
    CYCLE_TIME_FIELD_NUMBER: _ClassVar[int]
    PRESENCE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    channel_id: int
    command_prefix: str
    cycle_time: int
    presence_enabled: bool
    def __init__(self, channel_id: _Optional[int] = ..., presence_enabled: bool = ..., cycle_time: _Optional[int] = ..., command_prefix: _Optional[str] = ...) -> None: ...

class TextField(_message.Message):
    __slots__ = ["inline", "text", "title"]
    INLINE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    inline: bool
    text: str
    title: str
    def __init__(self, title: _Optional[str] = ..., text: _Optional[str] = ..., inline: bool = ...) -> None: ...
