from __future__ import unicode_literals

import io
import time

import logging
import os
import socket
import unittest

import yaml
from mock import mock
from discord import Embed, File

from octoprint_discordremote.discord import Discord
from octoprint_discordremote.embedbuilder import EmbedBuilder
from unittests.discordremotetestcase import DiscordRemoteTestCase


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


class TestSend(DiscordRemoteTestCase):
    def setUp(self):
        self.discord = Discord()
        if "NET_TEST" in os.environ:
            config_file = self._get_path("../config.yaml")
            try:
                with open(config_file, "r") as config:
                    config = yaml.load(config.read(), Loader=yaml.SafeLoader)
                self.discord.configure_discord(bot_token=config['bottoken'],
                                               channel_id=config['channelid'],
                                               logger=TestLogger(),
                                               command=None)
                time.sleep(5)
            except:
                self.fail("To test discord bot posting, you need to create a file "
                          "called config.yaml in the root directory with your bot "
                          "details. NEVER COMMIT THIS FILE.")

    def tearDown(self):
        self.discord.shutdown_discord()

    @unittest.skipIf("NET_TEST" not in os.environ,
                     "'NET_TEST' not in os.environ - Not running network test")
    def test_dispatch(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
        except Exception as e:
            self.fail("Can't be tested without an internet connection")
        finally:
            s.close()

        # Should result in 3 messages, one embed, one embed with photo, and one photo.
        builder = EmbedBuilder()
        builder.set_title("Test title")
        builder.set_description("No snapshot")
        self.discord.send(messages=builder.get_embeds())

        with open(self._get_path("test_pattern.png"), "rb") as f:
            builder.set_description("With snapshot")
            builder.set_image(("snapshot.png", f))
            self.discord.send(messages=builder.get_embeds())

            f.seek(0)
            self.discord.send(messages=[(None, File(fp=f, filename="snapshot.png"))])

    @unittest.skipIf("NET_TEST" in os.environ,
                     "'NET_TEST' in os.environ - Not running test")
    def test_send(self):
        self.discord.send_messages = mock.AsyncMock()
        mock_snapshot = mock.Mock(spec=io.IOBase)
        mock_embed = mock.Mock(spec=Embed)
        self.discord.send(messages=[(mock_embed, mock_snapshot)])
        self.assertIn([(mock_embed, mock_snapshot)], self.discord.message_queue)
        self.assertTrue(self.discord.process_queue.is_set())
