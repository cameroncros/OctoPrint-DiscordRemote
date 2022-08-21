from __future__ import unicode_literals
from logging import disable

from threading import Thread
import time
from typing import Optional

import humanfriendly

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from octoprint_discordremote import DiscordRemotePlugin
    from octoprint_discordremote import DiscordImpl


class Presence:
    def __init__(self):
        self.plugin: Optional['DiscordRemotePlugin'] = None
        self.discord: Optional['DiscordImpl'] = None
        self.presence_cycle_id: int = 0
        self.presence_thread: Optional[Thread] = None
        self.last_status = None

    def configure_presence(self, plugin: 'DiscordRemotePlugin', discord: 'DiscordImpl'):
        self.plugin = plugin
        self.discord = discord

        # Setup presence thread
        if not self.presence_thread or not self.presence_thread.is_alive():
            self.discord.logger.info("Starting Presence thread")
            self.presence_thread = Thread(target=self.presence)
            self.presence_thread.start()

    def update(self, status, msg):
        if not status == self.last_status:
            self.discord.update_presence(status, msg)
            self.last_status = status

    def generate_status(self):
        if self.plugin.get_printer().is_operational():
            if self.plugin.get_printer().is_printing() and not self.plugin.get_printer().is_ready():
                job_name = self.plugin.get_printer().get_current_data()['job']['file']['name']
                job_percent = self.plugin.get_printer().get_current_data()['progress']['completion']
                return ["online", "{}% of {} complete".format(
                                                  humanfriendly.format_number(job_percent, num_decimals=2),
                                                  job_name)]
            else:
                return ["idle", " and waiting"]
        else:
            return ["offline", "for printer to come online"]

    def presence(self):
        while not self.discord.shutdown_event.is_set():
            if self.plugin.get_settings().get(['presence']):
                [status, presence] = self.generate_status()
                self.update(status, presence)
            else:
                self.update("online", None)

            for i in range(int(self.plugin.get_settings().get(['presence_cycle_time']))):
                if not self.discord.shutdown_event.is_set():
                    time.sleep(1)
