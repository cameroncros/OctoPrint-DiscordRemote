# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: messages.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0emessages.proto\"+\n\tProtoFile\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\x12\x10\n\x08\x66ilename\x18\x02 \x01(\t\"8\n\tTextField\x12\r\n\x05title\x18\x01 \x01(\t\x12\x0c\n\x04text\x18\x02 \x01(\t\x12\x0e\n\x06inline\x18\x03 \x01(\x08\"\x8e\x01\n\x0c\x45mbedContent\x12\r\n\x05title\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\x12\x0e\n\x06\x61uthor\x18\x03 \x01(\t\x12\r\n\x05\x63olor\x18\x04 \x01(\x05\x12\x1c\n\x08snapshot\x18\x05 \x01(\x0b\x32\n.ProtoFile\x12\x1d\n\ttextfield\x18\x06 \x03(\x0b\x32\n.TextField\"\x1c\n\x08Presence\x12\x10\n\x08presence\x18\x01 \x01(\t\"d\n\x08Settings\x12\x12\n\nchannel_id\x18\x01 \x01(\t\x12\x18\n\x10presence_enabled\x18\x02 \x01(\x08\x12\x12\n\ncycle_time\x18\x03 \x01(\x05\x12\x16\n\x0e\x63ommand_prefix\x18\x04 \x01(\t\"B\n\x07Request\x12\x0f\n\x07\x63ommand\x18\x01 \x01(\t\x12\x0c\n\x04user\x18\x02 \x01(\x03\x12\x18\n\x04\x66ile\x18\x03 \x01(\x0b\x32\n.ProtoFile\"\xbd\x01\n\x08Response\x12!\n\x05\x65mbed\x18\x01 \x01(\x0b\x32\r.EmbedContentH\x00\x88\x01\x01\x12 \n\x08presence\x18\x02 \x01(\x0b\x32\t.PresenceH\x01\x88\x01\x01\x12\x1d\n\x04\x66ile\x18\x03 \x01(\x0b\x32\n.ProtoFileH\x02\x88\x01\x01\x12 \n\x08settings\x18\x04 \x01(\x0b\x32\t.SettingsH\x03\x88\x01\x01\x42\x08\n\x06_embedB\x0b\n\t_presenceB\x07\n\x05_fileB\x0b\n\t_settingsb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'messages_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _PROTOFILE._serialized_start=18
  _PROTOFILE._serialized_end=61
  _TEXTFIELD._serialized_start=63
  _TEXTFIELD._serialized_end=119
  _EMBEDCONTENT._serialized_start=122
  _EMBEDCONTENT._serialized_end=264
  _PRESENCE._serialized_start=266
  _PRESENCE._serialized_end=294
  _SETTINGS._serialized_start=296
  _SETTINGS._serialized_end=396
  _REQUEST._serialized_start=398
  _REQUEST._serialized_end=464
  _RESPONSE._serialized_start=467
  _RESPONSE._serialized_end=656
# @@protoc_insertion_point(module_scope)
