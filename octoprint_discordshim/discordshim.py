# coding: utf-8

# Simple module to send messages through a Discord WebHook
# post a message to discord api via a bot
# bot must be added to the server and have write access to the channel
import asyncio
import os
import re
from asyncio import Event
from http.client import HTTPException
from logging import Logger
from threading import Thread
from typing import Optional, Tuple, List

import discord
import yaml
from discord.embeds import Embed
from discord.file import File

from octoprint_discordshim.embedbuilder import embed_simple, upload_file
from proto.messages_pb2 import Command, Response, Presence


class DiscordShim:
    writer = None

    def __init__(self):
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

        self.loop = None
        self.client: Optional[discord.Client] = None
        self.running_thread: Optional[Thread] = None
        self.message_queue: List[List[Tuple[Embed, File]]] = []
        self.process_queue: Optional[Event] = None
        self.processsing_messages = False
        self.is_running = True

        self.logger = Logger("discordshim")

        self.client = discord.Client(intents=discord.Intents.all())

        @self.client.event
        async def on_message(message):
            await self.handle_message(message)

        @self.client.event
        async def on_ready():
            self.logger.info("Sending msgs")
            asyncio.create_task(self.talk_to_octoprint())

        self.client.run(self.bot_token)

    def update_presence(self, msg: Presence):
        try:
            if self.client.ws:
                self.loop.create_task(
                    self.client.change_presence(activity=discord.Activity(url='http://octoprint.url', name=msg.presence)))
        except:
            pass

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
        if message.channel.id != self.channel_id and message.channel.type.name != "private":
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

                messages = self.command.download_file(filename, url, user)
                await self.send(messages)

        if len(message.content) == 0:
            return

        cmdproto = Command(command=message.content).SerializeToString()
        self.writer.write(len(cmdproto).to_bytes(length=4, byteorder='little'))
        self.writer.write(cmdproto)

    async def get_messages(self, client):
        pass

    async def talk_to_octoprint(self):
        reader, self.writer = await asyncio.open_connection(
            '127.0.0.1', self.port)

        while True:
            length_bytes = await reader.read(4)
            length = int.from_bytes(length_bytes, byteorder='little')

            data_bytes = await reader.read(length)
            data = Response()
            data.ParseFromString(data_bytes)
            if data.embed:
                await self.send(embed_simple(data.embed))
            elif data.file:
                await self.send(upload_file(data.file))
            elif data.presence:
                await self.update_presence(data.presence)

