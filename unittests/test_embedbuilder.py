import time

import logging
import os
import yaml

from octoprint_discordremote import Discord
from octoprint_discordremote.embedbuilder import EmbedBuilder, MAX_TITLE, success_embed, error_embed, \
    info_embed, MAX_VALUE, MAX_NUM_FIELDS, COLOR_INFO, COLOR_SUCCESS, COLOR_ERROR
from unittests.discordremotetestcase import DiscordRemoteTestCase


class TestEmbedBuilder(DiscordRemoteTestCase):

    def setUp(self):
        if "NET_TEST" in os.environ:
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
        else:
            print("'NET_TEST' not in os.environ - Not running network test")

    def tearDown(self):
        if "NET_TEST" in os.environ:
            self.discord.shutdown_discord()

    def test_embedbuilder(self):
        # Success
        builder = EmbedBuilder()
        builder.set_title("Test Title")
        builder.set_description("This is a description")
        builder.set_color(COLOR_INFO)
        for i in range(0, 30):
            builder.add_field("a" * MAX_TITLE,
                              "b" * MAX_VALUE)
        embeds = builder.get_embeds()
        self.assertEqual(8, len(embeds))

        first_embed = embeds[0].get_embed()
        self.assertEqual("Test Title", first_embed['title'])
        self.assertEqual("This is a description", first_embed['description'])
        for embed in embeds:
            embed_obj = embed.get_embed()
            self.assertEqual(COLOR_INFO, embed_obj['color'])
            self.assertIsNotNone(embed_obj['timestamp'])
            self.assertLessEqual(len(embed_obj['fields']), MAX_NUM_FIELDS)
            for field in embed_obj['fields']:
                self.assertEqual("a" * MAX_TITLE, field['name'])
                self.assertEqual("b" * MAX_VALUE, field['value'])

        if "NET_TEST" in os.environ:
            self.assertTrue(self.discord.send(embeds=embeds))

    def test_success_embed(self):
        embeds = success_embed(author="OctoPrint", title="title", description="description")

        self.assertBasicEmbed(embeds,
                              author="OctoPrint",
                              title="title",
                              description="description",
                              color=COLOR_SUCCESS)

        if "NET_TEST" in os.environ:
            self.assertTrue(self.discord.send(embeds=embeds))

    def test_error_embed(self):
        embeds = error_embed(author="OctoPrint", title="title", description="description")

        self.assertBasicEmbed(embeds,
                              author="OctoPrint",
                              title="title",
                              description="description",
                              color=COLOR_ERROR)

        if "NET_TEST" in os.environ:
            self.assertTrue(self.discord.send(embeds=embeds))

    def test_info_embed(self):
        embeds = info_embed(author="OctoPrint", title="title", description="description")

        self.assertBasicEmbed(embeds,
                              author="OctoPrint",
                              title="title",
                              description="description",
                              color=COLOR_INFO)

        if "NET_TEST" in os.environ:
            self.assertTrue(self.discord.send(embeds=embeds))
