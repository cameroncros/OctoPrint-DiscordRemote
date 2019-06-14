from unittest import TestCase
import os

class DiscordRemoteTestCase(TestCase):
    def assertBasicEmbed(self, embeds, title, description, color, author):
        self.assertEqual(1, len(embeds))
        first_embed = embeds[0].get_embed()
        self.assertEqual(title, first_embed['title'])
        self.assertEqual(description, first_embed['description'])
        self.assertEqual(color, first_embed['color'])
        self.assertIsNotNone(first_embed['timestamp'])
        self.assertEqual(0, len(first_embed['fields']))
        self.assertEqual(author, first_embed['author']['name'])

    def _get_path(self, filename):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
