import io
from typing import List, Tuple, Optional

import humanfriendly
import mock
import os

from discord import Embed, File
from zipfile import ZipFile

from octoprint.printer import InvalidFileType, InvalidFileLocation

from octoprint_discordremote import Command, DiscordRemotePlugin, Response, ProtoFile
from octoprint_discordremote.responsebuilder import COLOR_INFO, COLOR_ERROR, COLOR_SUCCESS
from unittests.discordlinktestcase import DiscordLinkTestCase

file_list = {'local': {
    u'folder1': {'name': u'folder1', 'path': u'folder1', 'size': 6530, 'type': 'folder', 'typePath': ['folder'],
                 'display': u'folder1',
                 'children': {
                     u'test.gcode': {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'name': u'test.gcode',
                                     'typePath': ['machinecode', 'gcode'], 'analysis': {
                             'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None,
                                              'minZ': None}, 'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
                             'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'date': 1525822075,
                                     'path': u'folder1/test.gcode', 'type': 'machinecode', 'display': u'test.gcode',
                                     'size': 6530}
                 }},
    u'test2.gcode': {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'name': u'test.gcode',
                     'typePath': ['machinecode', 'gcode'], 'analysis': {
            'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None,
                             'minZ': None}, 'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
            'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'date': 1525822021,
                     'path': u'test.gcode', 'type': 'machinecode', 'display': u'test.gcode',
                     'size': 6530}}}

