from unittest import TestCase
import os
from discord import Embed


class DiscordRemoteTestCase(TestCase):
    def assertBasicEmbed(self, embed: Embed, title, description, color, author):
        if title is not None:
            self.assertEqual(title, embed.title)
        if description is not None:
            self.assertEqual(description, embed.description)
        if color is not None:
            self.assertEqual(color, embed.color.value)
        self.assertIsNotNone(embed.timestamp)
        self.assertEqual(0, len(embed.fields))
        if author is not None:
            self.assertEqual(author, embed.author.name)

    def _get_path(self, filename):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
