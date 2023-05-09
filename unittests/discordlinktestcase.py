import logging
import os
from typing import Optional
from unittest import TestCase

import yaml
from _pytest.outcomes import fail

from octoprint_discordremote import DiscordLink


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
    discord: Optional[DiscordLink] = None
    snapshot_bytes: bytes = []

    @classmethod
    def setUpClass(cls):
        config_file = cls._get_path("../config.yaml")
        try:
            with open(config_file, "r") as config:
                config = yaml.load(config.read(), Loader=yaml.SafeLoader)

            cls.discord = DiscordLink(bot_token=config['bottoken'],
                                      channel_id=config['channelid'])
        except:
            fail("To test discord bot posting, you need to create a file "
                 "called config.yaml in the root directory with your bot "
                 "details. NEVER COMMIT THIS FILE.")

        with open(cls._get_path("test_pattern.png"), "rb") as f:
            cls.snapshot_bytes = f.read()

    @classmethod
    def tearDownClass(cls):
        cls.discord.shutdown_discord()

    @staticmethod
    def _get_path(filename):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
