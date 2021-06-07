# coding: utf-8

# Simple module to send messages through a Discord WebHook
# post a message to discord api via a bot
# bot must be added to the server and have write access to the channel
import asyncio
import re
from threading import Thread, Event
from typing import Optional
from unittest.mock import Mock

import discord

from octoprint_discordremote import Command

# Constants
CHANNEL_ID_LENGTH = 18
BOT_TOKEN_LENGTH = 59


class Discord:
    def __init__(self):
        self.logger = None
        self.channel_id: int = 0  # enable dev mode on discord, right-click on the channel, copy ID
        self.bot_token: str = ""  # get from the bot page. must be a bot, not a discord app
        self.client: Optional[discord.Client] = None
        self.running_thread: Optional[Thread] = None
        self.command: Optional[Command] = None
        self.shutdown_event: Event = Event()

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
        thread = Thread(target=self.run_thread)
        thread.start()

    def run_thread(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

        loop.add_signal_handler = Mock()

        self.client = discord.Client()

        @self.client.event
        async def on_message(message):
            self.logger.error("Received msg: [%s]" % message)
            await self.handle_message(message)

        asyncio.run(self.client.run(self.bot_token))

    def update_presence(self, msg):
        if self.client is not None and self.client.is_ready():
            asyncio.run(self.client.change_presence(activity=discord.Activity(url='http://octoprint.url', name=msg)))

    async def send(self, snapshots=None, embeds=None):
        if embeds is None:
            embeds = []
        if snapshots is None:
            snapshots = []
        if self.client is None:
            return  # todo: queue messages and resend later
        channel = self.client.get_channel(int(self.channel_id))
        for snapshot in snapshots:
            await channel.send(file=snapshot)
        for embed in embeds:
            await channel.send(embed=embed)

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
            filename = upload['filename']
            url = upload['url']

            if re.match(r"^[\w,\s-]+\.(?:g|gco|gcode|zip(?:\.[\d]*)?)$", filename):
                embeds, snapshots = self.command.download_file(filename, url, user)
                await self.send(embeds=embeds)

        if len(message.content) > 0:
            embeds, snapshots = self.command.parse_command(message.content, user)
            await self.send(snapshots=snapshots,
                            embeds=embeds)
