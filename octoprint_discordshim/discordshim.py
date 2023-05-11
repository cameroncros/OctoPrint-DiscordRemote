# coding: utf-8

# Simple module to send messages through a Discord WebHook
# post a message to discord api via a bot
# bot must be added to the server and have write access to the channel
import asyncio
import os
import re
from logging import Logger
from typing import Optional, Tuple, List

import discord
import requests as requests
import yaml
from discord.embeds import Embed
from discord.file import File

from octoprint_discordremote.proto.messages_pb2 import Request, Response, ProtoFile
from octoprint_discordshim.embedbuilder import embed_simple, upload_file


def download_file(url) -> bytes:
    data = b''
    r = requests.get(url, stream=True)
    for chunk in r.iter_content(chunk_size=1024):
        if chunk:  # filter out keep-alive new chunks
            data += chunk
    return data


class DiscordShim:
    writer = None
    running = True

    presence_enabled = True
    cycle_time = 5
    command_prefix = '/'
    current_status = ""
    presence_cycle = {
        0: "{}help".format(command_prefix),
        1: current_status
    }
    presence_cycle_id = 0

    def __init__(self):
        self.logger = Logger("discordshim")

        config = os.environ.get('CONFIG', None)
        if __debug__ and config:
            with open(config) as f:
                data = yaml.load(f)
                self.bot_token = data['bottoken']
                self.channel_id = data['channelid']
                self.port = 23456
        else:
            self.bot_token = os.environ['BOT_TOKEN']
            os.environ['BOT_TOKEN'] = ''

            self.channel_id = os.environ['CHANNEL_ID']
            os.environ['CHANNEL_ID'] = ''

            self.port = int(os.environ['DISCORD_LINK_PORT'])
            os.environ['DISCORD_LINK_PORT'] = ''

        self.client = discord.Client(intents=discord.Intents.all())

        @self.client.event
        async def on_message(message):
            await self.handle_message(message)

        @self.client.event
        async def on_ready():
            self.logger.info("Sending msgs")
            asyncio.create_task(self.talk_to_octoprint())
            asyncio.create_task(self.update_presence())
            asyncio.create_task(self.wait_for_shutdown())

    def run(self):
        self.client.run(self.bot_token)

    def stop(self):
        self.running = False

    async def send(self, messages: List[Tuple[Optional[Embed], Optional[File]]]):
        channel = self.client.get_channel(int(self.channel_id))
        for embed, snapshot in messages:
            try:
                await channel.send(embed=embed, file=snapshot)
            except discord.errors.HTTPException as e:
                self.logger.error(self.log_safe(str(e)))

    def log_safe(self, message):
        return message.replace(self.bot_token, "[bot_token]").replace(self.channel_id, "[channel_id]")

    async def handle_message(self, message):
        if message.channel.id != int(self.channel_id) and message.channel.type.name != "private":
            # Only care about messages from correct channel, or DM messages
            return
        self.logger.debug("Message is: %s" % message)

        user = message.author.id
        if user == self.client.user.id:
            # Don't respond to our self.
            return

        if message.author.bot:
            # Don't respond to bots.
            return

        for upload in message.attachments:
            filename = upload.filename
            url = upload.url

            if re.match(r"^[\w,\s-]+\.(?:g|gco|gcode|zip(?:\.[\d]*)?)$", filename):
                data = download_file(url)
                cmdproto = Request(file=ProtoFile(data=data, filename=filename), user=user).SerializeToString()
                self.writer.write(len(cmdproto).to_bytes(length=4, byteorder='little'))
                self.writer.write(cmdproto)

        if len(message.content) == 0:
            return

        cmdproto = Request(command=message.content, user=user).SerializeToString()
        self.writer.write(len(cmdproto).to_bytes(length=4, byteorder='little'))
        self.writer.write(cmdproto)

    async def update_presence(self):
        await asyncio.sleep(5)
        while True:
            if self.presence_enabled:
                self.presence_cycle_id += 1
                if self.presence_cycle_id == len(self.presence_cycle):
                    self.presence_cycle_id = 0

                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                                            name=self.presence_cycle[
                                                                                self.presence_cycle_id]))
            else:

                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                                            name=None))

            await asyncio.sleep(self.cycle_time)

    async def talk_to_octoprint(self):
        reader, self.writer = await asyncio.open_connection(
            '127.0.0.1', self.port)

        while True:
            length_bytes = await reader.readexactly(4)
            if len(length_bytes) == 0:
                reader.feed_eof()
                return

            length = int.from_bytes(length_bytes, byteorder='little')

            data_bytes = await reader.readexactly(length)
            data = Response()
            data.ParseFromString(data_bytes)
            if data.HasField('embed'):
                await self.send(embed_simple(data.embed))
            elif data.HasField('file'):
                await self.send(upload_file(data.file))
            elif data.HasField('presence'):
                self.current_status = data.presence.presence

    async def wait_for_shutdown(self):
        while self.running:
            await asyncio.sleep(1)
        await self.client.close()
