from __future__ import unicode_literals
import requests
import os

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
            },
            command.command_dict["addjob"] = {
                'cmd': self.printscheduler_add,
                'params': '{path/time}',
                'description': "Add a file to the scheduled jobs.\n"
                               "Uses Print Scheduler plugin."
            },
            command.command_dict["removejob"] = {
                'cmd': self.printscheduler_remove,
                'params': '{path}',
                'description': "Remove a file from the scheduled jobs.\n"
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
        return builder.get_embeds()

    def printscheduler_add(self, params):
        if len(params) != 3:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Wrong number of args', description='%saddjob {path/time}' %
                                                                         self.plugin.get_settings().get(["prefix"]))
        files = self.plugin.get_settings().global_get(["plugins", "printscheduler", "scheduled_jobs"])
        file_path = params[1]
        file_name = os.path.basename(params[1])
        file_start_at = params[2]
        file_to_add = {"name": file_name, "path": file_path, "start_at": file_start_at}
        files.append(file_to_add)
        self.plugin.get_settings().global_set(["plugins", "printscheduler", "scheduled_jobs"], files)

        return success_embed(author=self.plugin.get_printer_name(),
                                       title="Scheduled job %s for %s." % (params[1], params[2]))
