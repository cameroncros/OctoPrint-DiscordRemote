from __future__ import unicode_literals
import json
import requests

from octoprint_discordremote.command_plugins.abstract_plugin import AbstractPlugin
from octoprint_discordremote.proto.messages_pb2 import Response
from octoprint_discordremote.responsebuilder import success_embed, error_embed, info_embed


class PsuControl(AbstractPlugin):
    plugin = None

    def __init__(self):
        pass

    def setup(self, command, plugin):
        self.plugin = plugin
        if self.plugin.get_plugin_manager().get_plugin("psucontrol"):
            command.command_dict["poweron"] = {
                'cmd': self.poweron,
                'description': "Turn on the printers PSU.\nUses PSUControl plugin."
            }
            command.command_dict["poweroff"] = {
                'cmd': self.poweroff,
                'description': "Turn off the printers PSU.\nUses PSUControl plugin."
            }
            command.command_dict["powerstatus"] = {
                'cmd': self.powerstatus,
                'description': "Get the status of the PSU.\nUses PSUControl plugin."
            }

    def poweron(self) -> Response:
        result = self.api_command("turnPSUOn")
        if result:
            return success_embed(author=self.plugin.get_printer_name(),
                                 title="Turned PSU on")
        return error_embed(author=self.plugin.get_printer_name(),
                           title="Failed to turn PSU on", description=result.content)

    def poweroff(self) -> Response:
        result = self.api_command("turnPSUOff")
        if result:
            return success_embed(author=self.plugin.get_printer_name(),
                                 title="Turned PSU off")
        return error_embed(author=self.plugin.get_printer_name(),
                           title="Failed to turn PSU off", description=result.content)

    def powerstatus(self) -> Response:
        result = self.api_command("getPSUState")
        if result:
            message = "PSU is OFF"
            if json.loads(result.content)['isPSUOn']:
                message = "PSU is ON"
            return info_embed(author=self.plugin.get_printer_name(),
                              title=message)
        return error_embed(author=self.plugin.get_printer_name(),
                           title="Failed to get PSU status", description=result.content)

    def api_command(self, command) -> Response:
        api_key = self.plugin.get_settings().global_get(["api", "key"])
        port = self.plugin.get_settings().global_get(["server", "port"])
        header = {'X-Api-Key': api_key, 'Content-Type': "application/json"}
        data = json.dumps({'command': command})
        return requests.post("http://127.0.0.1:%s/api/plugin/psucontrol" % port, headers=header, data=data)
