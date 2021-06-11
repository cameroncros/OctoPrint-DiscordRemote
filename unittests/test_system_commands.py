import json
from collections import OrderedDict
from mock import mock

from octoprint_discordremote.command_plugins.system_commands import SystemCommands
from octoprint_discordremote.embedbuilder import COLOR_SUCCESS, COLOR_ERROR
from unittests.discordremotetestcase import DiscordRemoteTestCase


class TestSystemCommand(DiscordRemoteTestCase):
    def setUp(self):
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

        # Server Failed
        mock_result = mock.Mock()
        mock_result.status_code = 500
        mock_result.content = "500 server error"

        requests_mock.return_value = mock_result

        messages = self.system_commands.list_system_commands()
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertBasicEmbed(embed,
                              title="Error code: %i" % mock_result.status_code,
                              description=mock_result.content,
                              color=COLOR_ERROR,
                              author=self.system_commands.plugin.get_printer_name.return_value)
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

        messages = self.system_commands.list_system_commands()
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        requests_mock.assert_called_once()
        self.assertIsNone(snapshot)
        self.assertEqual('List of system commands', embed.title)
        self.assertEqual('To execute a system command, use /systemcommand {command}. '
                         'Where command is similar to "core/restart"',
                         embed.description)
        self.assertEqual(2, len(embed.fields))
        self.assertEqual('core/restart - sudo restart', embed.fields[0].value)
        self.assertEqual('Restart', embed.fields[0].name)
        self.assertEqual('core/shutdown', embed.fields[1].value)
        self.assertEqual('Shutdown', embed.fields[1].name)

    @mock.patch('requests.post')
    def test_system_command(self, requests_mock):
        self.system_commands.plugin = mock.Mock()
        self.system_commands.plugin.get_printer_name = mock.Mock()
        self.system_commands.plugin.get_printer_name.return_value = "OctoPrint"

        # Not enough args
        messages = self.system_commands.system_command(['/systemcommand'])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        self.assertIsNone(snapshot)
        self.assertBasicEmbed(embed,
                              title='Wrong number of args',
                              description='/systemcommand {source/command}',
                              color=COLOR_ERROR,
                              author=self.system_commands.plugin.get_printer_name.return_value)

        # Successfully ran
        mock_result = mock.Mock()
        mock_result.status_code = 200

        requests_mock.return_value = mock_result

        messages = self.system_commands.system_command(['/systemcommand', 'core/restart'])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        requests_mock.assert_called_once()
        self.assertIsNone(snapshot)
        self.assertBasicEmbed(embed,
                              title='Successfully ran command',
                              description='core/restart',
                              color=COLOR_SUCCESS,
                              author=self.system_commands.plugin.get_printer_name.return_value)

        # Unsuccessful run
        requests_mock.reset_mock()
        requests_mock.return_value = False

        messages = self.system_commands.system_command(['/systemcommand', 'core/doesntexist'])
        self.assertEqual(1, len(messages))
        embed, snapshot = messages[0]
        requests_mock.assert_called_once()
        self.assertIsNone(snapshot)
        self.assertBasicEmbed(embed,
                              title='Failed to run command',
                              description='core/doesntexist',
                              color=COLOR_ERROR,
                              author=self.system_commands.plugin.get_printer_name.return_value)
