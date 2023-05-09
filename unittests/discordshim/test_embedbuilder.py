# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
import time

import os
import zipfile

from octoprint_discordremote.responsebuilder import COLOR_INFO
from octoprint_discordshim.embedbuilder import EmbedBuilder, MAX_TITLE, MAX_VALUE, MAX_NUM_FIELDS, upload_file, \
    DISCORD_MAX_FILE_SIZE
from discordshimtestcase import DiscordShimTestCase


class TestEmbedBuilder(DiscordShimTestCase):

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

        self.discord.send(messages=messages)

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

        self.discord.send(messages=messages)
        self.assertTrue(self.discord.process_queue.is_set())
        while self.discord.process_queue.is_set():
            time.sleep(1)

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
                self.assertEqual("large_file_temp.zip.%.03i" % i, snapshot.filename)
                snapshot.fp.seek(0)
                data = snapshot.fp.read()
                self.assertGreater(len(data), 0)
                self.assertLessEqual(len(data), DISCORD_MAX_FILE_SIZE)
                f.write(data)
                i += 1

        with zipfile.ZipFile("rebuilt.zip", 'r') as zip_file:
            with open(large_file_path, 'rb') as f:
                self.assertEqual(f.read(), zip_file.read("large_file_temp"))

        os.remove("rebuilt.zip")
        os.remove(large_file_path)
