import json
import logging
import os
import signal
import socket
import threading
import time
import uuid
from unittest import TestCase

import discord
import yaml
from _pytest.outcomes import fail

from octoprint_discordshim.discordshim import DiscordShim

"""
When in fork mode, it is not really easy to debug, but the tests will terminate correctly.

In non-fork mode, you can debug errors, but the tests will not terminate.
"""
FORK = True


def run_scraper(filename: str, bot_token: str, channel_id: str):
    file = open(filename, 'w')
    lock = threading.Lock()
    client = discord.Client(intents=discord.Intents.all())

    @client.event
    async def on_message(message):
        if message.channel.id != int(channel_id) and message.channel.type.name != "private":
            # Only care about messages from correct channel, or DM messages
            return

        lock.acquire()
        embed = message.embeds[0]
        js = f"Title: [{embed.title}] Description: [{embed.description}] "
        if embed.fields is not None:
            js += f" NumFields: [{len(embed.fields)}]"
        if embed.image is not None:
            js += f" Image: [{str(embed.image)}]"
        js += '\n'
        file.write(js)
        file.flush()
        lock.release()

    @client.event
    async def on_ready():
        file.flush()

    client.run(bot_token)


class TestLogger(logging.Logger):
    def __init__(self):
        super(TestLogger, self).__init__(name=None)

    def setLevel(self, level):
        pass

    def debug(self, msg, *args):
        print("DEBUG: %s" % msg, args)

    def info(self, msg, *args):
        print("INFO: %s" % msg, args)

    def warning(self, msg, *args):
        print("WARNING: %s" % msg, args)

    def error(self, msg, *args):
        print("ERROR: %s" % msg, args)

    def exception(self, msg, *args):
        print("EXCEPTION: %s" % msg, args)

    def critical(self, msg, *args):
        print("CRITICAL: %s" % msg, args)


class DiscordShimTestCase(TestCase):
    pid: int
    discord: DiscordShim
    client: socket
    thread: threading.Thread
    snapshot_bytes: bytes = []

    scraper_pid: int
    scraper_file: str

    @classmethod
    def discordshim_function(cls, bot_token: str, channel_id: str, port: int):
        os.environ['BOT_TOKEN'] = bot_token
        os.environ['CHANNEL_ID'] = channel_id
        os.environ['DISCORD_LINK_PORT'] = str(port)

        cls.discord = DiscordShim()
        cls.discord.run()

    def start_scraper(self):
        self.scraper_file = f'/tmp/discord_scraper_{str(uuid.uuid4())}'
        self.scraper_pid = os.fork()
        if self.scraper_pid == 0:
            run_scraper(self.scraper_file, self.bot_token, self.channel_id)
            exit(0)
        else:
            while not os.path.exists(self.scraper_file):
                time.sleep(1)

    def stop_scraper(self):
        time.sleep(5)
        results = []
        if self.scraper_pid > 0:
            os.kill(self.scraper_pid, signal.SIGKILL)
            os.waitpid(self.scraper_pid, 0)
        with open(self.scraper_file, 'r') as f:
            line = f.readline()
            print(f"Message Content: {line}")
            if len(line.strip()) != 0:
                results.append(line)
        os.remove(self.scraper_file)
        return results

    @classmethod
    def setUpClass(cls):
        config_file = cls._get_path("../../config.yaml")
        with open(config_file) as f:
            data = yaml.load(f)
            cls.bot_token = data['bottoken']
            cls.channel_id = data['channelid']

        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.settimeout(10)
            server.bind(('127.0.0.1', 0))
            sock_details = server.getsockname()
            server.listen()

            if FORK:
                cls.pid = os.fork()
                if cls.pid == 0:
                    os.environ['BOT_TOKEN'] = cls.bot_token
                    os.environ['CHANNEL_ID'] = cls.channel_id
                    os.environ['DISCORD_LINK_PORT'] = str(sock_details[1])
                    DiscordShim().run()
                    exit(0)
            else:
                cls.thread = threading.Thread(target=cls.discordshim_function,
                                              args=(cls.bot_token, cls.channel_id, sock_details[1]))
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

        with open(cls._get_path("../test_pattern.png"), "rb") as f:
            cls.snapshot_bytes = f.read()

    @classmethod
    def tearDownClass(cls):
        if FORK and cls.pid > 0:
            os.kill(cls.pid, signal.SIGKILL)

        # TODO work out how to properly kill discord, or move it back to its own process.

    @staticmethod
    def _get_path(filename):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
