from __future__ import unicode_literals

import io
import time

import socket
from asyncio import Event

from mock import mock
from discord import Embed, File

from octoprint_discordremote.discordimpl import DiscordImpl
from octoprint_discordshim.embedbuilder import EmbedBuilder
from unittests.discordremotetestcase import DiscordRemoteTestCase

import asyncio
import pytest

pytest_plugins = ('pytest_asyncio',)

async def update_event(event: DiscordImpl.AsyncIOEventWrapper):
    await asyncio.sleep(1)
    event.set_event(Event())
    await asyncio.sleep(3)
    event.set()

@pytest.mark.asyncio
async def testAsyncIOEventWrapper():
    event = DiscordImpl.AsyncIOEventWrapper()
    event.event = None
    future = event.wait()
    await update_event(event)
    await future

class TestSend(DiscordRemoteTestCase):
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
