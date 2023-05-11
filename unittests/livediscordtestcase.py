import asyncio
import os
import socket
import threading
import time
from typing import List

import discord
import yaml
from _pytest.outcomes import fail
from discord.message import Message

from octoprint_discordremote import Settings
from octoprint_discordshim.discordshim import DiscordShim
from unittests.mockdiscordtestcase import MockDiscordTestCase


class Scraper:
    lock = threading.Lock()
    running = True
    messages = []

    def __init__(self, bot_token: str, channel_id: str):
        self.is_connected = False
        self.messages = []
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.client = discord.Client(intents=discord.Intents.all())

        @self.client.event
        async def on_message(message):
            if message.channel.id != int(channel_id) and message.channel.type.name != "private":
                # Only care about messages from correct channel, or DM messages
                return

            self.lock.acquire()
            self.messages.append(message)
            self.lock.release()

        @self.client.event
        async def on_ready():
            self.lock.acquire()
            self.is_connected = True
            self.lock.release()
            asyncio.create_task(self.wait_for_shutdown())

    async def wait_for_shutdown(self):
        while self.running:
            await asyncio.sleep(1)
        await self.client.close()

    def run(self):
        self.client.run(self.bot_token)

    def stop(self):
        self.running = False


class LiveDiscordTestCase(MockDiscordTestCase):
    bot_token: str
    channel_id: str
    discord: DiscordShim
    client: socket
    thread: threading.Thread
    snapshot_bytes: bytes = []

    scraper_pid: int

    @classmethod
    def discordshim_function(cls, port: int):
        os.environ['BOT_TOKEN'] = cls.bot_token
        os.environ['DISCORD_LINK_PORT'] = str(port)

        cls.discord = DiscordShim()
        cls.discord.channel_id = cls.channel_id
        cls.discord.run()

    def start_scraper(self):
        self.scraper = Scraper(self.bot_token, self.channel_id)
        self.scraper_thread = threading.Thread(target=self.scraper.run)
        self.scraper_thread.start()

        while not self.scraper.is_connected:
            time.sleep(1)

    def stop_scraper(self, waitformessages, timeout=300) -> List[Message]:
        count = 0
        while len(self.scraper.messages) < waitformessages:
            time.sleep(1)
            count += 1
            if count > timeout:
                raise TimeoutError()
        self.scraper.stop()
        self.scraper_thread.join()
        return self.scraper.messages

    @classmethod
    def setUpClass(cls):
        config_file = cls._get_path("../config.yaml")
        with open(config_file) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            cls.bot_token = data['bottoken']
            cls.channel_id = data['channelid']

        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.settimeout(10)
            server.bind(('127.0.0.1', 0))
            sock_details = server.getsockname()
            server.listen()

            cls.thread = threading.Thread(target=cls.discordshim_function,
                                          args=(sock_details[1],))
            cls.thread.start()

            try:
                cls.client, _ = server.accept()
                server.close()
            except socket.timeout:
                pass
        except:
            fail("To test discord bot posting, you need to create a file "
                 "called config.yaml in the root directory with your bot "
                 "details. NEVER COMMIT THIS FILE.")

        with open(cls._get_path("test_pattern.png"), "rb") as f:
            cls.snapshot_bytes = f.read()

    @classmethod
    def tearDownClass(cls):
        cls.discord.stop()
        cls.thread.join()
