import os
import time
from unittest import skipIf
from unittest.mock import Mock

from octoprint_discordremote import DiscordLink
from octoprint_discordremote.proto.messages_pb2 import ProtoFile, TextField, Response
from octoprint_discordremote.responsebuilder import embed_simple, COLOR_INFO
from octoprint_discordremote.discordshim.embedbuilder import DISCORD_MAX_FILE_SIZE
from unittests.livediscordtestcase import LiveDiscordTestCase


class TestDiscordShim(LiveDiscordTestCase):

    @skipIf('FAST_TEST' in os.environ, "Running fast tests, skipping")
    def test_send_minimal_embed(self):
        self.start_scraper()

        response = embed_simple(author="")
        data = response.SerializeToString()
        self.client.send(len(data).to_bytes(4, byteorder='little'))
        self.client.send(data)

        self.stop_scraper(waitformessages=1)

    @skipIf('FAST_TEST' in os.environ, "Running fast tests, skipping")
    def test_send_complete_embed(self):
        self.start_scraper()

        response = embed_simple(author="Author",
                                title="Title",
                                description="description",
                                color=COLOR_INFO,
                                snapshot=ProtoFile(data=self.snapshot_bytes, filename="snapshot.png"))
        response.embed.textfield.append(TextField(title="Title"))
        response.embed.textfield.append(TextField(text="Text"))
        data = response.SerializeToString()
        self.client.send(len(data).to_bytes(4, byteorder='little'))
        self.client.send(data)

        results = self.stop_scraper(waitformessages=1)
        self.assertIn("snapshot.png", results[0].embeds[0].image.url)

    @skipIf('FAST_TEST' in os.environ, "Running fast tests, skipping")
    def test_send_small_file(self):
        self.start_scraper()

        file = ProtoFile(data=b"Hello World", filename="Helloworld.txt")
        response = Response(file=file)
        data = response.SerializeToString()
        self.client.send(len(data).to_bytes(4, byteorder='little'))
        self.client.send(data)

        results = self.stop_scraper(waitformessages=2)
        self.assertIn("Helloworld.txt", results[0].embeds[0].title)
        self.assertIn("Helloworld.txt", results[1].attachments[0].filename)

    @skipIf('FAST_TEST' in os.environ, "Running fast tests, skipping")
    def test_send_large_file(self):
        self.start_scraper()

        data = bytearray(1024)
        for i in range(1024):
            data[i] = i % 0xff
        data = bytes(data)
        large_file_data = b''
        for i in range(0, int(round(DISCORD_MAX_FILE_SIZE / 1024 * 6))):
            large_file_data += data

        file = ProtoFile(data=large_file_data, filename="Helloworld.dat")
        response = Response(file=file)
        data = response.SerializeToString()
        self.client.send(len(data).to_bytes(4, byteorder='little'))
        self.client.send(data)

        results = self.stop_scraper(waitformessages=8)
        self.assertIn("Helloworld.dat", results[0].embeds[0].title)
        self.assertIn("Helloworld.dat.zip.001", results[1].attachments[0].filename)
        self.assertIn("Helloworld.dat.zip.002", results[2].attachments[0].filename)
        self.assertIn("Helloworld.dat.zip.003", results[3].attachments[0].filename)
        self.assertIn("Helloworld.dat.zip.004", results[4].attachments[0].filename)
        self.assertIn("Helloworld.dat.zip.005", results[5].attachments[0].filename)
        self.assertIn("Helloworld.dat.zip.006", results[6].attachments[0].filename)
        self.assertIn("Helloworld.dat.zip.007", results[7].attachments[0].filename)

    def test_respawn_killed(self):
        discord = DiscordLink(self.bot_token, Mock(), Mock())
        discord.start_discord()

        while discord.client is None:
            time.sleep(1)

        first_pid = discord.process.pid
        discord.process.kill()

        time.sleep(20)

        second_pid = discord.process.pid

        self.assertNotEquals(first_pid, second_pid)

        discord.shutdown_discord()

    @skipIf(True, "Works in development, but not for CI")
    def test_respawn_socket_closed(self):
        discord = DiscordLink(self.bot_token, Mock())
        discord.start_discord()

        while discord.client is None:
            time.sleep(1)

        first_pid = discord.process.pid

        self.assertIsNotNone(self.client)
        discord.client.close()

        time.sleep(20)

        second_pid = discord.process.pid

        self.assertNotEqual(first_pid, second_pid)

        discord.shutdown_discord()
