import logging
import time
from unittest import TestCase
import os

import mock
import yaml
from _pytest.outcomes import fail
from discord import Embed

from octoprint_discordremote import DiscordImpl


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


class DiscordRemoteTestCase(TestCase):
    discord = None

    @classmethod
    def setUpClass(cls):
        config_file = cls._get_path("../config.yaml")
        try:
            with open(config_file, "r") as config:
                config = yaml.load(config.read(), Loader=yaml.SafeLoader)

            cls.discord = DiscordImpl(bot_token=config['bottoken'],
                                      channel_id=config['channelid'],
                                      logger=TestLogger(),
                                      command=mock.MagicMock,
                                      status_callback=mock.MagicMock)
            while not cls.discord.is_running:
                time.sleep(1)
        except:
            fail("To test discord bot posting, you need to create a file "
                 "called config.yaml in the root directory with your bot "
                 "details. NEVER COMMIT THIS FILE.")

    @classmethod
    def tearDownClass(cls):
        cls.discord.shutdown_discord()

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

    @staticmethod
    def _get_path(filename):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
