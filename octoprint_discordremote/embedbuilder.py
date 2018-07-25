from future.backports import datetime

COLOR_SUCCESS = 0x00AE86
COLOR_ERROR = 0xE84A4A
COLOR_INFO = 0xF2E82B

MAX_TITLE = 256
MAX_VALUE = 1024
MAX_DESCRIPTION = 2048
MAX_EMBED_LENGTH = 6000
MAX_NUM_FIELDS = 25


def embed_simple(title=None, description=None, color=None):
    builder = EmbedBuilder()
    if color:
        builder.set_color(color)
    if title:
        builder.set_title(title)
    if description:
        builder.set_description(description)
    return builder.get_embeds()


def success_embed(title=None, description=None):
    return embed_simple(title, description, COLOR_SUCCESS)


def error_embed(title=None, description=None):
    return embed_simple(title, description, COLOR_ERROR)


def info_embed(title=None, description=None):
    return embed_simple(title, description, COLOR_INFO)


class EmbedBuilder:

    def __init__(self):
        self.color = COLOR_INFO
        self.title = None
        self.description = None
        self.timestamp = True
        self.fields = []

    def set_color(self, color):
        self.color = color
        return self

    def set_title(self, title):
        if title is None:
            self.title = "ERROR: Title was None"
            return self
        if len(title) > MAX_TITLE:
            self.title = "ERROR: Title was too long for an embed: %d > %d" % (len(title), MAX_TITLE)
            return self
        self.title = title
        return self

    def set_description(self, description):
        if description is None:
            self.description = "ERROR: Description was None"
            return self
        if len(description) > MAX_DESCRIPTION:
            self.description = "ERROR: Description was too long for an embed: %d > %d" % (len(description), MAX_DESCRIPTION)
            return self
        self.description = description
        return self

    def add_field(self, title, text, inline=False):
        if title and len(str(title)) > MAX_TITLE:
            title = "ERROR: Title was too long for an embed: %d > %d" % (len(str(title)), MAX_TITLE)
        if text and len(str(text)) > MAX_VALUE:
            text = "ERROR: Text was too long for an embed: %d > %d" % (len(str(text)), MAX_VALUE)
        self.fields.append({'name': str(title), 'value': str(text), 'inline': inline})
        return self

    def enable_timestamp(self, enable):
        self.timestamp = enable

    def get_embeds(self):
        embeds = [self.new_embed()]
        current_embed_length = 0
        if self.title:
            embeds[0]['title'] = self.title
            current_embed_length += len(self.title)

        if self.description:
            embeds[0]['description'] = self.description
            current_embed_length += len(self.description)

        for field in self.fields:
            if current_embed_length + len(field['name']) + len(field['value']) > MAX_EMBED_LENGTH:
                embeds.append(self.new_embed())
                current_embed_length = 0

            embeds[-1]['fields'].append(field)
            current_embed_length += len(field['name']) + len(field['value'])

            if len(embeds[-1]['fields']) == MAX_NUM_FIELDS:
                embeds.append(self.new_embed())
                current_embed_length = 0

        return embeds

    def new_embed(self):
        embed = {'fields': []}
        if self.timestamp:
            embed['timestamp'] = datetime.datetime.utcnow().isoformat()
        if self.color:
            embed['color'] = self.color
        return embed
