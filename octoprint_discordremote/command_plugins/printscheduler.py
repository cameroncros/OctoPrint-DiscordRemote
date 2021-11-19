from __future__ import unicode_literals
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
                'cmd': self.listjobs,
                'description': "Get a list of all currently scheduled jobs.\n"
                               "Uses Print Scheduler plugin."
            },
            command.command_dict["addjob"] = {
                'cmd': self.addjob,
                'params': '{path} {timestamp}',
                'description': "Add a file to the scheduled jobs.\n"
                "Uses Print Scheduler plugin."
            },
            command.command_dict["removejob"] = {
                'cmd': self.removejob,
                'params': '{path} {timestamp}',
                'description': "Remove a file from the scheduled jobs.\n"
                               "Uses Print Scheduler plugin."
            }

    def listjobs(self):
        data = self.plugin.get_settings().global_get(["plugins", "printscheduler", "scheduled_jobs"])

        builder = EmbedBuilder()
        builder.set_title('Scheduled Jobs')
        builder.set_author(name=self.plugin.get_printer_name())

        for job in data:
            title = ("Name: %s" % job['name'])
            description = job['start_at']

            builder.add_field(title=title, text=description)

        # Use data in status to build an embed
        return builder.get_embeds()

    def addjob(self, params):
        if len(params) != 3:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Wrong number of args',
                               description='%saddjob {path} {timestamp}' % self.plugin.get_settings().get(["prefix"]))
        files = list(self.plugin.get_settings().global_get(["plugins", "printscheduler", "scheduled_jobs"]))
        file_path = params[1]
        file_name = os.path.basename(params[1])
        file_start_at = params[2]
        file_to_add = {"name": file_name, "path": file_path, "start_at": file_start_at}
        files.append(file_to_add)
        self.plugin.get_settings().global_set(["plugins", "printscheduler", "scheduled_jobs"], files)

        return success_embed(author=self.plugin.get_printer_name(),
                             title="Scheduled Job Added",
                             description="%s: %s" % (params[2], params[1]))

    def removejob(self, params):
        if len(params) != 2:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Wrong number of args',
                               description='%sremovejob {path} {timestamp}' % self.plugin.get_settings().get(["prefix"]))
        files = list(self.plugin.get_settings().global_get(["plugins", "printscheduler", "scheduled_jobs"]))
        for file in files:
            if file["path"] == params[1] and file["start_at"] == params[2]:
                files.remove(file)
        self.plugin.get_settings().global_set(["plugins", "printscheduler", "scheduled_jobs"], files)

        return success_embed(author=self.plugin.get_printer_name(),
                             title="Scheduled Job Removed",
                             description="%s: %s" % (params[2], params[1]))
