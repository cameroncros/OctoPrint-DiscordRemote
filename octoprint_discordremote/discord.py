# coding: utf-8

# Simple module to send messages through a Discord WebHook
# post a message to discord api via a bot
# bot must be added to the server and have write access to the channel
import asyncio
import re
from threading import Thread, Event
from typing import Optional, Tuple, List
from unittest.mock import Mock
from discord import Embed, File
import discord

from octoprint_discordremote import Command

# Constants
CHANNEL_ID_LENGTH = 18
BOT_TOKEN_LENGTH = 59


def asyncio_run(futures):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(futures))


class Discord:
    def __init__(self):
        self.logger = None
        self.channel_id: int = 0  # enable dev mode on discord, right-click on the channel, copy ID
        self.bot_token: str = ""  # get from the bot page. must be a bot, not a discord app
        self.client: Optional[discord.Client] = None
        self.running_thread: Optional[Thread] = None
        self.command: Optional[Command] = None
        self.shutdown_event: Event = Event()
        self.message_queue: List[List[Tuple[Embed, File]]] = []
        self.thread: Optional[Thread] = None

    def configure_discord(self, bot_token: str, channel_id: str, logger, command: Command, status_callback=None):
        self.bot_token = bot_token
        self.channel_id = int(channel_id)
        if logger:
            self.logger = logger
        self.command = command

        if len(str(self.channel_id)) != CHANNEL_ID_LENGTH:
            self.logger.error("Incorrectly configured: Channel ID must be %d chars long." % CHANNEL_ID_LENGTH)
            return
        if self.bot_token is None or len(self.bot_token) != BOT_TOKEN_LENGTH:
            self.logger.error("Incorrectly configured: Bot Token must be %d chars long." % BOT_TOKEN_LENGTH)
            return
        self.thread = Thread(target=self.run_thread)
        self.thread.start()

    def run_thread(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

        loop.add_signal_handler = Mock()

        self.client = discord.Client()

        @self.client.event
        async def on_message(message):
            await self.handle_message(message)

        @self.client.event
        async def on_ready():
            self.logger.info("Sending msgs")
            await self.process_message_queue()

        asyncio_run(self.client.run(self.bot_token))

    def update_presence(self, msg):
        if self.client is not None and self.client.is_ready():
            asyncio_run(self.client.change_presence(activity=discord.Activity(url='http://octoprint.url', name=msg)))

    async def send_messages(self):
        try:
            while len(self.message_queue):
                message_pairs = self.message_queue[0]
                channel = self.client.get_channel(int(self.channel_id))
                for embed, snapshot in message_pairs:
                    await channel.send(embed=embed, file=snapshot)
                del self.message_queue[0]
        except Exception as e:
            pass

    async def process_message_queue(self):
        while True:
            await self.send_messages()
            await asyncio.sleep(30)

    async def send(self, messages: List[Tuple[Optional[Embed], Optional[File]]]):
        if messages is None:
            messages = []
        self.message_queue.append(messages)
        await self.send_messages()

    def log_safe(self, message):
        return message.replace(self.bot_token, "[bot_token]").replace(self.channel_id, "[channel_id]")

    async def handle_message(self, message):
        if message.channel.id != self.channel_id:
            # Only care about messages from correct channel
            return
        self.logger.debug("Message is: %s" % message)

        user = message.author.id
        if user == self.client.user.id:
            # Don't respond to ourself.
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

        if len(message.content) > 0:
            messages = self.command.parse_command(message.content, user)
            await self.send(messages)

    def shutdown_discord(self):
        if self.client:
            self.client.close()
