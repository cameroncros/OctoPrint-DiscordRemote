import json
import requests

from octoprint_discordremote.embedbuilder import success_embed, error_embed, info_embed


class EnclosureControl:
    plugin = None

    def __init__(self):
        pass

    def setup(self, command, plugin):
        self.plugin = plugin
        if self.plugin.get_plugin_manager().get_plugin("enclosure"):
            command.command_dict["/encOn"] = {
                'cmd': self.on,
                'params': "[ID]",
                'description': ("Turn on the selected output.\nUses OctoPrint-Enclosure plugin. "
                                "\nThe ID number can be found in the Enclosure tab in OctoPrint settings. "
                                "\nThis only supports basic GPIO outputs.")
            }
            command.command_dict["/encOff"] = {
                'cmd': self.off,
                'params': "[ID]",
                'description': ("Turn off the selected output.\nUses OctoPrint-Enclosure plugin. "
                                "\nThe ID number can be found in the Enclosure tab in OctoPrint settings. "
                                "\nThis only supports basic GPIO outputs.")
            }
            command.command_dict["/encStatus"] = {
                'cmd': self.encStatus,
                'description': "Get the status of all configured outputs.\nUses OctoPrint-Enclosure plugin."
            }

    def on(self, params):
        if len(params) > 2:
            return None, error_embed(title='Too many parameters',
                                     description='Should be: /encOn [ID]')

        result = self.api_command("on", params[1])

        data = result.json()

        if data['success']:
            return None, success_embed(title="Turned ID " + params[1] + " on.")
        return None, error_embed(title="Failed to turn ID " + params[1] + " on.", description=str(result.content))

    def off(self, params):
        if len(params) > 1:
            return None, error_embed(title='Too many parameters',
                                     description='Should be: /encOff [ID]')

        result = self.api_command("off", params[1])
        data = result.json()

        if data['success']:
            return None, success_embed(title="Turned ID " + params[1] + " off.")
        return None, error_embed(title="Failed to turn ID " + params[1] + " off.", description=str(result.content))

    def encStatus(self):
        result = self.api_command("state", -1)
        data = result.json()

        status = ""

        for x in data:
            status += ("ID " + str(x['index_id']) + ": " + str(x['status']) + "\n")

        # Use data in status to build an embed
        return None, info_embed(title="Enclosure Status", description=status)

    def api_command(self, command, id):
        api_key = self.plugin.get_settings().global_get(["api", "key"])
        port = self.plugin.get_settings().global_get(["server", "port"])

        if command == "on":
            req = ("http://127.0.0.1:%s/plugin/enclosure/setIO?status=true&index_id=" % port) + id + "&apikey=" + api_key
        elif command == "off":
            req = ("http://127.0.0.1:%s/plugin/enclosure/setIO?status=false&index_id=" % port) + id + "&apikey=" + api_key
        elif command == "state":
            req = ("http://127.0.0.1:%s/plugin/enclosure/getOutputStatus?apikey=" % port) + str(api_key)
        return requests.get(req)
