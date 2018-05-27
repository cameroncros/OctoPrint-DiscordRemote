import json
import requests


class PsuControl:
    plugin = None

    def __init__(self):
        pass

    def setup(self, command, plugin):
        self.plugin = plugin
        if self.plugin._plugin_manager.get_plugin("psucontrol"):
            command.command_dict["/poweron"] = {
                                         'cmd': self.poweron,
                                         'description': "Turn on the printers power supply. Uses PSUControl plugin."
                                     }
            command.command_dict["/poweroff"] = {
                                         'cmd': self.poweroff,
                                         'description': "Turn off the printers power supply. Uses PSUControl plugin."
                                     }
            command.command_dict["/powerstatus"] = {
                                         'cmd': self.powerstatus,
                                         'description': "Get the status of the power supply. Uses PSUControl plugin."
                                     }

    def poweron(self):
        result = self.api_command("turnPSUOn")
        if result:
            return "Turned PSU on", None
        return "Failed to turn PSU on: %s" % str(result.content), None

    def poweroff(self):
        result = self.api_command("turnPSUOff")
        if result:
            return "Turned PSU off", None
        return "Failed to turn PSU off: %s" % str(result.content), None

    def powerstatus(self):
        result = self.api_command("getPSUState")
        if result:
            message = "PSU is OFF"
            if json.loads(result.content)['isPSUOn']:
                message = "PSU is ON"
            return message, None
        return "Failed to get PSU status: %s" % str(result.content), None

    def api_command(self, command):
        api_key = self.plugin._settings.global_get(["api", "key"])
        port = self.plugin._settings.global_get(["server", "port"])
        header = {'X-Api-Key': api_key, 'Content-Type': "application/json"}
        data = json.dumps({'command': command})
        return requests.post("http://127.0.0.1:%s/api/plugin/psucontrol" % port, headers=header, data=data)
