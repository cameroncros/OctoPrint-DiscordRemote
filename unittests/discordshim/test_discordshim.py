import time

from octoprint_discordremote.responsebuilder import embed_simple, COLOR_INFO
from octoprint_discordremote.proto.messages_pb2 import ProtoFile, TextField
from unittests.discordshim.discordshimtestcase import DiscordShimTestCase


class TestDiscordShim(DiscordShimTestCase):

    def test_send_minimal_embed(self):
        self.start_scraper()

        response = embed_simple(author="")
        data = response.SerializeToString()
        self.client.send(len(data).to_bytes(4, byteorder='little'))
        self.client.send(data)

        results = self.stop_scraper()
        self.assertEqual(1, len(results))
        self.assertNotIn("snapshot.png", results[0])

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

        results = self.stop_scraper()
        self.assertEqual(1, len(results))
        self.assertIn("snapshot.png", results[0])
