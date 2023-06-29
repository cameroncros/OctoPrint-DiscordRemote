from __future__ import unicode_literals

import time

from octoprint_discordremote import EmbedContent, Response
from unittests.mockdiscordtestcase import MockDiscordTestCase


class TestDiscordLink(MockDiscordTestCase):
    def test_send(self):
        builder = EmbedContent()
        builder.title = "Test title"
        builder.description = "No snapshot"
        self.discord.send(messages=Response(embed=builder))

        # Read settings
        length_bytes = self.client.recv(4)
        length = int.from_bytes(length_bytes, byteorder='little')
        _ = self.client.recv(length)

        # Read message
        length_bytes = self.client.recv(4)
        length = int.from_bytes(length_bytes, byteorder='little')
        self.assertEqual(len(Response(embed=builder).SerializeToString()), length)

        sent_bytes = self.client.recv(length)
        self.assertEqual(Response(embed=builder).SerializeToString(), sent_bytes)
