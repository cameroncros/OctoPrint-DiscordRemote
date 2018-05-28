import mock
from unittest import TestCase

from octoprint_discordremote import DiscordRemotePlugin


def mock_global_get_boolean(array):
    return {
        str(['webcam', 'flipV']): False,
        str(['webcam', 'flipH']): False,
        str(['webcam', 'rotate90']): False,
    }[str(array)]


class TestCommand(TestCase):
    def test_plugin_get_snapshot_http(self):
        plugin = DiscordRemotePlugin()
        plugin._settings = mock.Mock()
        plugin._settings.global_get = mock.Mock()
        plugin._settings.global_get.return_value = "http://ValidSnapshot"
        plugin._settings.global_get_boolean = mock_global_get_boolean
        plugin._logger = mock.Mock()

        with open("unittests/test_pattern.png", "rb") as f:
            file_data = f.read()

        with mock.patch("requests.get") as mock_requests_get:
            mock_requests_get.return_value = mock.Mock()
            mock_requests_get.return_value.content = file_data

            snapshot = plugin.get_snapshot()

            self.assertIsNotNone(snapshot)
            snapshot_data = snapshot.read()
            self.assertEqual(len(file_data),len(snapshot_data))
            self.assertEqual([file_data], [snapshot_data])

    def test_plugin_get_snapshot_file(self):
        plugin = DiscordRemotePlugin()
        plugin._settings = mock.Mock()
        plugin._settings.global_get = mock.Mock()
        plugin._settings.global_get.return_value = "file://unittests/test_pattern.png"
        plugin._settings.global_get_boolean = mock_global_get_boolean
        plugin._logger = mock.Mock()

        with open("unittests/test_pattern.png", "rb") as f:
            file_data = f.read()

        snapshot = plugin.get_snapshot()

        self.assertIsNotNone(snapshot)
        snapshot_data = snapshot.read()
        self.assertEqual(len(file_data), len(snapshot_data))
        self.assertEqual([file_data], [snapshot_data])
