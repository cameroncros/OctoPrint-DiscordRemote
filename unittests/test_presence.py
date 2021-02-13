from mock import MagicMock

from octoprint_discordremote import Presence
from unittests.discordremotetestcase import DiscordRemoteTestCase


class TestPresence(DiscordRemoteTestCase):

    def setUp(self):
        self.presence = Presence()

    def test_generate_status(self):
        self.presence.plugin = MagicMock()
        self.presence.plugin.get_printer.return_value.is_operational.return_value = True
        self.presence.plugin.get_printer.return_value.is_printing.return_value = True
        self.presence.plugin.get_printer.return_value.get_current_data.return_value = {
            'job': {'file' : {'name' : 'filename'}},
            'progress': {'completion': 12.4567899}
        }
        self.assertEqual("Printing filename - 12.45%", self.presence.generate_status())

        self.presence.plugin.get_printer.return_value.is_printing.return_value = False
        self.assertEqual("Idle.", self.presence.generate_status())

        self.presence.plugin.get_printer.return_value.is_operational.return_value = False
        self.assertEqual("Not operational.", self.presence.generate_status())
