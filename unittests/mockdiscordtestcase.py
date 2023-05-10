import logging
import os
import socket
from typing import Optional
from unittest import TestCase
from unittest.mock import Mock
from discord.embeds import Embed

from octoprint_discordremote import DiscordLink, Command
from octoprint_discordremote.proto.messages_pb2 import Response, ProtoFile


class TestLogger(logging.Logger):
    def __init__(self):
        super(TestLogger, self).__init__(name="")

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


class MockDiscordTestCase(TestCase):
    discord: Optional[DiscordLink] = None
    snapshot_bytes: bytes = []
    client: socket  # Discord link side
    server: socket  # Discord shim side

    @classmethod
    def setUpClass(cls):
        cls.discord = DiscordLink(bot_token='bottoken',
                                  channel_id='channelid',
                                  command=Command(Mock()))
        # Intentionally not calling cls.discord.run(),
        # as it will spawn discordshim which we dont want

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(10)
        server.bind(('127.0.0.1', 0))
        sock_details = server.getsockname()
        server.listen()

        cls.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.client.settimeout(10)
        cls.client.connect(('127.0.0.1', sock_details[1]))

        while cls.discord.client is None:
            try:
                cls.discord.client, _ = server.accept()
                server.close()
            except socket.timeout:
                pass

        with open(cls._get_path("test_pattern.png"), "rb") as f:
            cls.snapshot_bytes = f.read()

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls.discord.shutdown_discord()

    @staticmethod
    def _get_path(filename):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)

    def assertBasicEmbed(self, embed: Embed, title, description, color, author):
        if title is not None:
            self.assertEqual(title, embed.title)
        if description is not None:
            self.assertEqual(description, embed.description)
        if color is not None:
            self.assertEqual(color, embed.color.value)
        self.assertIsNotNone(embed.timestamp)
        self.assertEqual(0, len(embed.fields))
        if author is not None:
            self.assertEqual(author, embed.author.name)

    def validateResponse(self, response: Response, color, title=None, description=None,
                         image: Optional[ProtoFile] = None):
        self.assertIsNotNone(response)

        embed = response.embed
        self.assertIsNotNone(embed)

        self.assertEqual(color, embed.color)

        if title:
            self.assertEqual(title, embed.title)

        if description:
            self.assertEqual(description, embed.description)

        if image:
            self.assertEqual(embed.snapshot.filename, image.filename)
            self.assertEqual(embed.snapshot.data, image.data)
