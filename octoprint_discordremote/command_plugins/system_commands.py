from __future__ import unicode_literals

import json

import requests

from octoprint_discordremote.command_plugins.abstract_plugin import AbstractPlugin
from octoprint_discordremote.proto.messages_pb2 import TextField, Response, EmbedContent
from octoprint_discordremote.responsebuilder import success_embed, error_embed


class SystemCommands(AbstractPlugin):
    plugin = None

    def __init__(self):
        AbstractPlugin.__init__(self)

    def setup(self, command, plugin):
        self.plugin = plugin
        command.command_dict['listsystemcommands'] = {
            'cmd': self.list_system_commands,
            'description': 'List all registered system commands'
        }

        command.command_dict['systemcommand'] = {
            'params': '{source/command}',
            'cmd': self.system_command,
            'description': 'Execute a system command'
        }

    def list_system_commands(self) -> Response:
        api_key = self.plugin.get_settings().global_get(['api', 'key'])
        port = self.plugin.get_settings().global_get(['server', 'port'])
        header = {'X-Api-Key': api_key, 'Content-Type': 'application/json'}

        response = requests.get('http://127.0.0.1:%s/api/system/commands' % port, headers=header)
        if response.status_code != 200:
            return error_embed(author=self.plugin.get_printer_name(),
                               title="Error code: %i" % response.status_code, description=response.content)

        builder = EmbedContent()
        builder.title = 'List of system commands'
        builder.author = self.plugin.get_printer_name()
        builder.description = f'To execute a system command, use {self.plugin.get_settings().get(["prefix"])}systemcommand {{command}}.' \
                              f' Where command is similar to "core/restart"'
        data = json.loads(response.content)
        for source in data:
            for comm in data[source]:
                if 'name' not in comm:
                    continue
                comm_name = comm['name']
                comm_description = "%s/%s" % (source, comm['action'])
                if 'command' in comm:
                    comm_description = "%s - %s" % (comm_description, comm['command'])
                builder.textfield.append(TextField(title=comm_name, text=comm_description))
        return Response(embed=builder)


    def system_command(self, command) -> Response:
        if len(command) != 2:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Wrong number of args', description='%ssystemcommand {source/command}' %
                                                                         self.plugin.get_settings().get(["prefix"]))
        api_key = self.plugin.get_settings().global_get(['api', 'key'])
        port = self.plugin.get_settings().global_get(['server', 'port'])
        header = {'X-Api-Key': api_key, 'Content-Type': 'application/json'}
        if requests.post('http://127.0.0.1:%s/api/system/commands/%s' % (port, command[1]), headers=header):
            return success_embed(author=self.plugin.get_printer_name(),
                                 title='Successfully ran command', description=command[1])
        else:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Failed to run command', description=command[1])
