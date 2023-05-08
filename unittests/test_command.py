import io
from typing import List, Tuple

import humanfriendly
import mock
import os

from discord import Embed, File
from zipfile import ZipFile

from octoprint.printer import InvalidFileType, InvalidFileLocation

from octoprint_discordremote import Command, DiscordRemotePlugin
from octoprint_discordshim.embedbuilder import COLOR_INFO, COLOR_ERROR, COLOR_SUCCESS
from unittests.discordremotetestcase import DiscordRemoteTestCase

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


class TestCommand(DiscordRemoteTestCase):

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

    def _validate_simple_embed(self, embed: Embed, color, title=None, description=None, image: Tuple[str, File]=None):
        self.assertIsNotNone(embed)

        self.assertEqual(color, embed.color.value)
        self.assertIsNotNone(embed.timestamp)

        if title:
            self.assertEqual(title, embed.title)

        if description:
            self.assertEqual(description, embed.description)

        if image:
            self.assertEqual("attachment://%s" % image[0], embed.image.url)

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
            messages = self.command.parse_command(command, user="Dummy")
            self.assertEqual(1, len(messages))
            embed, snapshot = messages[0]
            self.assertIsNone(snapshot)
            self.assertIsNone(embed)
            self.command.help.assert_called_once()
            self.command.check_perms.assert_called_once()

        # Invalid commands
        for command in ['asdf / fdsa', 'help', 'whatever']:
            self.command.check_perms.reset_mock()
            self.command.help.reset_mock()
            messages = self.command.parse_command(command, user="Dummy")
            self.assertEqual(0, len(messages))
            self.command.help.assert_not_called()
            self.command.check_perms.assert_not_called()

        # Permission denied
        self.command.check_perms.reset_mock()
        self.command.check_perms.return_value = False
        messages = self.command.parse_command("/print", user="Dummy")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed, COLOR_ERROR, title="Permission Denied")
        self.command.check_perms.assert_called_once()

    def test_parse_command_list(self):
        # Success
        self.plugin.get_file_manager().list_files = mock.Mock()
        self.plugin.get_file_manager().list_files.return_value = file_list
        messages = self.command.parse_command("/files")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.plugin.get_file_manager().list_files.assert_called_once()
        self.assertIsNone(snapshot)

        self._validate_embeds([embed], COLOR_INFO)

    def test_parse_command_print(self):
        # Invalid Arguments
        messages = self.command.parse_command("/print")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title='Wrong number of arguments',
                                    description='try "%sprint [filename]"' % self.plugin.get_settings().get(
                                        ["prefix"]))
        self.assertIsNone(snapshot)

        # Printer not ready
        self.plugin.get_printer().is_ready = mock.Mock()
        self.plugin.get_printer().is_ready.return_value = False
        messages = self.command.parse_command("/print dummyfile.gcode")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title='Printer is not ready')
        self.assertIsNone(snapshot)

        # Printer is ready, file not found
        self.plugin.get_printer().is_ready.return_value = True
        self.command.find_file = mock.Mock()
        self.command.find_file.return_value = None
        messages = self.command.parse_command("/print dummyfile.gcode")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title='Failed to find the file')
        self.assertIsNone(snapshot)

        # Printer is ready, file is found, invalid file type
        self.command.find_file.return_value = {'location': 'sdcard', 'path': '/temp/path'}
        self.plugin.get_printer().select_file = mock.Mock()
        self.plugin.get_printer().select_file.side_effect = InvalidFileType
        messages = self.command.parse_command("/print dummyfile.gcode")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title='Invalid file type selected')
        self.assertIsNone(snapshot)

        # Printer is ready, file is found, invalid file location
        self.plugin.get_printer().select_file.side_effect = InvalidFileLocation
        messages = self.command.parse_command("/print dummyfile.gcode")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title='Invalid file location?')
        self.assertIsNone(snapshot)

        # Printer is ready, file is found, print started
        self.plugin.get_printer().select_file.side_effect = None
        messages = self.command.parse_command("/print dummyfile.gcode")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_SUCCESS,
                                    title='Successfully started print',
                                    description='/temp/path')
        self.assertIsNone(snapshot)

    def test_parse_command_snapshot(self):
        # Fail: Camera not working.
        # TODO

        # Success: Camera serving images
        self.plugin.get_snapshot = mock.Mock()
        with open(self._get_path("test_pattern.png")) as input_file:
            self.plugin.get_snapshot.return_value = ('snapshot.png', input_file)

            messages = self.command.parse_command("/snapshot")
            self.assertEqual(1, len(messages))
            embed, snapshot = messages[0]

            self.assertIsNotNone(snapshot)
            self._validate_simple_embed(embed, COLOR_INFO, image=self.plugin.get_snapshot.return_value)

    def test_parse_command_abort(self):
        # Success: Print aborted
        messages = self.command.parse_command("/abort")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]

        self._validate_simple_embed(embed, COLOR_ERROR, title="Print aborted")
        self.assertIsNone(snapshot)

    def test_parse_command_help(self):
        # Success: Printed help
        messages = self.command.parse_command("/help")
        self.assertEqual(2, len(messages))
        embed, snapshot = messages[0]

        # for command, details in self.command.command_dict.items():
        #     self.assertIn(command, str(embed))
        #     if details.get('params'):
        #         for line in details.get('params').split('\n'):
        #             self.assertIn(line, str(embed))
        #     for line in details.get('description').split('\n'):
        #         self.assertIn(line, str(embed))
        self.assertIsNone(snapshot)

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
        messages = self.command.parse_command("/connect asdf asdf  asdf")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Too many parameters",
                                    description="Should be: /connect [port] [baudrate]")
        self.assertIsNone(snapshot)

        # Fail: Printer already connected
        self.plugin.get_printer().is_operational = mock.Mock()
        self.plugin.get_printer().is_operational.return_value = True
        messages = self.command.parse_command("/connect")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Printer already connected",
                                    description="Disconnect first")
        self.assertIsNone(snapshot)
        self.plugin.get_printer().is_operational.assert_called_once()

        # Fail: wrong format for baudrate
        self.plugin.get_printer().is_operational = mock.Mock()
        self.plugin.get_printer().is_operational.return_value = False
        messages = self.command.parse_command("/connect port baudrate")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Wrong format for baudrate",
                                    description="should be a number")
        self.assertIsNone(snapshot)
        self.plugin.get_printer().is_operational.assert_called_once()

        # Fail: connect failed.
        self.plugin.get_printer().is_operational = mock.Mock()
        self.plugin.get_printer().is_operational.return_value = False
        self.plugin.get_printer().connect = mock.Mock()
        messages = self.command.parse_command("/connect port 1234")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Failed to connect",
                                    description='try: "/connect [port] [baudrate]"')
        self.assertIsNone(snapshot)
        self.assertEqual(31, self.plugin.get_printer().is_operational.call_count)
        self.plugin.get_printer().connect.assert_called_once_with(port="port", baudrate=1234, profile=None)

    @mock.patch("time.sleep")
    def test_parse_command_disconnect(self, mock_sleep):
        # Fail: Printer already disconnected
        self.plugin.get_printer().is_operational = mock.Mock()
        self.plugin.get_printer().is_operational.return_value = False
        messages = self.command.parse_command("/disconnect")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Printer is not connected")
        self.assertIsNone(snapshot)
        self.plugin.get_printer().is_operational.assert_called_once()

        # Fail: disconnect failed.
        self.plugin.get_printer().is_operational = mock.Mock()
        self.plugin.get_printer().is_operational.return_value = True
        self.plugin.get_printer().disconnect = mock.Mock()
        messages = self.command.parse_command("/disconnect")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Failed to disconnect")
        self.assertIsNone(snapshot)
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

        with open(self._get_path('test_pattern.png')) as input_file:
            self.plugin.get_snapshot.return_value = ('snapshot.png', input_file)

            messages = self.command.parse_command('/status')
            self.assertEqual(1, len(messages))
            embed, snapshot = messages[0]

            self.assertIsNotNone(snapshot)
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
        self.plugin.get_snapshot.return_value = ('snapshot.png', mock.Mock(spec=io.IOBase))
        self.plugin.get_printer().pause_print = mock.Mock()
        messages = self.command.parse_command("/pause")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_SUCCESS,
                                    title="Print paused",
                                    image=self.plugin.get_snapshot.return_value)
        self.plugin.get_snapshot.assert_called_once()
        self.assertEqual(self.plugin.get_snapshot.return_value[1], snapshot.fp)
        self.plugin.get_printer().pause_print.assert_called_once()

    def test_parse_command_resume(self):
        self.plugin.get_snapshot = mock.Mock()
        self.plugin.get_snapshot.return_value = ('snapshot.png', mock.Mock(spec=io.IOBase))
        self.plugin.get_printer().resume_print = mock.Mock()
        messages = self.command.parse_command("/resume")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self._validate_simple_embed(embed,
                                    COLOR_SUCCESS,
                                    title="Print resumed",
                                    image=self.plugin.get_snapshot.return_value)
        self.plugin.get_snapshot.assert_called_once()
        self.assertEqual(self.plugin.get_snapshot.return_value[1], snapshot.fp)
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
        messages = self.command.download_file("filename", "http://mock.url", None)
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
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

        messages = self.command.download_file("filename", "http://mock.url", "1234")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
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

        messages = self.command.download_file("filename", "http://mock.url", "1234")
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
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
        messages = self.command.gcode(["/gcode", "M0"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Printer not connected",
                                    description="Connect to printer first.")

        # Printer connected, invalid GCODE
        self.plugin.get_printer().is_operational.return_value = True
        self.plugin.get_settings().get = mock.Mock()
        self.plugin.get_settings().get.return_value = "G0, M0|M851"
        messages = self.command.gcode(["/gcode", "M1"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Invalid GCODE",
                                    description="If you want to use \"M1\", add it to the allowed GCODEs")

        # Failed to send
        self.plugin.get_printer().commands = mock.Mock()
        self.plugin.get_printer().commands.side_effect = Exception("Error")
        messages = self.command.gcode(["/gcode", "M0"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Failed to execute gcode",
                                    description="Error: Error")

        # Success - Case Insensitive:
        self.plugin.get_printer().commands.reset_mock()
        self.plugin.get_printer().commands.side_effect = None
        messages = self.command.gcode(["/gcode", "m0"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
                                    COLOR_SUCCESS,
                                    title="Sent script")
        self.plugin.get_printer().commands.assert_called_once_with(['M0'])

    @mock.patch('octoprint_discordremote.command.upload_file')
    def test_parse_command_getfile(self, mock_upload):
        self.command.find_file = mock.Mock()
        self.command.find_file.return_value = None
        messages = self.command.getfile(["/getfile", "test.gcode"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Failed to find file matching the name given")

        self.command.find_file.return_value = {'location': None, 'path': None}
        mock_upload.return_value = [(True, True)]
        self.plugin.get_file_manager = mock.Mock()
        mock_file_manager = mock.Mock()
        self.plugin.get_file_manager.return_value = mock_file_manager
        messages = self.command.getfile(["/getfile", "test.gcode"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertTrue(snapshot)
        self.assertTrue(embed)

    @mock.patch('os.walk')
    @mock.patch('octoprint_discordremote.command.upload_file')
    def test_parse_command_gettimelapse(self, mock_upload, mock_oswalk):
        self.plugin._data_folder = ''
        mock_oswalk.return_value = [('', [], [])]
        messages = self.command.gettimelapse(["/gettimelapse", "test.gcode"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Failed to find file matching the name given")

        mock_oswalk.return_value = [('', [], ['test.gcode'])]
        mock_upload.return_value = [(True, True)]
        messages = self.command.gettimelapse(["/gettimelapse", "test.gcode"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertTrue(snapshot)
        self.assertTrue(embed)

    def test_unzip(self):

        # prepare a working  dummy zip
        with ZipFile('./testzip.zip', 'w') as zipf:
            zipf.writestr('test.gcode', "Proper GCODE file!")
            zipf.writestr('test.txt', "Don't extract that!")
            zipf.close()

        # create a multi-volume dummy zip, too
        # code adapted, taken from Jeronimo's answer in https://stackoverflow.com/questions/52193680/split-a-zip-archive-into-multiple-chunks
        outfile = './testzipMV.zip'
        packet_size = int(100)  # bytes

        with open('./testzip.zip', "rb") as output:
            filecount = 1
            while True:
                data = output.read(packet_size)
                if not data:
                    break  # we're done
                with open("{}.{:03}".format(outfile, filecount), "wb") as packet:
                    packet.write(data)
                filecount += 1

        # reroute calls to Octoprint's local folder to project local folder
        def path_sideeff(*args, **kwargs):
            if args[0] == 'local':
                return os.path.join('./', args[1])
            return None

        def file_exists_sideeff(*args, **kwargs):
            if args[0] == 'local':
                return os.path.isfile(os.path.join('./', args[1]))
            return None

        self.plugin.get_file_manager().path_on_disk = mock.Mock()
        self.plugin.get_file_manager().path_on_disk.side_effect = path_sideeff

        self.plugin.get_file_manager().file_exists = mock.Mock()
        self.plugin.get_file_manager().file_exists.side_effect = file_exists_sideeff

        self.command.get_flat_file_list = mock.Mock()
        self.command.get_flat_file_list.return_value = []

        # CASE 1: File doesn't exist
        messages = self.command.unzip(["/unzip", "testzip.zip"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed, COLOR_ERROR, title="File testzip.zip not found.")

        # CASE 2: File exists but is not a zip file
        self.plugin.get_settings().get = mock.Mock()
        self.plugin.get_settings().get.return_value = ''

        messages = self.command.unzip(["/unzip", "testzip.nope"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Not a valid Zip file.")

        self.command.get_flat_file_list.return_value = zip_flat_file_list

        # CASE 3: File is a working zip file
        messages = self.command.unzip(["/unzip", "testzip.zip"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
                                    COLOR_SUCCESS,
                                    title="File(s) unzipped. ")

        # make sure it didn't extract the unwanted .txt in the zip file, only the gcode file
        self.assertTrue(os.path.isfile('./test.gcode'))
        self.assertFalse(os.path.isfile('./test.txt'))

        with open('./test.gcode') as f:
            self.assertEqual("Proper GCODE file!", f.read())

        os.remove('./test.gcode')
        os.remove('./testzip.zip')

        # CASE 4: File is a working multi-volume zip file
        messages = self.command.unzip(["/unzip", "testzipMV.zip.001"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
                                    COLOR_SUCCESS,
                                    title="File(s) unzipped. ")
        # no need to test for unwanted extracted files, code is the same as for single-volume zips
        os.remove('./test.gcode')
        os.remove('./testzipMV.zip')

        # CASE 5: File is a multi-volume zip file, but it's missing volumes
        os.remove('./testzipMV.zip.002')
        self.command.get_flat_file_list.return_value = [zip_flat_file_list[0], zip_flat_file_list[2]]

        messages = self.command.unzip(["/unzip", "testzipMV.zip.001"])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self._validate_simple_embed(embed,
                                    COLOR_ERROR,
                                    title="Bad zip file.")

        os.remove('./testzipMV.zip')
        os.remove('./testzipMV.zip.001')
        os.remove('./testzipMV.zip.003')
