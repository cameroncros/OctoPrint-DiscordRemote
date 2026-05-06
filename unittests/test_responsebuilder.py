from octoprint_discordremote.responsebuilder import (
    COLOR_ERROR,
    COLOR_INFO,
    COLOR_SUCCESS,
    error_embed,
    info_embed,
    success_embed,
)
from unittests.mockdiscordtestcase import MockDiscordTestCase


class TestResponseBuilder(MockDiscordTestCase):
    def test_success_embed(self):
        response = success_embed(author="OctoPrint", title="title", description="description")
        self.validateResponse(response,
                              title="title",
                              description="description",
                              color=COLOR_SUCCESS)

        self.discord.send(messages=response)

    def test_error_embed(self):
        response = error_embed(author="OctoPrint", title="title", description="description")
        self.validateResponse(response,
                              title="title",
                              description="description",
                              color=COLOR_ERROR)

        self.discord.send(messages=response)

    def test_info_embed(self):
        response = info_embed(author="OctoPrint", title="title", description="description")
        self.validateResponse(response,
                              title="title",
                              description="description",
                              color=COLOR_INFO)

        self.discord.send(messages=response)
