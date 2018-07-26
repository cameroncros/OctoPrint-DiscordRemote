import os
import humanfriendly
from unittest import TestCase

import mock

from octoprint_discordremote import Command
from octoprint_discordremote.embedbuilder import COLOR_INFO, COLOR_ERROR, COLOR_SUCCESS

file_list = {'local': {
    u'folder1': {'name': u'folder1', 'path': u'folder1', 'size': 6530L, 'type': 'folder', 'typePath': ['folder'],
                 'display': u'folder1',
                 'children': {
                     u'test.gcode': {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'name': u'test.gcode',
                                     'typePath': ['machinecode', 'gcode'], 'analysis': {
                             'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None,
                                              'minZ': None}, 'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
                             'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'date': 1525822075,
                                     'path': u'folder1/test.gcode', 'type': 'machinecode', 'display': u'test.gcode',
                                     'size': 6530L}
                 }},
    u'test.gcode': {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'name': u'test.gcode',
                    'typePath': ['machinecode', 'gcode'], 'analysis': {
            'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None,
                             'minZ': None}, 'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
            'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'date': 1525822021,
                    'path': u'test.gcode', 'type': 'machinecode', 'display': u'test.gcode',
                    'size': 6530L}}}

flatten_file_list = [
    {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'location': 'local', 'name': u'test.gcode', 'date': 1525822075,
     'path': u'folder1/test.gcode', 'size': 6530L, 'type': 'machinecode', 'typePath': ['machinecode', 'gcode'],
     'analysis': {'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None, 'minZ': None},
                  'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
                  'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'display': u'test.gcode'},
    {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'location': 'local', 'name': u'test.gcode', 'date': 1525822021,
     'path': u'/test.gcode', 'size': 6530L, 'type': 'machinecode', 'typePath': ['machinecode', 'gcode'],
     'analysis': {'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None, 'minZ': None},
                  'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
                  'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'display': u'test.gcode'}]


class TestCommand(TestCase):
    _file_manager = mock.Mock()
    _settings = mock.Mock()
    _printer = mock.Mock()
    _plugin_manager = mock.Mock()

    def get_file_manager(self):
        return self._file_manager

    def get_settings(self):
        return self._settings

    def get_printer(self):
        return self._printer

    def get_plugin_manager(self):
        return self._plugin_manager

    def setUp(self):
        self.command = Command(self)

    def _validate_embeds(self, embeds, color):
        self.assertIsNotNone(embeds)
        self.assertGreaterEqual(1, len(embeds))
        for embed in embeds:
            embed = embed.get_embed()
            self.assertIn('color', embed)
            self.assertEqual(color, embed['color'])
            self.assertIn('timestamp', embed)

    def _validate_simple_embed(self, embeds, color, title=None, description=None):
        self.assertIsNotNone(embeds)
        self.assertEqual(1, len(embeds))
        embed = embeds[0].get_embed()

        self.assertIn('color', embed)
        self.assertEqual(color, embed['color'])
        self.assertIn('timestamp', embed)

        if title:
            self.assertIn('title', embed)
            self.assertEqual(title, embed['title'])

        if description:
            self.assertIn('description', embed)
            self.assertEqual(description, embed['description'])

    def test_parse_command_list(self):
        # Success
        self.get_file_manager().list_files = mock.Mock()
        self.get_file_manager().list_files.return_value = file_list
        snapshots, embeds = self.command.parse_command("/files")
        self.get_file_manager().list_files.assert_called_once()
        self.assertIsNone(snapshots)

        message = ""
        for embed in embeds:
            message += str(embed)
        print(message)

        self._validate_embeds(embeds, COLOR_INFO)

    def test_parse_command_print(self):
        # FAIL: Printer not ready
        self.get_printer().is_ready = mock.Mock()
        self.get_printer().is_ready.return_value = False
        snapshots, embeds = self.command.parse_command("/print test.gcode")
        self.get_printer().is_ready.assert_called_once()
        self._validate_simple_embed(embeds, COLOR_ERROR, title="Printer is not ready")
        self.assertIsNone(snapshots)
        # TODO

        # Success: Printer ready
        # TODO: Mock and validate the print started
        self.command.get_flat_file_list = mock.Mock()
        self.command.get_flat_file_list.return_value = flatten_file_list
        self.get_printer().is_ready = mock.Mock()
        self.get_printer().is_ready.return_value = True
        snapshots, embeds = self.command.parse_command("/print test.gcode")
        self.get_printer().is_ready.assert_called_once()

        self._validate_simple_embed(embeds,
                                    COLOR_SUCCESS,
                                    title="Successfully started print",
                                    description="folder1/test.gcode")
        self.assertIsNone(snapshots)

    def get_snapshot(self):
        """Mock snapshot function."""
        return open("unittests/test_pattern.png")

    def test_parse_command_unknown(self):
        self.command.help = mock.Mock()

        self.command.parse_command("HELP")
        self.command.help.assert_called_once()
        self.command.help.reset_mock()

        self.command.parse_command("/?")
        self.command.help.assert_called_once()
        self.command.help.reset_mock()

        snapshots, embeds = self.command.parse_command("not a command")
        self.assertIsNone(embeds)
        self.assertIsNone(snapshots)
        self.command.help.assert_not_called()

    def test_parse_command_snapshot(self):
        # Fail: Camera not working.
        # TODO

        # Success: Camera serving images
        TestCommand.get_snapshot = mock.Mock()
        with open("unittests/test_pattern.png") as input_file:
            TestCommand.get_snapshot.return_value = [input_file]

            snapshots, embeds = self.command.parse_command("/snapshot")

            self.assertIsNone(embeds)
            with open("unittests/test_pattern.png") as image:
                self.assertEqual([image.read()], [snapshots[0].read()])

    def test_parse_command_abort(self):
        # Success: Print aborted
        snapshots, embeds = self.command.parse_command("/abort")

        self._validate_simple_embed(embeds, COLOR_ERROR, title="Print aborted")
        self.assertIsNone(snapshots)

    def test_parse_command_help(self):
        # Success: Printed help
        snapshots, embeds = self.command.parse_command("/help")

        message = ""
        for embed in embeds:
            message += str(embed)
        print(message)
        for command, details in self.command.command_dict.items():
            self.assertIn(command, message)
            if details.get('params'):
                for line in details.get('params').split('\n'):
                    self.assertIn(line, message)
            for line in details.get('description').split('\n'):
                self.assertIn(line, message)
        self.assertIsNone(snapshots)

    def test_get_flat_file_list(self):
        self.get_file_manager().list_files = mock.Mock()
        self.get_file_manager().list_files.return_value = file_list
        flat_file_list = self.command.get_flat_file_list()
        self.get_file_manager().list_files.assert_called_once()
        self.assertEqual(2, len(flat_file_list))
        self.assertEqual(flatten_file_list, flat_file_list)

    @mock.patch("time.sleep")
    def test_parse_command_connect(self, mock_sleep):
        # Fail: Too many parameters
        snapshots, embeds = self.command.parse_command("/connect asdf asdf  asdf")
        self._validate_simple_embed(embeds,
                                    COLOR_ERROR,
                                    title="Too many parameters",
                                    description="Should be: /connect [port] [baudrate]")
        self.assertIsNone(snapshots)

        # Fail: Printer already connected
        self.get_printer().is_operational = mock.Mock()
        self.get_printer().is_operational.return_value = True
        snapshots, embeds = self.command.parse_command("/connect")
        self._validate_simple_embed(embeds,
                                    COLOR_ERROR,
                                    title="Printer already connected",
                                    description="Disconnect first")
        self.assertIsNone(snapshots)
        self.get_printer().is_operational.assert_called_once()

        # Fail: wrong format for baudrate
        self.get_printer().is_operational = mock.Mock()
        self.get_printer().is_operational.return_value = False
        snapshots, embeds = self.command.parse_command("/connect port baudrate")
        self._validate_simple_embed(embeds,
                                    COLOR_ERROR,
                                    title="Wrong format for baudrate",
                                    description="should be a number")
        self.assertIsNone(snapshots)
        self.get_printer().is_operational.assert_called_once()

        # Fail: connect failed.
        self.get_printer().is_operational = mock.Mock()
        self.get_printer().is_operational.return_value = False
        self.get_printer().connect = mock.Mock()
        snapshots, embeds = self.command.parse_command("/connect port 1234")
        self._validate_simple_embed(embeds,
                                    COLOR_ERROR,
                                    title="Failed to connect",
                                    description='try: "/connect [port] [baudrate]"')
        self.assertIsNone(snapshots)
        self.assertEqual(2, self.get_printer().is_operational.call_count)
        self.get_printer().connect.assert_called_once_with(port="port", baudrate=1234, profile=None)

    @mock.patch("time.sleep")
    def test_parse_command_disconnect(self, mock_sleep):
        # Fail: Printer already disconnected
        self.get_printer().is_operational = mock.Mock()
        self.get_printer().is_operational.return_value = False
        snapshots, embeds = self.command.parse_command("/disconnect")
        self._validate_simple_embed(embeds,
                                    COLOR_ERROR,
                                    title="Printer is not connected")
        self.assertIsNone(snapshots)
        self.get_printer().is_operational.assert_called_once()

        # Fail: disconnect failed.
        self.get_printer().is_operational = mock.Mock()
        self.get_printer().is_operational.return_value = True
        self.get_printer().disconnect = mock.Mock()
        snapshots, embeds = self.command.parse_command("/disconnect")
        self._validate_simple_embed(embeds,
                                    COLOR_ERROR,
                                    title="Failed to disconnect")
        self.assertIsNone(snapshots)
        self.assertEqual(2, self.get_printer().is_operational.call_count)
        self.get_printer().disconnect.assert_called_once_with()

    def test_parse_command_status(self):
        self.get_settings().get = mock.Mock()
        self.get_settings().get.return_value = True

        self.get_ip_address = mock.Mock()
        self.get_ip_address.return_value = "192.168.1.1"

        self.get_external_ip_address = mock.Mock()
        self.get_external_ip_address.return_value = "8.8.8.8"

        self.get_printer().is_operational = mock.Mock()
        self.get_printer().is_operational.return_value = True

        self.get_printer().is_printing = mock.Mock()
        self.get_printer().is_printing.return_value = True

        self.get_printer().get_current_data = mock.Mock()
        self.get_printer().get_current_data.return_value = {
            'currentZ': 10,
            'job': {'file': {'name': 'filename'}},
            'progress': {
                'completion': 15,
                'printTime': 300,
                'printTimeLeft': 500
            }
        }

        self.get_printer().get_current_temperatures = mock.Mock()
        self.get_printer().get_current_temperatures.return_value = {
            'bed': {'actual': 100},
            'extruder0': {'actual': 250},
            'extruder1': {'actual': 350}
        }

        self.get_snapshot = mock.Mock()
        self.get_snapshot.return_value = mock.Mock()
        snapshots, embeds = self.command.parse_command('/status')

        message = ""
        for embed in embeds:
            message += str(embed)
        print(message)

        self.get_snapshot.assert_called_once()
        self.assertEqual(self.get_snapshot.return_value, snapshots)

        expected_terms = ['Status', 'Operational', 'Current Z',
                          'Bed Temp', 'extruder0', 'extruder1', 'File', 'Progress',
                          'Time Spent', 'Time Remaining',
                          humanfriendly.format_timespan(300), humanfriendly.format_timespan(500),
                          self.get_ip_address.return_value, self.get_external_ip_address.return_value]

        self.assertEqual(2, self.get_settings().get.call_count)

        calls = [mock.call(["show_local_ip"], merged=True),
                 mock.call(["show_external_ip"], merged=True)]
        self.get_settings().get.assert_has_calls(calls)

        for term in expected_terms:
            self.assertIn(term, message)

    def test_parse_command_pause(self):
        self.get_snapshot = mock.Mock()
        self.get_snapshot.return_value = mock.Mock()
        self.get_printer().pause_print = mock.Mock()
        snapshots, embeds = self.command.parse_command("/pause")

        self._validate_simple_embed(embeds,
                                    COLOR_SUCCESS,
                                    title="Print paused")
        self.get_snapshot.assert_called_once()
        self.assertEqual(self.get_snapshot.return_value, snapshots)
        self.get_printer().pause_print.assert_called_once()

    def test_parse_command_resume(self):
        self.get_snapshot = mock.Mock()
        self.get_snapshot.return_value = mock.Mock()
        self.get_printer().resume_print = mock.Mock()
        snapshots, embeds = self.command.parse_command("/resume")

        self._validate_simple_embed(embeds,
                                    COLOR_SUCCESS,
                                    title="Print resumed")
        self.get_snapshot.assert_called_once()
        self.assertEqual(self.get_snapshot.return_value, snapshots)
        self.get_printer().resume_print.assert_called_once()

    @mock.patch("requests.get")
    def test_upload_file(self, mock_get):
        self.get_file_manager().path_on_disk = mock.Mock()
        self.get_file_manager().path_on_disk.return_value = "./temp.file"

        mock_request_val = mock.Mock()
        mock_request_val.iter_content = mock.Mock()
        mock_request_val.iter_content.return_value = b'1234'
        mock_get.return_value = mock_request_val

        self.command.upload_file("filename", "http://mock.url")

        self.get_file_manager().path_on_disk.assert_called_once_with('local', 'filename')
        mock_get.assert_called_once_with("http://mock.url", stream=True)

        with open("./temp.file", 'rb') as f:
            self.assertEqual(b'1234', f.read())

        os.remove("./temp.file")
