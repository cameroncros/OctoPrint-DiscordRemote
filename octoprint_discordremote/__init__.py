# coding=utf-8
from __future__ import absolute_import

from datetime import timedelta, datetime

import ipgetter as ipgetter
import octoprint.plugin
import octoprint.settings
from octoprint.server import user_permission
import os
import requests
import socket
import subprocess
from PIL import Image
from io import BytesIO
from requests import ConnectionError
from flask import make_response

from octoprint_discordremote.command import Command
from octoprint_discordremote.embedbuilder import info_embed
from .discord import Discord


class DiscordRemotePlugin(octoprint.plugin.EventHandlerPlugin,
                          octoprint.plugin.StartupPlugin,
                          octoprint.plugin.ShutdownPlugin,
                          octoprint.plugin.SettingsPlugin,
                          octoprint.plugin.AssetPlugin,
                          octoprint.plugin.TemplatePlugin,
                          octoprint.plugin.ProgressPlugin,
                          octoprint.plugin.SimpleApiPlugin):
    discord = None
    command = None
    last_progress_message = None

    def __init__(self):
        # Events definition here (better for intellisense in IDE)
        # referenced in the settings too.
        self.events = {
            "startup": {
                "name": "Octoprint Startup",
                "enabled": True,
                "with_snapshot": False,
                "message": "⏰ I just woke up! What are we gonna print today?\n"
                           "Local IP: {ipaddr} External IP: {externaddr}"
            },
            "shutdown": {
                "name": "Octoprint Shutdown",
                "enabled": True,
                "with_snapshot": False,
                "message": "💤 Going to bed now!"
            },
            "printer_state_operational": {
                "name": "Printer state : operational",
                "enabled": True,
                "with_snapshot": False,
                "message": "✅ Your printer is operational."
            },
            "printer_state_error": {
                "name": "Printer state : error",
                "enabled": True,
                "with_snapshot": False,
                "message": "⚠️ Your printer is in an erroneous state."
            },
            "printer_state_unknown": {
                "name": "Printer state : unknown",
                "enabled": True,
                "with_snapshot": False,
                "message": "❔ Your printer is in an unknown state."
            },
            "printing_started": {
                "name": "Printing process : started",
                "enabled": True,
                "with_snapshot": True,
                "message": "🖨️ I've started printing {file}"
            },
            "printing_paused": {
                "name": "Printing process : paused",
                "enabled": True,
                "with_snapshot": True,
                "message": "⏸️ The printing was paused."
            },
            "printing_resumed": {
                "name": "Printing process : resumed",
                "enabled": True,
                "with_snapshot": True,
                "message": "▶️ The printing was resumed."
            },
            "printing_cancelled": {
                "name": "Printing process : cancelled",
                "enabled": True,
                "with_snapshot": True,
                "message": "🛑 The printing was stopped."
            },
            "printing_done": {
                "name": "Printing process : done",
                "enabled": True,
                "with_snapshot": True,
                "message": "👍 Printing is done! Took about {time_formatted}"
            },
            "printing_failed": {
                "name": "Printing process : failed",
                "enabled": True,
                "with_snapshot": True,
                "message": "👎 Printing has failed! :("
            },
            "printing_progress": {
                "name": "Printing progress",
                "enabled": True,
                "with_snapshot": True,
                "message": "📢 Printing is at {progress}%",
                "step": 10
            },
            "test": {  # Not a real message, but we will treat it as one
                "enabled": True,
                "with_snapshot": True,
                "message": "Hello hello! If you see this message, it means that the settings are correct!"
            },
        }

    def on_after_startup(self):
        self._logger.info("DiscordRemote is started !")
        if self.command is None:
            self.command = Command(self)
        # Configure discord
        if self.discord is None:
            self.discord = Discord()
        self.discord.configure_discord(self._settings.get(['bottoken'], merged=True),
                                       self._settings.get(['channelid'], merged=True),
                                       self._settings.get(['allowedusers'], merged=True),
                                       self._logger,
                                       self.command,
                                       self.update_discord_status)

    # ShutdownPlugin mixin
    def on_shutdown(self):
        self._logger.info("DiscordRemote is shutting down.")
        self.discord.shutdown_discord()
        self._logger.info("Discord bot has excited cleanly.")

    # SettingsPlugin mixin
    def get_settings_defaults(self):
        return {
            'bottoken': "",
            'channelid': "",
            'allowedusers': "",
            'show_local_ip': True,
            'show_external_ip': True,
            'events': self.events,
            'allow_scripts': False,
            'script_before': '',
            'script_after': ''
        }

    # Restricts some paths to some roles only
    def get_settings_restricted_paths(self):
        # settings.events.tests is a false message, so we should never see it as configurable.
        # settings.bottoken and channelid are admin only.
        return dict(never=[["events", "test"]],
                    admin=[["bottoken"],
                           ["channelid"],
                           ["allowedusers"],
                           ["show_local_ip"],
                           ["show_external_ip"],
                           ['script_before'],
                           ['script_after']])

    # AssetPlugin mixin
    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return dict(
            js=["js/discordremote.js"],
            css=["css/discordremote.css"],
            less=["less/discordremote.less"]
        )

    # TemplatePlugin mixin
    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    # Softwareupdate hook
    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
        # for details.
        return dict(
            discordremote=dict(
                displayName="DiscordRemote Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="cameroncros",
                repo="OctoPrint-DiscordRemote",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/cameroncros/OctoPrint-DiscordRemote/archive/{target_version}.zip"
            )
        )

    # EventHandlerPlugin hook
    def on_event(self, event, payload):

        if event == "Startup":
            return self.notify_event("startup")

        if event == "Shutdown":
            return self.notify_event("shutdown")

        if event == "PrinterStateChanged":
            if payload["state_id"] == "OPERATIONAL":
                return self.notify_event("printer_state_operational")
            elif payload["state_id"] == "ERROR":
                return self.notify_event("printer_state_error")
            elif payload["state_id"] == "UNKNOWN":
                return self.notify_event("printer_state_unknown")

        if event == "PrintStarted":
            return self.notify_event("printing_started", payload)
        if event == "PrintPaused":
            return self.notify_event("printing_paused", payload)
        if event == "PrintResumed":
            return self.notify_event("printing_resumed", payload)
        if event == "PrintCancelled":
            return self.notify_event("printing_cancelled", payload)

        if event == "PrintDone":
            payload['time_formatted'] = str(timedelta(seconds=int(payload["time"])))
            return self.notify_event("printing_done", payload)

        return True

    def on_print_progress(self, location, path, progress):
        self.notify_event("printing_progress", {"progress": progress})

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        self._logger.info("Settings have saved. Send a test message...")
        # Configure discord
        if self.command is None:
            self.command = Command(self)

        if self.discord is None:
            self.discord = Discord()

        self.discord.configure_discord(self._settings.get(['bottoken'], merged=True),
                                       self._settings.get(['channelid'], merged=True),
                                       self._settings.get(['allowedusers'], merged=True),
                                       self._logger,
                                       self.command,
                                       self.update_discord_status)
        self.notify_event("test")

    # SimpleApiPlugin mixin
    def get_api_commands(self):
        return dict(
            executeCommand=['args']
        )

    def on_api_command(self, command, data):
        if not user_permission.can():
            return make_response("Insufficient rights", 403)

        if command == 'executeCommand':
            self.execute_command(data)

    def execute_command(self, data):
        args = ""
        if 'args' in data:
            args = data['args']

        snapshots, embeds = self.command.parse_command(data['args'])
        self.discord.send(snapshots=snapshots, embeds=embeds)

    def notify_event(self, event_id, data=None):
        if data is None:
            data = {}
        if event_id not in self.events:
            self._logger.error("Tried to notify on non-existant eventID : ", event_id)
            return False

        tmp_config = self._settings.get(["events", event_id], merged=True)

        if not tmp_config["enabled"]:
            self._logger.debug("Event {} is not enabled. Returning gracefully".format(event_id))
            return False

        # Store IP address for message
        data['ipaddr'] = self.get_ip_address()
        data['externaddr'] = self.get_external_ip_address()

        # Special case for progress eventID : we check for progress and steps
        if event_id == 'printing_progress':
            # Skip if just started
            if int(data["progress"]) == 0:
                return False

            # Skip if not a multiple of the given interval
            if int(data["progress"]) % int(tmp_config["step"]) != 0:
                return False

            # Always send last message, and reset timer.
            if int(data["progress"]) == 100:
                self.last_progress_message = None

            # Otherwise work out if time since last message has passed.
            try:
                min_progress_time = timedelta(seconds=int(tmp_config["timeout"]))
                if self.last_progress_message is not None \
                        and self.last_progress_message > (datetime.now() - min_progress_time):
                    return False
            except ValueError:
                pass
            except KeyError:
                pass

            self.last_progress_message = datetime.now()

        return self.send_message(event_id, tmp_config["message"].format(**data), tmp_config["with_snapshot"])

    @staticmethod
    def get_ip_address():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            return s.getsockname()[0]
        except Exception as e:
            print(e)
            return '127.0.0.1'
        finally:
            s.close()

    @staticmethod
    def get_external_ip_address():
        return str(ipgetter.myip())

    def exec_script(self, event_name, which=""):

        # I want to be sure that the scripts are allowed by the special configuration flag
        scripts_allowed = self._settings.get(["allow_scripts"], merged=True)
        if scripts_allowed is None or scripts_allowed is False:
            return ""

        # Finding which one should be used.
        script_to_exec = None
        if which == "before":
            script_to_exec = self._settings.get(["script_before"], merged=True)

        elif which == "after":
            script_to_exec = self._settings.get(["script_after"], merged=True)

        # Finally exec the script
        out = ""
        self._logger.info("{}:{} File to start: '{}'".format(event_name, which, script_to_exec))

        try:
            if script_to_exec is not None and len(script_to_exec) > 0 and os.path.exists(script_to_exec):
                out = subprocess.check_output(script_to_exec)
        except (OSError, subprocess.CalledProcessError) as err:
            out = err
        finally:
            self._logger.info("{}:{} > Output: '{}'".format(event_name, which, out))
            return out

    def send_message(self, event_id, message, with_snapshot=False):
        # exec "before" script if any
        self.exec_script(event_id, "before")

        # Get snapshot if asked for
        snapshots = None
        if with_snapshot:
            snapshots = self.get_snapshot()

        # Send to Discord bot (Somehow events can happen before discord bot has been created and initialised)
        if self.discord is None:
            self.discord = Discord()

        out = self.discord.send(snapshots=snapshots, embeds=info_embed(message))

        # exec "after" script if any
        self.exec_script(event_id, "after")

        return out

    def get_snapshot(self):
        snapshot = None
        snapshot_url = self._settings.global_get(["webcam", "snapshot"])
        if snapshot_url is None:
            return None
        if "http" in snapshot_url:
            try:
                snapshot_call = requests.get(snapshot_url)
                if not snapshot_call:
                    return None
                snapshot = BytesIO(snapshot_call.content)
            except ConnectionError:
                return None
        if snapshot_url.startswith("file://"):
            snapshot = open(snapshot_url.partition('file://')[2], "rb")

        if snapshot is None:
            return None

        # Get the settings used for streaming to know if we should transform the snapshot
        must_flip_h = self._settings.global_get_boolean(["webcam", "flipH"])
        must_flip_v = self._settings.global_get_boolean(["webcam", "flipV"])
        must_rotate = self._settings.global_get_boolean(["webcam", "rotate90"])

        # Only call Pillow if we need to transpose anything
        if must_flip_h or must_flip_v or must_rotate:
            img = Image.open(snapshot)

            self._logger.info(
                "Transformations : FlipH={}, FlipV={} Rotate={}".format(must_flip_h, must_flip_v, must_rotate))

            if must_flip_h:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)

            if must_flip_v:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)

            if must_rotate:
                img = img.transpose(Image.ROTATE_90)

            new_image = BytesIO()
            img.save(new_image, 'png')

            return [new_image]
        return [snapshot]

    def update_discord_status(self, connected):
        self._plugin_manager.send_plugin_message(self._identifier, dict(isConnected=connected))


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "DiscordRemote"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = DiscordRemotePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
