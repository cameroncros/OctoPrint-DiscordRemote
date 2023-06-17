import json
from collections import OrderedDict
from mock import mock

from octoprint_discordremote.command_plugins.system_commands import SystemCommands
from octoprint_discordremote.responsebuilder import COLOR_SUCCESS, COLOR_ERROR
from unittests.mockdiscordtestcase import MockDiscordTestCase


class TestSystemCommand(MockDiscordTestCase):
    def setUp(self):
        super().setUp()
        self.system_commands = SystemCommands()

    def test_setup(self):
        command = mock.Mock()
        command.command_dict = OrderedDict()

        plugin = mock.Mock()
        self.system_commands.setup(command, plugin)

        self.assertEqual(2, len(command.command_dict))
        self.assertIn('listsystemcommands', command.command_dict.keys())
        self.assertIn('systemcommand', command.command_dict.keys())

    @mock.patch('requests.get')
    def test_list_all_commands(self, requests_mock):
        self.system_commands.plugin = mock.Mock()
        self.system_commands.plugin.get_printer_name = mock.Mock()
        self.system_commands.plugin.get_printer_name.return_value = "OctoPrint"
        self.system_commands.plugin.get_settings.return_value.get.return_value = '/'
        # Server Failed
        mock_result = mock.Mock()
        mock_result.status_code = 500
        mock_result.content = "500 server error"

        requests_mock.return_value = mock_result

        response = self.system_commands.list_system_commands()
        self.validateResponse(response,
                              title="Error code: %i" % mock_result.status_code,
                              description=mock_result.content,
                              color=COLOR_ERROR)
        requests_mock.assert_called_once()
        requests_mock.reset_mock()

        # Success
        mock_result.content = json.dumps({
            'core': [{'action': 'restart',
                      'command': 'sudo restart',
                      'name': 'Restart'},
                     {'action': 'shutdown',
                      'name': 'Shutdown'}],
            'other': []
        })
        mock_result.status_code = 200

        response = self.system_commands.list_system_commands()
        requests_mock.assert_called_once()
        self.assertEqual('List of system commands', response.embed.title)
        self.assertEqual('To execute a system command, use /systemcommand {command}. '
                         'Where command is similar to "core/restart"',
                         response.embed.description)
        self.assertEqual(2, len(response.embed.textfield))
        self.assertEqual('core/restart - sudo restart', response.embed.textfield[0].text)
        self.assertEqual('Restart', response.embed.textfield[0].title)
        self.assertEqual('core/shutdown', response.embed.textfield[1].text)
        self.assertEqual('Shutdown', response.embed.textfield[1].title)

    @mock.patch('requests.post')
    def test_system_command(self, requests_mock):
        self.system_commands.plugin = mock.Mock()
        self.system_commands.plugin.get_printer_name = mock.Mock()
        self.system_commands.plugin.get_printer_name.return_value = "OctoPrint"
        self.system_commands.plugin.get_settings.return_value.get.return_value = '/'

        # Not enough args
        response = self.system_commands.system_command(['/systemcommand'])
        self.validateResponse(response,
                              title='Wrong number of args',
                              description='/systemcommand {source/command}',
                              color=COLOR_ERROR)

        # Successfully ran
        mock_result = mock.Mock()
        mock_result.status_code = 200

        requests_mock.return_value = mock_result

        response = self.system_commands.system_command(['/systemcommand', 'core/restart'])
        requests_mock.assert_called_once()
        self.validateResponse(response,
                              title='Successfully ran command',
                              description='core/restart',
                              color=COLOR_SUCCESS)

        # Unsuccessful run
        requests_mock.reset_mock()
        requests_mock.return_value = False

        response = self.system_commands.system_command(['/systemcommand', 'core/doesntexist'])
        requests_mock.assert_called_once()
        self.validateResponse(response,
                              title='Failed to run command',
                              description='core/doesntexist',
                              color=COLOR_ERROR)
