import logging
import time

import socket
from unittest import TestCase

import yaml

from octoprint_discordremote.discord import Discord


class TestSend(TestCase):
    def setUp(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
        except Exception as e:
            self.fail("Can't be tested without an internet connection")
        finally:
            s.close()

        config_file = "config.yaml"
        try:
            with open(config_file, "r") as config:
                config = yaml.load(config.read())
            self.discord = Discord()
            self.discord.configure_discord(bot_token=config['bottoken'],
                                           channel_id=config['channelid'],
                                           logger=logging,
                                           command=None)
            time.sleep(5)
        except:
            self.fail("To test discord bot posting, you need to create a file "
                      "called config.yaml in the root directory with your bot "
                      "details. NEVER COMMIT THIS FILE.")

    def tearDown(self):
        # self.assertTrue(self.discord.stop_listener())
        pass

    def test_send(self):
        # Should result in 3 messages. 1 text only, 1 text+img and 1 image only
        self.assertTrue(self.discord.send("Test message 1"))
        with open("unittests/test_pattern.png", "rb") as file:
            self.assertTrue(self.discord.send("Test message 2", file))
            self.assertTrue(self.discord.send(None, file))
