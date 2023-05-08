from __future__ import unicode_literals

from threading import Thread
import time
from typing import Optional

from discordshim import DiscordShim


class Presence:
    def __init__(self, discord: DiscordShim):
        self.presence_cycle_id: int = 0
        self.presence_thread: Optional[Thread] = None
        self.status = ""
        self.enabled = True
        self.cycle_time = 5
        self.command_prefix = '/'
        self.discord = discord

    def configure_presence(self):
        # Setup presence thread
        if not self.presence_thread or not self.presence_thread.is_alive():
            self.presence_thread = Thread(target=self.presence)
            self.presence_thread.start()

    def presence(self):
        presence_cycle = {
            0: "{}help".format(self.command_prefix),
            1: self.status
        }
        while True:
            if self.enabled:
                self.presence_cycle_id += 1
                if self.presence_cycle_id == len(presence_cycle):
                    self.presence_cycle_id = 0

                self.discord.update_presence(presence_cycle[self.presence_cycle_id])
            else:
                self.discord.update_presence(None)

            time.sleep(self.cycle_time)
