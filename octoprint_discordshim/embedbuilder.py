from __future__ import unicode_literals

import io
import math
import os
import zipfile
from datetime import datetime
from typing import Tuple, List, Optional

from discord.embeds import Embed
from discord.file import File

from octoprint_discordremote.responsebuilder import COLOR_INFO
from octoprint_discordremote.proto.messages_pb2 import EmbedContent, ProtoFile

DISCORD_MAX_FILE_SIZE = 5 * 1024 * 1024

MAX_TITLE = 256
MAX_VALUE = 1024
MAX_DESCRIPTION = 2048
MAX_EMBED_LENGTH = 6000
MAX_NUM_FIELDS = 25


def embed_simple(data: EmbedContent) -> List[Tuple[Embed, File]]:
    builder = EmbedBuilder()
    builder.set_author(data.author)
    builder.set_description(data.description)
    if data.color:
        builder.set_color(data.color)
    if data.title:
        builder.set_title(data.title)
    if data.snapshot:
        builder.set_image(filename=data.snapshot.filename, snapshot=data.snapshot.data)
    for field in data.textfield:
        builder.add_field(field.title, field.text, field.inline)

    return builder.get_embeds()


def upload_file(file: ProtoFile, author=None) -> List[Tuple[Optional[Embed], Optional[File]]]:
    file_name = file.filename
    file_size = len(file.data)

    if file_size < DISCORD_MAX_FILE_SIZE:
        embeds = EmbedBuilder() \
            .set_author(author) \
            .set_title("Uploaded %s" % file_name) \
            .get_embeds()
        embeds.append((None, File(io.BytesIO(file.data), file_name)))
        return embeds

    else:
        with zipfile.ZipFile("temp.zip", 'w') as zip_file:
            zip_file.writestr(file_name, file.data)

        # Get the compressed file size
        file_stat = os.stat("temp.zip")
        file_size = file_stat.st_size
        num_parts = int(math.ceil(float(file_size) / DISCORD_MAX_FILE_SIZE))

        embedbuilder = EmbedBuilder() \
            .set_author(author) \
            .set_title("Uploaded %s in %i parts" % (file_name, num_parts))
        messages = embedbuilder.get_embeds()

        with open("temp.zip", 'rb') as zip_file:
            i = 1
            while True:
                part_name = "%s.zip.%.03i" % (file_name, i)
                part_file = io.BytesIO()
                data = zip_file.read(DISCORD_MAX_FILE_SIZE)
                if len(data) == 0:
                    break
                part_file.write(data)
                part_file.seek(0)
                messages.append((None, File(part_file, filename=part_name)))
                i += 1

        os.remove("temp.zip")
        return messages


class EmbedBuilder:
    def __init__(self):
        self.color = COLOR_INFO
        self.embeds = [EmbedWrapper()]
        self.timestamp = True
        self.author = None
        self.files: List[File] = []

    def set_color(self, color):
        self.color = color
        return self

    def set_title(self, title):
        if title is None:
            title = ""
        elif len(title) > MAX_TITLE:
            title = title[0:MAX_TITLE - 3] + "..."

        while not self.embeds[-1].set_title(title):
            self.embeds.append(EmbedWrapper())

        return self

    def set_description(self, description):
        if description is None or description == "":
            description = "\u200b"
        elif len(description) > MAX_DESCRIPTION:
            description = description[0:MAX_DESCRIPTION - 3] + "..."

        while not self.embeds[-1].set_description(description):
            self.embeds.append(EmbedWrapper())

        return self

    def set_author(self, name, url=None, icon_url=None):
        if name is None:
            self.author = ""
            return self
        if len(name) > MAX_TITLE:
            name = name[0:MAX_TITLE - 3] + "..."
        self.author = {'name': name}
        if url:
            self.author['url'] = url
        if icon_url:
            self.author['icon_url'] = icon_url
        return self

    def add_field(self, title, text, inline=False):
        if title is None or len(title) == 0:
            title = ""
        if text is None or len(text) == 0:
            text = ""

        if len(title) > MAX_TITLE:
            title = title[0:MAX_TITLE - 3] + "..."
        if len(text) > MAX_VALUE:
            text = text[0:MAX_VALUE - 3] + "..."

        while not self.embeds[-1].add_field({'name': title,
                                             'value': text,
                                             'inline': inline}):
            self.embeds.append(EmbedWrapper())

        return self

    def enable_timestamp(self, enable):
        self.timestamp = enable
        return self

    def set_image(self, snapshot: bytes, filename: str):
        if snapshot and len(snapshot) == 2:
            self.embeds[-1].set_image(file=snapshot, filename=filename)
        return self

    def get_embeds(self) -> List[Tuple[Optional[Embed], Optional[File]]]:
        # Finalise changes to embeds
        self.embeds[-1].timestamp = self.timestamp

        embeds: List[Tuple[Optional[Embed], Optional[File]]] = []
        for embed in self.embeds:
            embed.color = self.color
            if self.author:
                embed.set_author(self.author)
            embeds.append(embed.get_embed())

        return embeds

    def __str__(self):
        string = ""
        for embed in self.get_embeds():
            string += embed


