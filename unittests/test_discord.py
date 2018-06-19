import os

import logging
import time

import socket
import unittest
from mock import mock
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
                                           logger=logging.getLogger(),
                                           command=None)
            time.sleep(5)
        except:
            self.fail("To test discord bot posting, you need to create a file "
                      "called config.yaml in the root directory with your bot "
                      "details. NEVER COMMIT THIS FILE.")

    def tearDown(self):
        self.discord.shutdown_discord()

    def test_send(self):
        # Should result in 3 messages. 1 text only, 1 text+img and 1 image only
        self.assertTrue(self.discord.send("Test message 1"))
        with open("unittests/test_pattern.png", "rb") as file:
            self.assertTrue(self.discord.send("Test message 2", file))
            self.assertTrue(self.discord.send(None, file))

    @unittest.skipIf("LONG_TEST" not in os.environ,
                     "Not running long test")
    def test_reconnect(self):
        # Wait til connected fully
        while self.discord.session_id is None:
            time.sleep(0.001)

        print("Connected and authenticated: %s" % self.discord.session_id)

        orig_send_resume = self.discord.send_resume
        self.discord.send_resume = mock.Mock()
        self.discord.send_resume.side_effect = orig_send_resume

        while self.discord.restart_event.is_set():
            time.sleep(0.001)

        self.discord.restart_event.set()

        resume_called_count = 0
        for i in range(0, 1100):
            self.discord.send_resume.reset_mock()
            self.discord.restart_event.set()
            time.sleep(60)
            # Wait til resume is called
            if self.discord.send_resume.called:
                resume_called_count += 1
                print("Resumed: %i" % i)

        print("Total Successful Resumes: %i" % resume_called_count)
