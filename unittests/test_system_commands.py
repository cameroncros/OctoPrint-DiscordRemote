import json
from collections import OrderedDict
from mock import mock
from unittest import TestCase

from octoprint_discordremote.command_plugins.system_commands import SystemCommands
from octoprint_discordremote.embedbuilder import COLOR_SUCCESS, COLOR_ERROR


class TestSystemCommand(TestCase):
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

        mock_result = mock.Mock()
        mock_result.content = json.dumps({
            'core': [{'action': 'restart',
                      'command': 'sudo restart',
                      'name': 'Restart'},
                     {'action': 'shutdown',
                      'name': 'Shutdown'}],
            'other': []
        })
        mock_result.status_code = 200

        requests_mock.return_value = mock_result

        snapshots, embeds = self.system_commands.list_system_commands()
        requests_mock.assert_called_once()
        self.assertIsNone(snapshots)
        self.assertEqual(1, len(embeds))
        embed = embeds[0]
        self.assertEqual('List of system commands', embed.title)
        self.assertEqual('To execute a system command, use /systemcommand {command}. '
                         'Where command is similar to "core/restart"',
                         embed.description)
        self.assertEqual(2, len(embed.fields))
        self.assertEqual('core/restart - sudo restart', embed.fields[0]['value'])
        self.assertEqual('Restart', embed.fields[0]['name'])
        self.assertEqual('core/shutdown', embed.fields[1]['value'])
        self.assertEqual('Shutdown', embed.fields[1]['name'])
        
    @mock.patch('requests.post')
    def test_system_command(self, requests_mock):
        self.system_commands.plugin = mock.Mock()

        # Successfully ran
        mock_result = mock.Mock()
        mock_result.status_code = 200

        requests_mock.return_value = mock_result
        
        snapshots, embeds = self.system_commands.system_command('core/restart')
        
        requests_mock.assert_called_once()
        self.assertIsNone(snapshots)
        self.assertEqual(1, len(embeds))
        embed = embeds[0]
        
        self.assertEqual('Successfully ran command', embed.title)
        self.assertEqual('core/restart', embed.description)
        self.assertEqual(0, len(embed.fields))
        self.assertEqual(COLOR_SUCCESS, embed.color)

        # Unsuccessful run
        requests_mock.reset_mock()
        requests_mock.return_value = False

        snapshots, embeds = self.system_commands.system_command('core/doesntexist')

        requests_mock.assert_called_once()
        self.assertIsNone(snapshots)
        self.assertEqual(1, len(embeds))
        embed = embeds[0]

        self.assertEqual('Failed to run command', embed.title)
        self.assertEqual('core/doesntexist', embed.description)
        self.assertEqual(0, len(embed.fields))
        self.assertEqual(COLOR_ERROR, embed.color)
