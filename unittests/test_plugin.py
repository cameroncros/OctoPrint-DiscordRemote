import mock

from octoprint_discordremote import DiscordRemotePlugin
from unittests.discordremotetestcase import DiscordRemoteTestCase


def mock_global_get_boolean(array):
    return {
        unicode(['webcam', 'flipV']): False,
        unicode(['webcam', 'flipH']): False,
        unicode(['webcam', 'rotate90']): False,
    }[unicode(array)]


class TestCommand(DiscordRemoteTestCase):
    def test_plugin_get_snapshot_http(self):
        plugin = DiscordRemotePlugin()
        plugin._settings = mock.Mock()
        plugin._settings.global_get = mock.Mock()
        plugin._settings.global_get.return_value = "http://ValidSnapshot"
        plugin._settings.global_get_boolean = mock_global_get_boolean
        plugin._logger = mock.Mock()

        with open(self._get_path('test_pattern.png'), "rb") as f:
            file_data = f.read()

        with mock.patch("requests.get") as mock_requests_get:
            mock_requests_get.return_value = mock.Mock()
            mock_requests_get.return_value.content = file_data

            snapshots = plugin.get_snapshot()

            self.assertIsNotNone(snapshots)
            self.assertEqual(1, len(snapshots))
            snapshot = snapshots[0]
            self.assertEqual(2, len(snapshot))
            self.assertEqual("snapshot.png", snapshot[0])
            snapshot_data = snapshot[1].read()
            self.assertEqual(len(file_data), len(snapshot_data))
            self.assertEqual([file_data], [snapshot_data])

    def test_plugin_get_snapshot_file(self):
        plugin = DiscordRemotePlugin()
        plugin._settings = mock.Mock()
        plugin._settings.global_get = mock.Mock()
        plugin._settings.global_get.return_value = "file://" + self._get_path('test_pattern.png')
        plugin._settings.global_get_boolean = mock_global_get_boolean
        plugin._logger = mock.Mock()

        with open(self._get_path('test_pattern.png'), "rb") as f:
            file_data = f.read()

        snapshots = plugin.get_snapshot()

        self.assertIsNotNone(snapshots)
        self.assertEqual(1, len(snapshots))
        snapshot = snapshots[0]
        self.assertEqual(2, len(snapshot))
        self.assertEqual("snapshot.png", snapshot[0])
        snapshot_data = snapshot[1].read()
        self.assertEqual(len(file_data), len(snapshot_data))
        self.assertEqual([file_data], [snapshot_data])

    def test_plugin_get_printer_name(self):
        plugin = DiscordRemotePlugin()
        plugin._settings = mock.Mock()
        plugin._settings.global_get = mock.Mock()
        plugin._settings.global_get.return_value = "DiscordBot"
        self.assertEqual(plugin._settings.global_get.return_value, plugin.get_printer_name())

        plugin._settings.global_get.return_value = None
        self.assertEqual("OctoPrint", plugin.get_printer_name())

    def test_get_print_time_spent(self):
        plugin = DiscordRemotePlugin()
        plugin._printer = mock.Mock()
        plugin._printer.get_current_data = mock.Mock()

        plugin._printer.get_current_data.return_value = {}
        self.assertEqual('Unknown', plugin.get_print_time_spent())

        plugin._printer.get_current_data.return_value = {'progress': {}}
        self.assertEqual('Unknown', plugin.get_print_time_spent())

        plugin._printer.get_current_data.return_value = {'progress': {'printTime': None}}
        self.assertEqual('Unknown', plugin.get_print_time_remaining())

        plugin._printer.get_current_data.return_value = {'progress': {'printTime': 1234}}
        self.assertEqual('20 minutes and 34 seconds', plugin.get_print_time_spent())

    def test_get_print_time_remaining(self):
        plugin = DiscordRemotePlugin()
        plugin._printer = mock.Mock()
        plugin._printer.get_current_data = mock.Mock()

        plugin._printer.get_current_data.return_value = {}
        self.assertEqual('Unknown', plugin.get_print_time_remaining())

        plugin._printer.get_current_data.return_value = {'progress': {}}
        self.assertEqual('Unknown', plugin.get_print_time_remaining())

        plugin._printer.get_current_data.return_value = {'progress': {'printTimeLeft': None}}
        self.assertEqual('Unknown', plugin.get_print_time_remaining())

        plugin._printer.get_current_data.return_value = {'progress': {'printTimeLeft': 1234}}
        self.assertEqual('20 minutes and 34 seconds', plugin.get_print_time_remaining())