class EmbedWrapper:
    def __init__(self):
        self.embed_length = 0
        self.color = COLOR_INFO
        self.title = None
        self.description = None
        self.timestamp = True
        self.fields = []
        self.files = []
        self.author = None
        self.image_url: Optional[str] = None
        self.file: Optional[File] = None

    def set_author(self, author):
        current_length = 0
        if self.author:
            current_length = len(self.author['name'])
        if self.embed_length - current_length + len(author['name']) > MAX_EMBED_LENGTH:
            return False
        self.embed_length -= current_length
        self.author = author
        self.embed_length += len(self.author['name'])
        return True

    def set_title(self, title):
        current_length = 0
        if self.title:
            current_length = len(self.title)
        if self.embed_length - current_length + len(title) > MAX_EMBED_LENGTH:
            return False
        self.embed_length -= current_length
        self.title = title
        self.embed_length += len(self.title)
        return True

    def set_description(self, description):
        current_length = 0
        if self.description:
            current_length = len(self.description)
        if self.embed_length - current_length + len(description) > MAX_EMBED_LENGTH:
            return False
        self.embed_length -= current_length
        self.description = description
        self.embed_length += len(self.description)
        return True

    def add_field(self, field):
        if len(self.fields) == MAX_NUM_FIELDS:
            return False

        field_length = 0
        if 'name' in field and field['name']:
            field_length += len(field['name'])
        if 'value' in field and field['value']:
            field_length += len(field['value'])

        if self.embed_length + field_length > MAX_EMBED_LENGTH:
            return False

        self.fields.append(field)
        self.embed_length += field_length
        return True

    def set_image(self, file: bytes, filename: str):
        self.image_url = "attachment://%s" % filename
        self.file = File(file, filename=filename)

    def get_embed(self) -> Tuple[Optional[Embed], Optional[File]]:
        embed = Embed(title=self.title if self.title else "",
                      description=self.description if self.description else "",
                      colour=self.color,
                      timestamp=datetime.now())
        for field in self.fields:
            embed.add_field(name=field['name'], value=field['value'])
        if self.author:
            embed.set_author(name=self.author['name'],
                             url=self.author.get('url', None),
                             icon_url=self.author.get('icon_url', None))
        if self.image_url:
            embed.set_image(url=self.image_url)
        return embed, self.file

    def get_files(self):
        return self.files

    # def __str__(self):
    #     embed = self.get_embed()
    #     string = "\n---------------------------------\n"
    #     if 'author' in embed:
    #         string += "~~Author~~~~~~~~~~~~~~~~~~\n"
    #         if 'name' in embed['author']:
    #             string += "\tAuthor Name: %s\n" % embed['author']['name']
    #         if 'url' in embed['author']:
    #             string += "\tAuthor Url: %s\n" % embed['author']['url']
    #         if 'icon_url' in embed['author']:
    #             string += "\tAuthor Icon: %s\n" % embed['author']['icon_url']
    #         string += "~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
    #     if 'color' in embed:
    #         string += "Color: %x\n" % embed['color']
    #     if 'title' in embed:
    #         string += "Title: %s\n" % embed['title']
    #     if 'description' in embed:
    #         string += "Description: %s\n" % embed['description']
    #     for field in embed['fields']:
    #         string += "~~~Field~~~~~~~~~~~~~~~~~~\n"
    #         if 'name' in field:
    #             string += "\tField Name: %s\n" % field['name']
    #         if 'value' in field:
    #             string += "\tField Value: %s\n" % field['value']
    #         string += "~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
    #     if 'image' in embed:
    #         string += "Attached image: %s\n" % embed['image']['url']
    #     if 'timestamp' in embed:
    #         string += "Timestamp: %s\n" % embed['timestamp']
    #     string += "---------------------------------\n"
    #     return string
