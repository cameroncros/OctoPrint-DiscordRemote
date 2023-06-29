from octoprint_discordremote.responsebuilder import success_embed, COLOR_SUCCESS, error_embed, COLOR_ERROR, info_embed, \
    COLOR_INFO
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
