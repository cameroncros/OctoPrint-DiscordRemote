import os
import time
from base64 import b64encode
from unittest import skipIf
from unittest.mock import Mock

import mock
import octoprint
import yaml

from octoprint_discordremote import DiscordRemotePlugin
from unittests.mockdiscordtestcase import MockDiscordTestCase


def mock_global_get_boolean(array):
    return {
        u'webcam_flipV': False,
        u'webcam_flipH': False,
        u'webcam_rotate90': False,
    }[u"_".join(array)]


class TestPlugin(MockDiscordTestCase):
    def setUp(self):
        super().setUp()
        self.plugin = DiscordRemotePlugin()
        self.plugin._settings = mock.Mock()
        self.plugin._printer = mock.Mock()
        self.plugin._logger = mock.Mock()

    @skipIf(not hasattr(octoprint.plugin.types, "WebcamProviderPlugin"), "Camera API not supported")
    def test_plugin_get_snapshot_camera_api(self):
        with open(self._get_path('test_pattern.png'), "rb") as f:
            file_data = f.read()

        camera_mock = mock.MagicMock()
        self.plugin._plugin_manager = mock.MagicMock()
        self.plugin._plugin_manager.get_implementations.return_value = [camera_mock]

        self.plugin._settings = mock.MagicMock()
        self.plugin._settings.global_get.return_value = None

        configuration = mock.MagicMock()
        configuration.flipH = False
        configuration.flipV = False
        configuration.rotate90 = False

        camera_mock.get_webcam_configurations.return_value = [configuration]
        camera_mock.take_webcam_snapshot.return_value = [file_data]

        file = self.plugin.get_snapshot()

        self.assertEqual("snapshot.png", file.filename)
        self.assertEqual(len(file_data), len(file.data))
        self.assertEqual([file_data], [file.data])

    def test_plugin_get_snapshot_http(self):
        self.plugin._plugin_manager = mock.MagicMock()
        self.plugin._plugin_manager.get_implementations.return_value = []

        self.plugin._settings.global_get = mock.Mock()
        self.plugin._settings.global_get.return_value = "http://ValidSnapshot"
        self.plugin._settings.global_get_boolean = mock_global_get_boolean

        with open(self._get_path('test_pattern.png'), "rb") as f:
            file_data = f.read()

        with mock.patch("requests.get") as mock_requests_get:
            mock_requests_get.return_value = mock.Mock()
            mock_requests_get.return_value.content = file_data

            file = self.plugin.get_snapshot()

            self.assertEqual("snapshot.png", file.filename)
            self.assertEqual(len(file_data), len(file.data))
            self.assertEqual([file_data], [file.data])

    def test_plugin_get_snapshot_file(self):
        self.plugin._plugin_manager = mock.MagicMock()
        self.plugin._plugin_manager.get_implementations.return_value = []

        self.plugin._settings.global_get = mock.Mock()
        self.plugin._settings.global_get.return_value = "file://" + self._get_path('test_pattern.png')
        self.plugin._settings.global_get_boolean = mock_global_get_boolean

        with open(self._get_path('test_pattern.png'), "rb") as f:
            file_data = f.read()

        file = self.plugin.get_snapshot()

        self.assertEqual("snapshot.png", file.filename)
        self.assertEqual(len(file_data), len(file.data))
        self.assertEqual([file_data], [file.data])

    def test_plugin_get_printer_name(self):
        self.plugin._settings.global_get = mock.Mock()
        self.plugin._settings.global_get.return_value = "DiscordBot"
        self.assertEqual(self.plugin._settings.global_get.return_value,
                         self.plugin.get_printer_name())

        self.plugin._settings.global_get.return_value = None
        self.assertEqual("OctoPrint",
                         self.plugin.get_printer_name())

    def test_get_print_time_spent(self):
        self.plugin._printer.get_current_data = mock.Mock()

        self.plugin._printer.get_current_data.return_value = {}
        self.assertEqual('Unknown', self.plugin.get_print_time_spent())

        self.plugin._printer.get_current_data.return_value = {'progress': {}}
        self.assertEqual('Unknown', self.plugin.get_print_time_spent())

        self.plugin._printer.get_current_data.return_value = {'progress': {'printTime': None}}
        self.assertEqual('Unknown', self.plugin.get_print_time_remaining())

        self.plugin._printer.get_current_data.return_value = {'progress': {'printTime': 1234}}
        self.assertEqual('20 minutes and 34 seconds', self.plugin.get_print_time_spent())

    def test_get_print_time_remaining(self):
        self.plugin._printer.get_current_data = mock.Mock()

        self.plugin._printer.get_current_data.return_value = {}
        self.assertEqual('Unknown', self.plugin.get_print_time_remaining())

        self.plugin._printer.get_current_data.return_value = {'progress': {}}
        self.assertEqual('Unknown', self.plugin.get_print_time_remaining())

        self.plugin._printer.get_current_data.return_value = {'progress': {'printTimeLeft': None}}
        self.assertEqual('Unknown', self.plugin.get_print_time_remaining())

        self.plugin._printer.get_current_data.return_value = {'progress': {'printTimeLeft': 1234}}
        self.assertEqual('20 minutes and 34 seconds', self.plugin.get_print_time_remaining())

    def test_unpack_message(self):
        with open(self._get_path('test_pattern.png'), "rb") as f:
            file_data = f.read()

        base64_data = b64encode(file_data)
        data = {
            'title': 'title',
            'author': 'author',
            'description': 'description',
            'color': 0xabcdef,
            'image': base64_data,
            'imagename': "snapshot.jpg"
        }

        self.plugin.discord = mock.Mock()
        self.plugin.discord.send = mock.Mock()
        self.plugin.unpack_message(data)
        self.plugin.discord.send.assert_called()