flatten_file_list = [
    {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'location': 'local', 'name': u'test.gcode', 'date': 1525822075,
     'path': u'folder1/test.gcode', 'size': 6530, 'type': 'machinecode', 'typePath': ['machinecode', 'gcode'],
     'analysis': {'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None, 'minZ': None},
                  'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
                  'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'display': u'test.gcode'},
    {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'location': 'local', 'name': u'test.gcode', 'date': 1525822021,
     'path': u'/test2.gcode', 'size': 6530, 'type': 'machinecode', 'typePath': ['machinecode', 'gcode'],
     'analysis': {'printingArea': {'maxZ': None, 'maxX': None, 'maxY': None, 'minX': None, 'minY': None, 'minZ': None},
                  'dimensions': {'width': 0.0, 'depth': 0.0, 'height': 0.0},
                  'filament': {'tool0': {'volume': 0.0, 'length': 0.0}}}, 'display': u'test.gcode'}]

zip_flat_file_list = [
    {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'location': 'local', 'name': u'testzip.zip',
     'date': 1525822021, 'path': u'/testzip.zip', 'size': 6530},
    {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'location': 'local', 'name': u'testzipMV.zip.001',
     'date': 1525822021,
     'path': u'/testzipMV.zip.001', 'size': 6530},
    {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'location': 'local', 'name': u'testzipMV.zip.002',
     'date': 1525822021,
     'path': u'/testzipMV.zip.002', 'size': 6530},
    {'hash': 'e2337a4310c454a0198718425330e62fcbe4329e', 'location': 'local', 'name': u'testzipMV.zip.003',
     'date': 1525822021,
     'path': u'/testzipMV.zip.003', 'size': 6530}
]


class TestCommand(DiscordLinkTestCase):

    def _mock_settings_get(self, *args, **kwards):
        if args[0] == ["prefix"]:
            return "/"
        elif args[0] == ['show_local_ip']:
            return True
        elif args[0] == ['show_external_ip']:
            return True
        elif args[0] == ['baseurl']:
            return None
        else:
            self.assertFalse(True, "Not mocked: %s" % args[0])

    def setUp(self):
        self.plugin = DiscordRemotePlugin()
        self.plugin.discord = mock.Mock()
        self.plugin._printer = mock.Mock()
        self.plugin._plugin_manager = mock.Mock()
        self.plugin._file_manager = mock.Mock()
        self.plugin._settings = mock.Mock()
        self.plugin._settings.get = mock.Mock()
        self.plugin._settings.get.side_effect = self._mock_settings_get

        self.plugin.get_printer_name = mock.Mock()
        self.plugin.get_printer_name.return_value = 'OctoPrint'

        self.plugin.get_ip_address = mock.Mock()
        self.plugin.get_ip_address.return_value = "192.168.1.1"

        self.plugin.get_external_address = mock.Mock()
        self.plugin.get_external_address.return_value = "1.2.3.4"

        self.command = Command(self.plugin)

    def _validate_embeds(self, embeds: List[Embed], color):
        self.assertIsNotNone(embeds)
        self.assertGreaterEqual(1, len(embeds))
        for embed in embeds:
            self.assertEqual(color, embed.color.value)
            self.assertIsNotNone(embed.timestamp)

    def _validate_simple_embed(self, response: Response, color, title=None, description=None, image: Optional[ProtoFile] = None):
        self.assertIsNotNone(response)

        embed = response.embed
        self.assertIsNotNone(embed)

        self.assertEqual(color, embed.color)

        if title:
            self.assertEqual(title, embed.title)

        if description:
            self.assertEqual(description, embed.description)

        if image:
            self.assertEqual(embed.snapshot.filename, image.filename)
            self.assertEqual(embed.snapshot.data, image.data)

    def test_parse_command(self):
        self.command.check_perms = mock.Mock()
        self.command.check_perms.return_value = True
        self.command.help = mock.Mock()
        self.command.help.return_value = [(None, None)]

        self.command.command_dict['help'] = {'cmd': self.command.help, 'description': "Mock help."}

        # Valid /help commands
        for command in ['/asdf', "/", "/help", "/?"]:
            self.command.check_perms.reset_mock()
            self.command.help.reset_mock()
            response = self.command.parse_command(command, user="Dummy")
            self.command.help.assert_called_once()
            self.command.check_perms.assert_called_once()

        # Invalid commands
        for command in ['asdf / fdsa', 'help', 'whatever']:
            self.command.check_perms.reset_mock()
            self.command.help.reset_mock()
            response = self.command.parse_command(command, user="Dummy")
            self.command.help.assert_not_called()
            self.command.check_perms.assert_not_called()

        # Permission denied
        self.command.check_perms.reset_mock()
        self.command.check_perms.return_value = False
        response = self.command.parse_command("/print", user="Dummy")

        self._validate_simple_embed(response, COLOR_ERROR, title="Permission Denied")
        self.command.check_perms.assert_called_once()

    def test_parse_command_list(self):
        # Success
        self.plugin.get_file_manager().list_files = mock.Mock()
        self.plugin.get_file_manager().list_files.return_value = file_list
        response = self.command.parse_command("/files")

        self.plugin.get_file_manager().list_files.assert_called_once()

        self._validate_embeds(response, COLOR_INFO)

    def test_parse_command_print(self):
        # Invalid Arguments
        response = self.command.parse_command("/print")

        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title='Wrong number of arguments',
                                    description='try "%sprint [filename]"' % self.plugin.get_settings().get(
                                        ["prefix"]))

        # Printer not ready
        self.plugin.get_printer().is_ready = mock.Mock()
        self.plugin.get_printer().is_ready.return_value = False
        response = self.command.parse_command("/print dummyfile.gcode")

        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title='Printer is not ready')

        # Printer is ready, file not found
        self.plugin.get_printer().is_ready.return_value = True
        self.command.find_file = mock.Mock()
        self.command.find_file.return_value = None
        response = self.command.parse_command("/print dummyfile.gcode")

        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title='Failed to find the file')

        # Printer is ready, file is found, invalid file type
        self.command.find_file.return_value = {'location': 'sdcard', 'path': '/temp/path'}
        self.plugin.get_printer().select_file = mock.Mock()
        self.plugin.get_printer().select_file.side_effect = InvalidFileType
        response = self.command.parse_command("/print dummyfile.gcode")

        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title='Invalid file type selected')

        # Printer is ready, file is found, invalid file location
        self.plugin.get_printer().select_file.side_effect = InvalidFileLocation
        response = self.command.parse_command("/print dummyfile.gcode")

        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title='Invalid file location?')

        # Printer is ready, file is found, print started
        self.plugin.get_printer().select_file.side_effect = None
        response = self.command.parse_command("/print dummyfile.gcode")

        self._validate_simple_embed(response,
                                    COLOR_SUCCESS,
                                    title='Successfully started print',
                                    description='/temp/path')

    def test_parse_command_snapshot(self):
        # Fail: Camera not working.
        # TODO

        # Success: Camera serving images
        self.plugin.get_snapshot = mock.Mock()
        with open(self._get_path("test_pattern.png")) as input_file:
            self.plugin.get_snapshot.return_value = ('snapshot.png', input_file)

            response = self.command.parse_command("/snapshot")
            self._validate_simple_embed(response, COLOR_INFO, image=self.plugin.get_snapshot.return_value)

    def test_parse_command_abort(self):
        # Success: Print aborted
        response = self.command.parse_command("/abort")

        self._validate_simple_embed(response, COLOR_ERROR, title="Print aborted")

    def test_parse_command_help(self):
        # Success: Printed help
        response = self.command.parse_command("/help")

        # for command, details in self.command.command_dict.items():
        #     self.assertIn(command, str(embed))
        #     if details.get('params'):
        #         for line in details.get('params').split('\n'):
        #             self.assertIn(line, str(embed))
        #     for line in details.get('description').split('\n'):
        #         self.assertIn(line, str(embed))

    def test_get_flat_file_list(self):
        self.plugin.get_file_manager().list_files = mock.Mock()
        self.plugin.get_file_manager().list_files.return_value = file_list
        flat_file_list = self.command.get_flat_file_list()
        self.plugin.get_file_manager().list_files.assert_called_once()
        self.assertEqual(len(flatten_file_list), len(flat_file_list))
        for file in flatten_file_list:
            self.assertIn(file, flat_file_list)

    def test_find_file(self):
        self.plugin.get_file_manager().list_files = mock.Mock()
        self.plugin.get_file_manager().list_files.return_value = file_list

        self.assertIsNone(self.command.find_file("NOT_IN_ANY_FILENAME"))
        self.assertEqual(flatten_file_list[0], self.command.find_file("ER1/T"))
        self.assertEqual(flatten_file_list[1], self.command.find_file("TEST2"))

    @mock.patch("time.sleep")
    def test_parse_command_connect(self, mock_sleep):
        # Fail: Too many parameters
        response = self.command.parse_command("/connect asdf asdf  asdf")

        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title="Too many parameters",
                                    description="Should be: /connect [port] [baudrate]")

        # Fail: Printer already connected
        self.plugin.get_printer().is_operational = mock.Mock()
        self.plugin.get_printer().is_operational.return_value = True
        response = self.command.parse_command("/connect")

        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title="Printer already connected",
                                    description="Disconnect first")
        self.plugin.get_printer().is_operational.assert_called_once()

        # Fail: wrong format for baudrate
        self.plugin.get_printer().is_operational = mock.Mock()
        self.plugin.get_printer().is_operational.return_value = False
        response = self.command.parse_command("/connect port baudrate")

        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title="Wrong format for baudrate",
                                    description="should be a number")
        self.plugin.get_printer().is_operational.assert_called_once()

        # Fail: connect failed.
        self.plugin.get_printer().is_operational = mock.Mock()
        self.plugin.get_printer().is_operational.return_value = False
        self.plugin.get_printer().connect = mock.Mock()
        response = self.command.parse_command("/connect port 1234")

        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title="Failed to connect",
                                    description='try: "/connect [port] [baudrate]"')
        self.assertEqual(31, self.plugin.get_printer().is_operational.call_count)
        self.plugin.get_printer().connect.assert_called_once_with(port="port", baudrate=1234, profile=None)

    @mock.patch("time.sleep")
    def test_parse_command_disconnect(self, mock_sleep):
        # Fail: Printer already disconnected
        self.plugin.get_printer().is_operational = mock.Mock()
        self.plugin.get_printer().is_operational.return_value = False
        response = self.command.parse_command("/disconnect")

        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title="Printer is not connected")
        self.plugin.get_printer().is_operational.assert_called_once()

        # Fail: disconnect failed.
        self.plugin.get_printer().is_operational = mock.Mock()
        self.plugin.get_printer().is_operational.return_value = True
        self.plugin.get_printer().disconnect = mock.Mock()
        response = self.command.parse_command("/disconnect")

        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title="Failed to disconnect")
        self.assertEqual(2, self.plugin.get_printer().is_operational.call_count)
        self.plugin.get_printer().disconnect.assert_called_once_with()

    @mock.patch("subprocess.Popen")
    def test_parse_command_status(self, mock_popen):
        self.plugin.get_ip_address = mock.Mock()
        self.plugin.get_ip_address.return_value = "192.168.1.1"

        self.plugin.get_external_ip_address = mock.Mock()
        self.plugin.get_external_ip_address.return_value = "8.8.8.8"

        self.plugin.get_printer().is_operational = mock.Mock()
        self.plugin.get_printer().is_operational.return_value = True

        self.plugin.get_printer().is_printing = mock.Mock()
        self.plugin.get_printer().is_printing.return_value = True

        self.plugin.get_printer().get_current_data = mock.Mock()
        self.plugin.get_printer().get_current_data.return_value = {
            'currentZ': 10,
            'job': {'file': {'name': 'filename'}},
            'progress': {
                'completion': 15,
                'printTime': 300,
                'printTimeLeft': 500
            }
        }

        self.plugin.get_printer().get_current_temperatures = mock.Mock()
        self.plugin.get_printer().get_current_temperatures.return_value = {
            'bed': {'actual': 100},
            'extruder0': {'actual': 250},
            'extruder1': {'actual': 350}
        }

        mock_popen.return_value.communicate.return_value = [b"throttled=0xf000f"]  # All flags raised
        expected_throttled_terms = [
            "PI is under-voltage",
            "PI has capped it's ARM frequency",
            "PI is currently throttled",
            "PI has reached temperature limit",
            "PI Under-voltage has occurred",
            "PI ARM frequency capped has occurred",
            "PI Throttling has occurred",
            "PI temperature limit has occurred",
        ]

        self.plugin.get_snapshot = mock.Mock()

        with open(self._get_path('test_pattern.png'), 'rb') as input_file:
            file_data = input_file.read()
        self.plugin.get_snapshot.return_value = ProtoFile(filename='snapshot.png', data=file_data)

        response = self.command.parse_command('/status')

        self.assertEqual(response.embed.snapshot.data, file_data)
        self.assertEqual(response.embed.snapshot.filename, 'snapshot.png')
        self.plugin.get_snapshot.assert_called_once()

        expected_terms = ['Status', 'Operational', 'Current Z',
                          'Bed Temp', 'extruder0', 'extruder1', 'File', 'Progress',
                          'Time Spent', 'Time Remaining',
                          humanfriendly.format_timespan(300), humanfriendly.format_timespan(500),
                          self.plugin.get_ip_address.return_value, self.plugin.get_external_ip_address.return_value]
        expected_terms += expected_throttled_terms

        self.assertEqual(3, self.plugin.get_settings().get.call_count)

        calls = [mock.call(["show_local_ip"], merged=True),
                 mock.call(["show_external_ip"], merged=True)]
        self.plugin.get_settings().get.assert_has_calls(calls)

    def test_parse_command_pause(self):
        self.plugin.get_snapshot = mock.Mock()
        self.plugin.get_snapshot.return_value = ProtoFile(filename='snapshot.png', data=b'')
        self.plugin.get_printer().pause_print = mock.Mock()
        response = self.command.parse_command("/pause")

        self._validate_simple_embed(response,
                                    COLOR_SUCCESS,
                                    title="Print paused",
                                    image=self.plugin.get_snapshot.return_value)
        self.plugin.get_snapshot.assert_called_once()
        self.plugin.get_printer().pause_print.assert_called_once()

    def test_parse_command_resume(self):
        self.plugin.get_snapshot = mock.Mock()
        self.plugin.get_snapshot.return_value = ProtoFile(filename='snapshot.png', data=b'')
        self.plugin.get_printer().resume_print = mock.Mock()
        response = self.command.parse_command("/resume")

        self._validate_simple_embed(response,
                                    COLOR_SUCCESS,
                                    title="Print resumed",
                                    image=self.plugin.get_snapshot.return_value)
        self.plugin.get_snapshot.assert_called_once()
        self.plugin.get_printer().resume_print.assert_called_once()

    @mock.patch("requests.get")
    def test_download_file(self, mock_get):
        self.plugin.get_file_manager().path_on_disk = mock.Mock()
        self.plugin.get_file_manager().path_on_disk.return_value = "./temp.file"

        mock_request_val = mock.Mock()
        mock_request_val.iter_content = mock.Mock()
        mock_request_val.iter_content.return_value = [b'1234']
        mock_get.return_value = mock_request_val

        # Upload, no user
        response = self.command.download_file("filename", "http://mock.url", None)

        self.assertIsNone(response.embed.snapshot.filename)
        self.assertIsNone(response.embed.snapshot.data)
        self._validate_simple_embed(response,
                                    COLOR_SUCCESS,
                                    title="File Received")

        self.plugin.get_file_manager().path_on_disk.assert_called_once_with('local', 'filename')
        self.plugin.get_file_manager().path_on_disk.reset_mock()
        mock_get.assert_called_once_with("http://mock.url", stream=True)
        mock_get.reset_mock()

        with open("./temp.file", 'rb') as f:
            self.assertEqual(b'1234', f.read())

        os.remove("./temp.file")

        # Upload with user
        self.command.check_perms = mock.Mock()
        self.command.check_perms.return_value = True

        response = self.command.download_file("filename", "http://mock.url", "1234")

        self.assertIsNone(response.embed.snapshot.filename)
        self.assertIsNone(response.embed.snapshot.data)
        self._validate_simple_embed(response,
                                    COLOR_SUCCESS,
                                    title="File Received")

        self.plugin.get_file_manager().path_on_disk.assert_called_once_with('local', 'filename')
        self.plugin.get_file_manager().path_on_disk.reset_mock()
        mock_get.assert_called_once_with("http://mock.url", stream=True)
        mock_get.reset_mock()

        with open("./temp.file", 'rb') as f:
            self.assertEqual(b'1234', f.read())

        # Upload denied
        self.command.check_perms.return_value = False

        response = self.command.download_file("filename", "http://mock.url", "1234")

        self.assertIsNone(response.embed.snapshot.filename)
        self.assertIsNone(response.embed.snapshot.data)
        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title="Permission Denied")

    def test_parse_array(self):
        self.assertIsNone(self.command._parse_array(None))
        self.assertIsNone(self.command._parse_array(1))

        results = self.command._parse_array("*")
        self.assertEqual(1, len(results))
        self.assertIn("*", results)

        results = self.command._parse_array("123")
        self.assertEqual(1, len(results))
        self.assertIn("123", results)

        results = self.command._parse_array("123,456")
        self.assertEqual(2, len(results))
        self.assertIn("123", results)
        self.assertIn("456", results)

        results = self.command._parse_array("123 456")
        self.assertEqual(2, len(results))
        self.assertIn("123", results)
        self.assertIn("456", results)

        results = self.command._parse_array("123/456")
        self.assertEqual(2, len(results))
        self.assertIn("123", results)
        self.assertIn("456", results)

    def test_check_perms(self):
        get_mock = mock.Mock()

        settings_mock = mock.Mock()
        settings_mock.get = get_mock

        self.command.plugin.get_settings = mock.Mock()
        self.command.plugin.get_settings.return_value = settings_mock

        get_mock.return_value = {}
        self.assertFalse(self.command.check_perms("notallowed", "123"))

        get_mock.return_value = {'1': {'users': '*', 'commands': ''}}
        self.assertFalse(self.command.check_perms("notallowed", "123"))

        get_mock.return_value = {'1': {'users': '', 'commands': '*'}}
        self.assertFalse(self.command.check_perms("notallowed", "123"))

        get_mock.return_value = {'1': {'users': '*', 'commands': '*'}}
        self.assertTrue(self.command.check_perms("allowed", "123"))

        get_mock.return_value = {'1': {'users': '123', 'commands': '*'}}
        self.assertTrue(self.command.check_perms("allowed", "123"))

        get_mock.get.return_value = {'1': {'users': '*', 'commands': 'allowed'}}
        self.assertTrue(self.command.check_perms("allowed", "123"))

        get_mock.return_value = {'1': {'users': '123', 'commands': 'allowed'}}
        self.assertTrue(self.command.check_perms("allowed", "123"))

        get_mock.return_value = {'1': {'users': '456', 'commands': 'notallowed'},
                                 '2': {'users': '123', 'commands': 'allowed'}}
        self.assertTrue(self.command.check_perms("allowed", "123"))

    def test_gcode(self):
        # Printer disconnected
        self.plugin.get_printer().is_operational = mock.Mock()
        self.plugin.get_printer().is_operational.return_value = False
        response = self.command.gcode(["/gcode", "M0"])

        self.assertIsNone(response.embed.snapshot.filename)
        self.assertIsNone(response.embed.snapshot.data)
        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title="Printer not connected",
                                    description="Connect to printer first.")

        # Printer connected, invalid GCODE
        self.plugin.get_printer().is_operational.return_value = True
        self.plugin.get_settings().get = mock.Mock()
        self.plugin.get_settings().get.return_value = "G0, M0|M851"
        response = self.command.gcode(["/gcode", "M1"])

        self.assertIsNone(response.embed.snapshot.filename)
        self.assertIsNone(response.embed.snapshot.data)
        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title="Invalid GCODE",
                                    description="If you want to use \"M1\", add it to the allowed GCODEs")

        # Failed to send
        self.plugin.get_printer().commands = mock.Mock()
        self.plugin.get_printer().commands.side_effect = Exception("Error")
        response = self.command.gcode(["/gcode", "M0"])

        self.assertIsNone(response.embed.snapshot.filename)
        self.assertIsNone(response.embed.snapshot.data)
        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title="Failed to execute gcode",
                                    description="Error: Error")

        # Success - Case Insensitive:
        self.plugin.get_printer().commands.reset_mock()
        self.plugin.get_printer().commands.side_effect = None
        response = self.command.gcode(["/gcode", "m0"])

        self.assertIsNone(response.embed.snapshot.filename)
        self.assertIsNone(response.embed.snapshot.data)
        self._validate_simple_embed(response,
                                    COLOR_SUCCESS,
                                    title="Sent script")
        self.plugin.get_printer().commands.assert_called_once_with(['M0'])

    @mock.patch('octoprint_discordremote.command.upload_file')
    def test_parse_command_getfile(self, mock_upload):
        self.command.find_file = mock.Mock()
        self.command.find_file.return_value = None
        response = self.command.getfile(["/getfile", "test.gcode"])

        self.assertIsNone(response.embed.snapshot.filename)
        self.assertIsNone(response.embed.snapshot.data)
        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title="Failed to find file matching the name given")

        self.command.find_file.return_value = {'location': None, 'path': None}
        mock_upload.return_value = [(True, True)]
        self.plugin.get_file_manager = mock.Mock()
        mock_file_manager = mock.Mock()
        self.plugin.get_file_manager.return_value = mock_file_manager
        response = self.command.getfile(["/getfile", "test.gcode"])

        self.assertIsNotNone(response)

    @mock.patch('os.walk')
    @mock.patch('octoprint_discordremote.command.upload_file')
    def test_parse_command_gettimelapse(self, mock_upload, mock_oswalk):
        self.plugin._data_folder = ''
        mock_oswalk.return_value = [('', [], [])]
        response = self.command.gettimelapse(["/gettimelapse", "test.gcode"])

        self.assertIsNone(response.embed.snapshot.filename)
        self.assertIsNone(response.embed.snapshot.data)
        self._validate_simple_embed(response,
                                    COLOR_ERROR,
                                    title="Failed to find file matching the name given")

        mock_oswalk.return_value = [('', [], ['test.gcode'])]
        mock_upload.return_value = [(True, True)]
        response = self.command.gettimelapse(["/gettimelapse", "test.gcode"])

        self.assertIsNotNone(response)
