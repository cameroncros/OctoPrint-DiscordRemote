import logging
import time
from unittest import TestCase

import yaml

from octoprint_discordremote.discord import send, configure_discord


class TestSend(TestCase):
    def setUp(self):
        config_file = "config.yaml"
        try:
            with open(config_file, "r") as config:
                config = yaml.load(config.read())
            configure_discord(logging,
                              p_bot_token=config['bottoken'],
                              p_channel_id=config['channelid'],
                              p_command=None)
            time.sleep(5)
        except:
            self.fail("To test discord bot posting, you need to create a file "
                      "called config.yaml in the root directory with your bot "
                      "details. NEVER COMMIT THIS FILE.")

    def test_send(self):
        # Should result in 3 messages. 1 text only, 1 text+img and 1 image only
        self.assertTrue(send("Test message 1"))
        with open("unittests/test_pattern.png", "rb") as file:
            self.assertTrue(send("Test message 2", file))
            self.assertTrue(send(None, file))
