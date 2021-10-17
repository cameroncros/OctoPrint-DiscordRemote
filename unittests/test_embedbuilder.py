# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
import time

import logging
import os
import zipfile

import yaml

from octoprint_discordremote import DiscordImpl
from octoprint_discordremote.embedbuilder import EmbedBuilder, MAX_TITLE, success_embed, error_embed, \
    info_embed, MAX_VALUE, MAX_NUM_FIELDS, COLOR_INFO, COLOR_SUCCESS, COLOR_ERROR, upload_file, DISCORD_MAX_FILE_SIZE
from unittests.discordremotetestcase import DiscordRemoteTestCase


class TestEmbedBuilder(DiscordRemoteTestCase):

    def setUp(self):
        if "NET_TEST" in os.environ:
            config_file = self._get_path("../config.yaml")
            try:
                with open(config_file, "r") as config:
                    config = yaml.load(config.read(), Loader=yaml.SafeLoader)
                self.discord = DiscordImpl()
                self.discord.configure_discord(bot_token=config['bottoken'],
                                               channel_id=config['channelid'],
                                               logger=logging.getLogger(),
                                               command=None)
                while True:
                    if self.discord.client.is_ready():
                        break

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
        messages = builder.get_embeds()
        self.assertEqual(8, len(messages))

        embed, snapshot = messages[0]
        self.assertEqual("Test Title", embed.title)
        self.assertEqual("This is a description", embed.description)
        for embed, snapshot in messages:
            self.assertEqual(COLOR_INFO, embed.color.value)
            self.assertIsNotNone(embed.timestamp)
            self.assertLessEqual(len(embed.fields), MAX_NUM_FIELDS)
            for field in embed.fields:
                self.assertEqual("a" * MAX_TITLE, field.name)
                self.assertEqual("b" * MAX_VALUE, field.value)

        if "NET_TEST" in os.environ:
            self.discord.send(messages=messages)

    def test_success_embed(self):
        messages = success_embed(author="OctoPrint", title="title", description="description")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertBasicEmbed(embed,
                              author="OctoPrint",
                              title="title",
                              description="description",
                              color=COLOR_SUCCESS)

        if "NET_TEST" in os.environ:
            self.discord.send(messages=(embed, snapshot))

    def test_error_embed(self):
        messages = error_embed(author="OctoPrint", title="title", description="description")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertBasicEmbed(embed,
                              author="OctoPrint",
                              title="title",
                              description="description",
                              color=COLOR_ERROR)

        if "NET_TEST" in os.environ:
            self.discord.send(messages=(embed, snapshot))

    def test_info_embed(self):
        messages = info_embed(author="OctoPrint", title="title", description="description")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertBasicEmbed(embed,
                              author="OctoPrint",
                              title="title",
                              description="description",
                              color=COLOR_INFO)

        if "NET_TEST" in os.environ:
            self.discord.send(messages=(embed, snapshot))

    def test_unicode_embed(self):
        teststr = "٩(-̮̮̃-̃)۶ ٩(●̮̮̃•̃)۶ ٩(͡๏̯͡๏)۶ ٩(-̮̮̃•̃)."
        embed_builder = EmbedBuilder()
        embed_builder.set_title(teststr)
        embed_builder.set_description(teststr)
        embed_builder.set_author(teststr)
        embed_builder.add_field(teststr, teststr)
        embeds = embed_builder.get_embeds()

        self.assertIsNotNone(embeds)

    def test_upload_file(self):
        small_file_path = self._get_path("test_pattern.png")
        messages = upload_file(small_file_path, "Author")
        self.assertIsNotNone(messages)
        if "NET_TEST" in os.environ:
            self.discord.send(messages=messages)
        self.assertEqual(2, len(messages))
        embed, snapshot = messages[0]
        self.assertBasicEmbed(embed,
                              author="Author",
                              color=COLOR_INFO,
                              title="Uploaded test_pattern.png",
                              description=None)

        embed, snapshot = messages[1]
        self.assertEqual(snapshot.filename, "test_pattern.png")
        with open(small_file_path, 'rb') as f:
            snapshot.fp.seek(0)
            self.assertEqual(f.read(), snapshot.fp.read())

        # create large file, that requires splitting
        large_file_path = self._get_path("large_file_temp")
        data = bytearray(1024)
        for i in range(1024):
            data[i] = i % 0xff
        data = bytes(data)
        with open(large_file_path, 'wb') as f:
            for i in range(0, int(round(DISCORD_MAX_FILE_SIZE / 1024 * 6))):
                f.write(data)

        messages = upload_file(large_file_path, author="Author")
        self.assertIsNotNone(messages)
        if "NET_TEST" in os.environ:
            self.discord.send(messages)
        self.assertEqual(8, len(messages))
        embed, snapshot = messages[0]
        self.assertBasicEmbed(embed,
                              author="Author",
                              color=COLOR_INFO,
                              title="Uploaded large_file_temp in 7 parts",
                              description=None)

        with open("rebuilt.zip", 'wb') as f:
            i = 1
            for embed, snapshot in messages[1:]:
                self.assertEquals("large_file_temp.zip.%.03i" % i, snapshot.filename)
                snapshot.fp.seek(0)
                data = snapshot.fp.read()
                self.assertGreater(len(data), 0)
                self.assertLessEqual(len(data), DISCORD_MAX_FILE_SIZE)
                f.write(data)
                i += 1

        with zipfile.ZipFile("rebuilt.zip", 'r') as zip_file:
            with open(large_file_path, 'rb') as f:
                self.assertEquals(f.read(), zip_file.read("large_file_temp"))

        os.remove("rebuilt.zip")
        os.remove(large_file_path)
