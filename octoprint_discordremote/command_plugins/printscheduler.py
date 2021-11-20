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
            }
            command.command_dict["addjob"] = {
                'cmd': self.addjob,
                'params': "{YYYY-MM-DD} {HH:MM} {path}",
                'description': "Add a file to the scheduled jobs.\n"
                               "Uses Print Scheduler plugin."
            }
            command.command_dict["removejob"] = {
                'cmd': self.removejob,
                'params': "{YYYY-MM-DD} {HH:MM} {path}",
                'description': "Remove a file from the scheduled jobs.\n"
                               "Uses Print Scheduler plugin."
            }

    def listjobs(self):
        data = self.plugin.get_settings().global_get(["plugins", "printscheduler", "scheduled_jobs"])

        builder = EmbedBuilder()
        builder.set_title('Scheduled Jobs')
        builder.set_author(name=self.plugin.get_printer_name())

        for job in data:
            title = "%s: %s" % (job['start_at'], job['name'])
            description = "remove: `/removejob %s %s`" % (job['start_at'], job['path'])

            builder.add_field(title=title, text=description)

        # Use data in status to build an embed
        return builder.get_embeds()

    def addjob(self, params):
        if len(params) < 4:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Wrong number of args',
                               description='%saddjob {YYYY-MM-DD} {HH:MM} {path}' % self.plugin.get_settings().get(["prefix"]))
        try:
            files = list(self.plugin.get_settings().global_get(["plugins", "printscheduler", "scheduled_jobs"]))
            params.pop(0)  # remove the command from params
            file_start_at = "%s %s" % (params.pop(0), params.pop(0))
            file_path = " ".join(params)
            file_name = file_path
            file_to_add = {"name": file_name, "path": file_path, "start_at": file_start_at}
            files.append(file_to_add)
            self.plugin.get_settings().global_set(["plugins", "printscheduler", "scheduled_jobs"], files)
            self.plugin.get_settings().save(trigger_event=True)

            return success_embed(author=self.plugin.get_printer_name(),
                                 title="%s scheduled for %s" % (file_path, file_start_at))
        except Exception as e:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Error',
                               description='%s' % e)

    def removejob(self, params):
        if len(params) < 4:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Wrong number of args',
                               description='%sremovejob {YYYY-MM-DD} {HH:MM} {path}' % self.plugin.get_settings().get(["prefix"]))
        try:
            files = list(self.plugin.get_settings().global_get(["plugins", "printscheduler", "scheduled_jobs"]))
            params.pop(0)  # remove the command from params
            file_start_at = "%s %s" % (params.pop(0), params.pop(0))
            file_path = " ".join(params)
            for file in files:
                if file["path"] == file_path and file["start_at"] == file_start_at:
                    files.remove(file)
            self.plugin.get_settings().global_set(["plugins", "printscheduler", "scheduled_jobs"], files)
            self.plugin.get_settings().save(trigger_event=True)

            return success_embed(author=self.plugin.get_printer_name(),
                                 title="%s unscheduled for %s" % (file_path, file_start_at))
        except Exception as e:
            return error_embed(author=self.plugin.get_printer_name(),
                               title='Error',
                               description='%s' % e)
