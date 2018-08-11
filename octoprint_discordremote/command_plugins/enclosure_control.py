import requests

from octoprint_discordremote.embedbuilder import EmbedBuilder, success_embed, error_embed


class EnclosureControl:
    plugin = None

    def __init__(self):
        pass

    def setup(self, command, plugin):
        self.plugin = plugin
        if self.plugin.get_plugin_manager().get_plugin("enclosure"):
            command.command_dict["/outputon"] = {
                'cmd': self.on,
                'params': "[ID]",
                'description': ("Turn on the selected output.\n"
                                "Uses OctoPrint-Enclosure plugin.\n"
                                "The ID number can be found in the Enclosure tab in OctoPrint settings.\n"
                                "This only supports basic GPIO outputs.")
            }
            command.command_dict["/outputoff"] = {
                'cmd': self.off,
                'params': "[ID]",
                'description': ("Turn off the selected output.\n"
                                "Uses OctoPrint-Enclosure plugin.\n"
                                "The ID number can be found in the Enclosure tab in OctoPrint settings.\n"
                                "This only supports basic GPIO outputs.")
            }
            command.command_dict["/outputstatus"] = {
                'cmd': self.enc_status,
                'description': "Get the status of all configured outputs.\n"
                               "Uses OctoPrint-Enclosure plugin."
            }

    def on(self, params):
        if len(params) > 2:
            return None, error_embed(title='Too many parameters',
                                     description='Should be: /outputon [ID]')

        result = self.api_command("on", params[1])

        data = result.json()

        if data['success']:
            return None, success_embed(title="Turned ID %i on." % int(params[1]))
        return None, error_embed(title="Failed to turn ID %i on." % int(params[1]),
                                 description=str(result.content))

    def off(self, params):
        if len(params) > 2:
            return None, error_embed(title='Too many parameters',
                                     description='Should be: /outputoff [ID]')

        result = self.api_command("off", params[1])
        data = result.json()

        if data['success']:
            return None, success_embed(title="Turned ID %i off." % int(params[1]))
        return None, error_embed(title="Failed to turn ID %i off." % int(params[1]),
                                 description=str(result.content))

    def enc_status(self):
        result = self.api_command("state", -1)
        data = result.json()

        builder = EmbedBuilder()
        builder.set_title('Enclosure Status')

        for file in data:
            title = ("ID: %s" % str(file['index_id']))
            description = str(file['status'])

            builder.add_field(title=title, text=description)

        # Use data in status to build an embed
        return None, builder.get_embeds()

    def api_command(self, command, id):
        api_key = self.plugin.get_settings().global_get(["api", "key"])
        port = int(self.plugin.get_settings().global_get(["server", "port"]))

        id = int(id)
        req = ""
        if command == "on":
            req = "http://127.0.0.1:%i/plugin/enclosure/setIO?status=true&index_id=%i&apikey=%s" % (port, id, api_key)
        elif command == "off":
            req = "http://127.0.0.1:%i/plugin/enclosure/setIO?status=false&index_id=%i&apikey=%s" % (port, id, api_key)
        elif command == "state":
            req = "http://127.0.0.1:%i/plugin/enclosure/getOutputStatus?apikey=%s" % (port, api_key)
        return requests.get(req)
