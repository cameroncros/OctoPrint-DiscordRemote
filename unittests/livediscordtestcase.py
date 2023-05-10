import asyncio
import os
import socket
import threading
import time
import uuid
from typing import IO, Optional

import discord
import yaml
from _pytest.outcomes import fail

from octoprint_discordshim.discordshim import DiscordShim
from unittests.mockdiscordtestcase import MockDiscordTestCase


class Scraper:
    lock = threading.Lock()
    running = True
    file: Optional[IO]

    def __init__(self, filename: str, bot_token: str, channel_id: str):
        self.filename = filename
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.client = discord.Client(intents=discord.Intents.all())

        @self.client.event
        async def on_message(message):
            if message.channel.id != int(channel_id) and message.channel.type.name != "private":
                # Only care about messages from correct channel, or DM messages
                return

            self.lock.acquire()
            embed = message.embeds[0]
            js = f"Title: [{embed.title}] Description: [{embed.description}] "
            if embed.fields is not None:
                js += f" NumFields: [{len(embed.fields)}]"
            if embed.image is not None:
                js += f" Image: [{str(embed.image)}]"
            js += '\n'
            if self.file is None:
                self.file = open(self.filename, 'w')
            self.file.write(js)
            self.file.flush()
            self.lock.release()

        @self.client.event
        async def on_ready():
            self.lock.acquire()
            self.file = open(self.filename, 'w')
            self.file.flush()
            self.lock.release()
            asyncio.create_task(self.wait_for_shutdown())

    async def wait_for_shutdown(self):
        while self.running:
            await asyncio.sleep(1)
        self.file.close()
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
    scraper_file: str

    @classmethod
    def discordshim_function(cls, port: int):
        os.environ['BOT_TOKEN'] = cls.bot_token
        os.environ['CHANNEL_ID'] = cls.channel_id
        os.environ['DISCORD_LINK_PORT'] = str(port)

        cls.discord = DiscordShim()
        cls.discord.run()

    def start_scraper(self):
        self.scraper_file = f'/tmp/discord_scraper_{str(uuid.uuid4())}'
        self.scraper = Scraper(self.scraper_file, self.bot_token, self.channel_id)
        self.scraper_thread = threading.Thread(target=self.scraper.run)
        self.scraper_thread.start()

        while not os.path.exists(self.scraper_file):
            time.sleep(1)

    def stop_scraper(self):
        time.sleep(5)
        results = []
        self.scraper.stop()
        self.scraper_thread.join()

        with open(self.scraper_file, 'r') as f:
            line = f.readline()
            print(f"Message Content: {line}")
            if len(line.strip()) != 0:
                results.append(line)
        os.remove(self.scraper_file)
        return results

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
