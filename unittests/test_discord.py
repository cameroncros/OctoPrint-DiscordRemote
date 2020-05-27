from __future__ import unicode_literals

import time

import logging
import os
import socket
import unittest

import six
import yaml
from mock import mock

from octoprint_discordremote.discord import Discord
from octoprint_discordremote.embedbuilder import EmbedBuilder, upload_file, DISCORD_MAX_FILE_SIZE
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
                                               channel_ids=config['channelid'],
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

        self.assertTrue(self.discord._dispatch_message(embed=builder.get_embeds()[0]))

        with open(self._get_path("test_pattern.png"), "rb") as f:
            builder.set_description("With snapshot")
            builder.set_image(("snapshot.png", f))
            self.assertTrue(self.discord._dispatch_message(embed=builder.get_embeds()[0]))

            f.seek(0)
            self.assertTrue(self.discord._dispatch_message(snapshot=("snapshot.png", f)))

    def test_send(self):
        self.discord._dispatch_message = mock.Mock()
        mock_snapshot = mock.Mock()
        mock_embed = mock.Mock()
        self.assertTrue(self.discord.send(snapshots=[mock_snapshot], embeds=[mock_embed]))

        self.assertEqual(2, self.discord._dispatch_message.call_count)
        calls = [mock.call(snapshot=mock_snapshot),
                 mock.call(embed=mock_embed)]
        self.discord._dispatch_message.assert_has_calls(calls=calls)

        large_file_path = self._get_path("large_file_temp")
        with open(large_file_path, 'w') as f:
            for i in range(0, DISCORD_MAX_FILE_SIZE):
                f.write(str(i))

        embeds = upload_file(large_file_path)
        self.discord.send(embeds=embeds)

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

        orig_handle_invalid = self.discord.handle_invalid_session
        self.discord.handle_invalid_session = mock.Mock()
        self.discord.handle_invalid_session.side_effect = orig_handle_invalid

        while self.discord.restart_event.is_set():
            time.sleep(0.001)

        self.discord.web_socket = None
        self.discord.restart_event.set()

        resume_succeeded = 0
        for i in range(0, 1100):
            self.discord.send_resume.reset_mock()
            while self.discord.restart_event.is_set():
                time.sleep(1)
            self.discord.restart_event.set()
            # Wait til resume is called
            while not self.discord.send_resume.called:
                time.sleep(1)
            self.discord.send_resume.reset_mock()

            # Check if invalid session occurred. Might not receive it til the next iteration.
            if self.discord.handle_invalid_session.called:
                resume_succeeded -= 1
                self.discord.handle_invalid_session.reset_mock()

            resume_succeeded += 1
            print("Resumed: %i, Succeeded: %i" % (i, resume_succeeded))

        print("Total Successful Resumes: %i" % resume_succeeded)
