# coding: utf-8

# Simple module to send messages through a Discord WebHook
# post a message to discord api via a bot
# bot must be added to the server and have write access to the channel
import asyncio
from asyncio import Event
import re
import time
from threading import Thread
from typing import Optional, Tuple, List, Callable
from unittest.mock import Mock

import discord
from discord.embeds import Embed
from discord.file import File

from octoprint_discordremote import Command

# Constants
CHANNEL_ID_LENGTH = 18
BOT_TOKEN_LENGTH = 59


class DiscordImpl:
    class AsyncIOEventWrapper:
        def __init__(self, event: Optional[Event] = None):
            self.set_state = False
            self.event = event

        def set_event(self, event: Optional[Event]):
            self.event = event
            if self.set_state:
                self.event.set()
            else:
                self.event.clear()

        def is_set(self) -> bool:
            if self.event is None:
                return self.set_state
            return self.event.is_set()

        async def wait(self):
            while self.event is None:
                await asyncio.sleep(1)
            await self.event.wait()

        def set(self):
            if self.event:
                self.event.set()
            else:
                self.set_state = True

        def clear(self):
            if self.event:
                self.event.clear()
            else:
                self.set_state = False

    def __init__(self,
                 bot_token: str,
                 channel_id: str,
                 logger,
                 command: Command,
                 status_callback: Callable[[str], None]):
        self.loop = None
        self.client: Optional[discord.Client] = None
        self.running_thread: Optional[Thread] = None
        self.shutdown_event: DiscordImpl.AsyncIOEventWrapper = DiscordImpl.AsyncIOEventWrapper(None)
        self.message_queue: List[List[Tuple[Embed, File]]] = []
        self.thread: Optional[Thread] = None
        self.process_queue: DiscordImpl.AsyncIOEventWrapper = DiscordImpl.AsyncIOEventWrapper(None)
        self.processsing_messages = False

        self.bot_token = bot_token
        self.channel_id = int(channel_id)
        self.logger = logger
        self.command = command
        self.status_callback = status_callback
        self.status_callback(connected="connecting")

        if len(str(self.channel_id)) != CHANNEL_ID_LENGTH:
            self.logger.error("Incorrectly configured: Channel ID must be %d chars long." % CHANNEL_ID_LENGTH)
            return
        if self.bot_token is None or len(self.bot_token) != BOT_TOKEN_LENGTH:
            self.logger.error("Incorrectly configured: Bot Token must be %d chars long." % BOT_TOKEN_LENGTH)
            return
        self.thread = Thread(target=self.run_thread)
        self.thread.start()
        while self.loop is None:
            time.sleep(0.1)

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
            if not self.processsing_messages:
                asyncio.create_task(self.process_message_queue())
            self.status_callback(connected="connected")

        try:
            self.loop = asyncio.get_event_loop()

            # Create proper events now that we have an event loop.
            self.shutdown_event.set_event(Event())
            self.process_queue.set_event(Event())

            future = self.client.run(self.bot_token)
            self.loop.run_until_complete(asyncio.wait([future]))
        except RuntimeError as e:
            self.logger.info("Failed with: %s" % e)
        except Exception as e:
            self.logger.error("Failed with: %s" % e)

    def update_presence(self, msg):
        try:
            if self.client.ws:
                self.loop.create_task(
                    self.client.change_presence(activity=discord.Activity(url='http://octoprint.url', name=msg)))
        except:
            pass

    async def send_messages(self):
        try:
            while len(self.message_queue):
                message_pairs = self.message_queue[0]
                channel = self.client.get_channel(int(self.channel_id))
                for embed, snapshot in message_pairs:
                    await channel.send(embed=embed, file=snapshot)
                del self.message_queue[0]
            if len(self.message_queue) == 0:
                self.process_queue.clear()
        except Exception as e:
            self.logger.error("Failed with: %s" % e)

    async def process_message_queue(self):
        self.processsing_messages = True
        while not self.shutdown_event.is_set():
            await self.send_messages()
            if len(self.message_queue) != 0:
                await asyncio.sleep(10)
                continue
            await self.process_queue.wait()

    def send(self, messages: List[Tuple[Optional[Embed], Optional[File]]]):
        self.message_queue.append(messages)
        self.process_queue.set()

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
                self.send(messages)

        if len(message.content) > 0:
            messages = self.command.parse_command(message.content, user)
            self.send(messages)

    def shutdown_discord(self):
        self.status_callback(connected="disconnected")
        self.shutdown_event.set()
        self.process_queue.set()
        if self.loop:
            self.loop.stop()
