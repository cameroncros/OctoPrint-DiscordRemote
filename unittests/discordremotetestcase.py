from unittest import TestCase


class DiscordRemoteTestCase(TestCase):
    def assertBasicEmbed(self, embeds, title, description, color):
        self.assertEqual(1, len(embeds))
        first_embed = embeds[0].get_embed()
        self.assertEqual(title, first_embed['title'])
        self.assertEqual(description, first_embed['description'])
        self.assertEqual(color, first_embed['color'])
        self.assertIsNotNone(first_embed['timestamp'])
        self.assertEqual(0, len(first_embed['fields']))
