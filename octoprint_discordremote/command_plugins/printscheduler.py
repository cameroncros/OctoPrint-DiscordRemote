from __future__ import unicode_literals
import requests

from octoprint_discordremote.command_plugins.abstract_plugin import AbstractPlugin
from octoprint_discordremote.embedbuilder import EmbedBuilder, success_embed, error_embed


class PrintSchedulerControl(AbstractPlugin):
    plugin = None

    def __init__(self):
        AbstractPlugin.__init__(self)

    def setup(self, command, plugin):
        self.plugin = plugin
        if self.plugin.get_plugin_manager().get_plugin("printscheduler"):
            command.command_dict["listjobs"] = {
                'cmd': self.printscheduler_status,
                'description': "Get a list of all currently scheduled jobs.\n"
                               "Uses Print Scheduler plugin."
            }

    def printscheduler_status(self):
        data = self.plugin.get_settings().global_get(["plugins", "printscheduler", "scheduled_jobs"])

        builder = EmbedBuilder()
        builder.set_title('Print Scheduler Job List')
        builder.set_author(name=self.plugin.get_printer_name())

        for job in data:
            title = ("Name: %s" % job['name'])
            description = job['start_at']

            builder.add_field(title=title, text=description)

        # Use data in status to build an embed
        return None, builder.get_embeds()
