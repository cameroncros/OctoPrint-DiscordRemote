import os
import humanfriendly
from unittest import TestCase

import mock

from octoprint_discordremote import Command

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
    _printer = mock.Mock()
    _plugin_manager = mock.Mock()

    def setUp(self):
        self.command = Command(self)

    def test_parse_command_list(self):
        # Success
        self._file_manager.list_files = mock.Mock()
        self._file_manager.list_files.return_value = file_list
        message, snapshot = self.command.parse_command("/files")
        print('\n' + message + '\n')
        self._file_manager.list_files.assert_called_once()
        self.assertIsNone(snapshot)

    def test_parse_command_print(self):
        # FAIL: Printer not ready
        self._printer.is_ready = mock.Mock()
        self._printer.is_ready.return_value = False
        message, snapshot = self.command.parse_command("/print test.gcode")
        self._printer.is_ready.assert_called_once()
        self.assertEqual("Printer is not ready", message)
        self.assertIsNone(snapshot)
        # TODO

        # Success: Printer ready
        # TODO: Mock and validate the print started
        self.command.get_flat_file_list = mock.Mock()
        self.command.get_flat_file_list.return_value = flatten_file_list
        self._printer.is_ready = mock.Mock()
        self._printer.is_ready.return_value = True
        message, snapshot = self.command.parse_command("/print test.gcode")
        self._printer.is_ready.assert_called_once()
        self.assertIn("Successfully started print:", message)
        self.assertIn("test.gcode", message)
        self.assertIsNone(snapshot)

    def get_snapshot(self):
        """Mock snapshot function."""
        return open("unittests/test_pattern.png")

    def test_parse_command_snapshot(self):
        # Fail: Camera not working.
        # TODO

        # Success: Camera serving images
        TestCommand.get_snapshot = mock.Mock()
        with open("unittests/test_pattern.png") as input_file:
            TestCommand.get_snapshot.return_value = input_file

            message, snapshot = self.command.parse_command("/snapshot")

            self.assertIsNone(message)
            with open("unittests/test_pattern.png") as image:
                self.assertEqual([image.read()], [snapshot.read()])

    def test_parse_command_abort(self):
        # Success: Print aborted
        message, snapshot = self.command.parse_command("/abort")
        self.assertEqual("Print aborted", message)
        self.assertIsNone(snapshot)

    def test_parse_command_help(self):
        # Success: Printed help
        message, snapshot = self.command.parse_command("/help")
        print('\n' + message + '\n')
        for command, details in self.command.command_dict.items():
            self.assertIn(command, message)
            if details.get('params'):
                for line in details.get('params').split('\n'):
                    self.assertIn(line, message)
            for line in details.get('description').split('\n'):
                self.assertIn(line, message)
        self.assertIsNone(snapshot)

    def test_get_flat_file_list(self):
        self._file_manager.list_files = mock.Mock()
        self._file_manager.list_files.return_value = file_list
        flat_file_list = self.command.get_flat_file_list()
        self._file_manager.list_files.assert_called_once()
        self.assertEqual(2, len(flat_file_list))
        self.assertEqual(flatten_file_list, flat_file_list)

    @mock.patch("time.sleep")
    def test_parse_command_connect(self, mock_sleep):
        # Fail: Too many parameters
        message, snapshot = self.command.parse_command("/connect asdf asdf  asdf")
        self.assertEqual("Too many parameters. Should be: /connect [port] [baudrate]", message)
        self.assertIsNone(snapshot)

        # Fail: Printer already connected
        self._printer.is_operational = mock.Mock()
        self._printer.is_operational.return_value = True
        message, snapshot = self.command.parse_command("/connect")
        self.assertEqual('Printer already connected. Disconnect first', message)
        self.assertIsNone(snapshot)
        self._printer.is_operational.assert_called_once()

        # Fail: wrong format for baudrate
        self._printer.is_operational = mock.Mock()
        self._printer.is_operational.return_value = False
        message, snapshot = self.command.parse_command("/connect port baudrate")
        self.assertEqual('Wrong format for baudrate, should be a number', message)
        self.assertIsNone(snapshot)
        self._printer.is_operational.assert_called_once()

        # Fail: connect failed.
        self._printer.is_operational = mock.Mock()
        self._printer.is_operational.return_value = False
        self._printer.connect = mock.Mock()
        message, snapshot = self.command.parse_command("/connect port 1234")
        self.assertEqual('Failed to connect, try: "/connect [port] [baudrate]"', message)
        self.assertIsNone(snapshot)
        self.assertEqual(2, self._printer.is_operational.call_count)
        self._printer.connect.assert_called_once_with(port="port", baudrate=1234, profile=None)

    @mock.patch("time.sleep")
    def test_parse_command_disconnect(self, mock_sleep):
        # Fail: Printer already disconnected
        self._printer.is_operational = mock.Mock()
        self._printer.is_operational.return_value = False
        message, snapshot = self.command.parse_command("/disconnect")
        self.assertEqual('Printer is not connected', message)
        self.assertIsNone(snapshot)
        self._printer.is_operational.assert_called_once()

        # Fail: disconnect failed.
        self._printer.is_operational = mock.Mock()
        self._printer.is_operational.return_value = True
        self._printer.disconnect = mock.Mock()
        message, snapshot = self.command.parse_command("/disconnect")
        self.assertEqual('Failed to disconnect', message)
        self.assertIsNone(snapshot)
        self.assertEqual(2, self._printer.is_operational.call_count)
        self._printer.disconnect.assert_called_once_with()

    def test_parse_command_status(self):
        self._printer.is_operational = mock.Mock()
        self._printer.is_operational.return_value = True

        self._printer.is_printing = mock.Mock()
        self._printer.is_printing.return_value = True

        self._printer.get_current_data = mock.Mock()
        self._printer.get_current_data.return_value = {
            'currentZ': 10,
            'job': {'file': {'name': 'filename'}},
            'progress': {
                'completion': 15,
                'printTime': 300,
                'printTimeLeft': 500
            }
        }

        self._printer.get_current_temperatures = mock.Mock()
        self._printer.get_current_temperatures.return_value = {
            'bed': {'actual': 100},
            'extruder0': {'actual': 250},
            'extruder1': {'actual': 350}
        }

        self.get_snapshot = mock.Mock()
        self.get_snapshot.return_value = mock.Mock()
        message, snapshot = self.command.parse_command('/status')
        print('\n' + message + '\n')
        self.get_snapshot.assert_called_once()
        self.assertEqual(self.get_snapshot.return_value, snapshot)

        expected_terms = ['Status', 'Value', 'Operational', 'Current Z',
                          'Bed Temp', 'extruder0', 'extruder1', 'File', 'Progress',
                          'Time Spent', 'Time Remaining',
                          humanfriendly.format_timespan(300), humanfriendly.format_timespan(500)]
        for term in expected_terms:
            self.assertIn(term, message)

    def test_parse_command_pause(self):
        self.get_snapshot = mock.Mock()
        self.get_snapshot.return_value = mock.Mock()
        self._printer.pause_print = mock.Mock()
        message, snapshot = self.command.parse_command("/pause")
        self.assertEqual("Print paused", message)
        self.get_snapshot.assert_called_once()
        self.assertEqual(self.get_snapshot.return_value, snapshot)
        self._printer.pause_print.assert_called_once()

    def test_parse_command_resume(self):
        self.get_snapshot = mock.Mock()
        self.get_snapshot.return_value = mock.Mock()
        self._printer.resume_print = mock.Mock()
        message, snapshot = self.command.parse_command("/resume")
        self.assertEqual("Print resumed", message)
        self.get_snapshot.assert_called_once()
        self.assertEqual(self.get_snapshot.return_value, snapshot)
        self._printer.resume_print.assert_called_once()

    @mock.patch("requests.get")
    def test_upload_file(self, mock_get):
        self._file_manager.path_on_disk = mock.Mock()
        self._file_manager.path_on_disk.return_value = "./temp.file"

        mock_request_val = mock.Mock()
        mock_request_val.iter_content = mock.Mock()
        mock_request_val.iter_content.return_value = b'1234'
        mock_get.return_value = mock_request_val

        self.command.upload_file("filename", "http://mock.url")

        self._file_manager.path_on_disk.assert_called_once_with('local', 'filename')
        mock_get.assert_called_once_with("http://mock.url", stream=True)

        with open("./temp.file", 'rb') as f:
            self.assertEqual(b'1234', f.read())

        os.remove("./temp.file")
