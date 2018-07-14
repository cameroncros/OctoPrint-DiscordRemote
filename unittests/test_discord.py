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
        config_file = "config.yaml"
        try:
            with open(config_file, "r") as config:
                config = yaml.load(config.read())
            self.discord = Discord()
            self.discord.configure_discord(bot_token=config['bottoken'],
                                           channel_id=config['channelid'],
                                           allowed_users="",
                                           logger=logging.getLogger(),
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

        # Should result in 3 messages. 1 text only, 1 text+img and 1 image only
        self.assertTrue(self.discord._dispatch_message("Test message 1"))
        with open("unittests/test_pattern.png", "rb") as f:
            self.assertTrue(self.discord._dispatch_message("Test message 2", f))
            self.assertTrue(self.discord._dispatch_message(None, f))

    def test_send(self):
        self.discord._dispatch_message = mock.Mock()

        with open("unittests/test_pattern.png", "rb") as f:
            short_str = "x" * 1998
            self.assertTrue(self.discord.send(short_str, f))
            self.discord._dispatch_message.assert_called_once_with(message="`%s`" % short_str, snapshot=f)
            self.discord._dispatch_message.reset_mock()

            # split_text() doesnt properly deal with lines over 1998 chars long.
            # Wont fix it til it comes up.
            long_str = (short_str + '\n') * 5
            self.assertTrue(self.discord.send(long_str, f))
            self.assertEqual(6 , self.discord._dispatch_message.call_count)
            self.discord._dispatch_message.reset_mock()

    @unittest.skipIf("LONG_TEST" not in os.environ,
                     "'LONG_TEST' not in os.environ - Not running long test")
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
