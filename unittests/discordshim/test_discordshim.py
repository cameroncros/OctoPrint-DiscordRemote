import time

from octoprint_discordremote.responsebuilder import embed_simple, COLOR_INFO
from proto.messages_pb2 import ProtoFile, TextField, Response
from unittests.discordshim.discordshimtestcase import DiscordShimTestCase


class TestDiscordShim(DiscordShimTestCase):

    def test_send_minimal_embed(self):
        response = embed_simple(author="", description="description")
        data = response.SerializeToString()
        self.client.send(len(data).to_bytes(4, byteorder='little'))
        self.client.send(data)

    def test_send_complete_embed(self):
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
