from __future__ import unicode_literals

import io
import time

import socket

from mock import mock
from discord import Embed, File

from unittests.discordlinktestcase import DiscordLinkTestCase

pytest_plugins = ('pytest_asyncio',)

class TestSend(DiscordLinkTestCase):
    def test_dispatch(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
        time.sleep(1)
        self.assertTrue(self.discord.process_queue.is_set())
        while self.discord.process_queue.is_set():
            time.sleep(1)


    def test_send(self):
        real_send_messages = self.discord.send_messages
        self.discord.send_messages = mock.AsyncMock()
        real_process_message_queue = self.discord.process_message_queue
        self.discord.process_message_queue = mock.AsyncMock()

        mock_snapshot = mock.Mock(spec=io.IOBase)
        mock_embed = mock.Mock(spec=Embed)
        self.discord.send(messages=[(mock_embed, mock_snapshot)])
        self.assertIn([(mock_embed, mock_snapshot)], self.discord.message_queue)
        self.assertTrue(self.discord.process_queue.is_set())

        self.discord.send_messages = real_send_messages
        self.discord.process_message_queue = real_process_message_queue
