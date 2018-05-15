import mock
from unittest import TestCase

from octoprint_octorant import OctorantPlugin

def mock_global_get(array):
	return {
		str(['webcam', 'snapshot']): "http://ValidSnapshot",
		str(['webcam', 'flipV']): False,
		str(['webcam', 'flipH']): False,
		str(['webcam', 'rotate90']): False,
	}[str(array)]


class TestCommand(TestCase):
	def test_plugin_get_snapshot(self):
		plugin = OctorantPlugin()
		plugin._settings = mock.Mock()
		plugin._settings.global_get = mock_global_get
		plugin._settings.global_get_boolean = mock_global_get
		plugin._logger = mock.Mock()

		with open("unittests/test_pattern.png", "rb") as file:
			file_data = file.read()

		with mock.patch("requests.get") as mock_requests_get:
			mock_requests_get.return_value = mock.Mock()
			mock_requests_get.return_value.content = file_data

			snapshot = plugin.get_snapshot()

			self.assertIsNotNone(snapshot)
			snapshot_data = snapshot.read()
			self.assertEqual(len(file_data),len(snapshot_data))
			self.assertEqual([file_data], [snapshot_data])
