import json
import requests

from octoprint_discordremote.command_plugins.abstract_plugin import AbstractPlugin
from octoprint_discordremote.embedbuilder import EmbedBuilder, success_embed, error_embed


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

    def list_system_commands(self):
        api_key = self.plugin.get_settings().global_get(['api', 'key'])
        port = self.plugin.get_settings().global_get(['server', 'port'])
        header = {'X-Api-Key': api_key, 'Content-Type': 'application/json'}

        response = requests.get('http://127.0.0.1:%s/api/system/commands' % port, headers=header)
        if response.status_code != 200:
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title="Error code: %i" % response.status_code, description=response.content)

        builder = EmbedBuilder()
        builder.set_title('List of system commands')
        builder.set_author(name=self.plugin.get_printer_name())
        builder.set_description('To execute a system command, use /systemcommand {command}. '
                                'Where command is similar to "core/restart"')
        data = json.loads(response.content)
        for source in data:
            for comm in data[source]:
                if 'name' not in comm:
                    continue
                comm_name = comm['name']
                comm_description = "%s/%s" % (source, comm['action'])
                if 'command' in comm:
                    comm_description = "%s - %s" % (comm_description, comm['command'])
                builder.add_field(title=comm_name, text=comm_description)
        return None, builder.get_embeds()

    def system_command(self, command):
        if len(command) != 2:
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title='Wrong number of args', description='/systemcommand {source/command}')
        api_key = self.plugin.get_settings().global_get(['api', 'key'])
        port = self.plugin.get_settings().global_get(['server', 'port'])
        header = {'X-Api-Key': api_key, 'Content-Type': 'application/json'}
        if requests.post('http://127.0.0.1:%s/api/system/commands/%s' % (port, command[1]), headers=header):
            return None, success_embed(author=self.plugin.get_printer_name(),
                                       title='Successfully ran command', description=command[1])
        else:
            return None, error_embed(author=self.plugin.get_printer_name(),
                                     title='Failed to run command', description=command[1])
