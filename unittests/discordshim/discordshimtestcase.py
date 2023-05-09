import logging
import os
import random
import threading

import yaml
from signal import SIGKILL
import socket
from unittest import TestCase

from _pytest.outcomes import fail

from octoprint_discordshim.discordshim import DiscordShim


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


def discordshim_function(bot_token: str, channel_id: str, port: int):
    os.environ['BOT_TOKEN'] = bot_token
    os.environ['CHANNEL_ID'] = channel_id
    os.environ['DISCORD_LINK_PORT'] = str(port)

    DiscordShim()

class DiscordShimTestCase(TestCase):
    client: socket
    thread: threading.Thread
    snapshot_bytes: bytes = []

    @classmethod
    def setUpClass(cls):
        config_file = cls._get_path("../../config.yaml")
        with open(config_file) as f:
            data = yaml.load(f)
            bot_token = data['bottoken']
            channel_id = data['channelid']
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.settimeout(10)
            server.bind(('127.0.0.1', 0))
            sock_details = server.getsockname()
            server.listen()

            cls.thread = threading.Thread(target=discordshim_function, args=(bot_token, channel_id, sock_details[1]))
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
        cls.client.close()

    @staticmethod
    def _get_path(filename):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
