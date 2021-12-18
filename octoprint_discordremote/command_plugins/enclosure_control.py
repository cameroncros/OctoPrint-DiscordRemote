from __future__ import unicode_literals
import requests

from octoprint_discordremote.command_plugins.abstract_plugin import AbstractPlugin
from octoprint_discordremote.embedbuilder import EmbedBuilder, success_embed, error_embed


class EnclosureControl(AbstractPlugin):
    plugin = None

    def __init__(self):
        AbstractPlugin.__init__(self)

    def setup(self, command, plugin):
        self.plugin = plugin
        if self.plugin.get_plugin_manager().get_plugin("enclosure"):
            command.command_dict["outputon"] = {
                'cmd': self.on,
                'params': "{ID}",
                'description': ("Turn on the selected output.\n"
                                "Uses OctoPrint-Enclosure plugin.\n"
                                "The ID number can be found in the Enclosure tab in OctoPrint settings.\n"
                                "This only supports basic GPIO outputs.")
            }
            command.command_dict["outputoff"] = {
                'cmd': self.off,
                'params': "{ID}",
                'description': ("Turn off the selected output.\n"
                                "Uses OctoPrint-Enclosure plugin.\n"
                                "The ID number can be found in the Enclosure tab in OctoPrint settings.\n"
                                "This only supports basic GPIO outputs.")
            }
            command.command_dict["outputstatus"] = {
                'cmd': self.enc_status,
                'description': "Get the status of all configured outputs.\n"
                               "Uses OctoPrint-Enclosure plugin."
            }

    def on(self, params):
        if len(params) > 2:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Too many parameters',
                               description='Should be: %soutputon {ID}' % self.plugin.get_settings().get(
                                   ["prefix"]))
        elif len(params) < 2:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Missing parameters',
                               description='Should be: %soutputon {ID}' % self.plugin.get_settings().get(
                                   ["prefix"]))

        result = self.api_command("on", params[1])

        data = result.json()

        if data['success']:
            return success_embed(author=self.plugin.get_printer_name(),
                                 title="Turned ID %i on." % int(params[1]))
        return error_embed(author=self.plugin.get_printer_name(),
                           title="Failed to turn ID %i on." % int(params[1]),
                           description=result.content)

    def off(self, params):
        if len(params) > 2:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Too many parameters',
                               description='Should be: %soutputoff {ID}' % self.plugin.get_settings().get(
                                   ["prefix"]))
        elif len(params) < 2:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Missing parameters',
                               description='Should be: %soutputoff {ID}' % self.plugin.get_settings().get(
                                   ["prefix"]))

        result = self.api_command("off", params[1])
        data = result.json()

        if data['success']:
            return success_embed(author=self.plugin.get_printer_name(),
                                 title="Turned ID %i off." % int(params[1]))
        return error_embed(author=self.plugin.get_printer_name(),
                           title="Failed to turn ID %i off." % int(params[1]),
                           description=result.content)

    def enc_status(self):
        result = self.api_command("state", -1)
        data = result.json()

        builder = EmbedBuilder()
        builder.set_title('Enclosure Status')
        builder.set_author(name=self.plugin.get_printer_name())

        for file in data:
            title = ("ID: %s" % file['index_id'])
            description = file['status']

            builder.add_field(title=title, text=description)

        # Use data in status to build an embed
        return builder.get_embeds()

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
