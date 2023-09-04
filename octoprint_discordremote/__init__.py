# coding=utf-8
from __future__ import absolute_import

import logging
import os
import socket
import subprocess
import time
from base64 import b64decode
from datetime import timedelta, datetime
from io import BytesIO
from threading import Thread, Event
from typing import Optional

import humanfriendly
import octoprint.plugin
import octoprint.settings
import requests
from PIL import Image
from flask import make_response
from octoprint.server import user_permission
from requests import ConnectionError

from octoprint_discordremote.command import Command
from .discordlink import DiscordLink
from .libs import ipgetter
from .proto.messages_pb2 import EmbedContent, ProtoFile, Response, Presence


class DiscordRemotePlugin(octoprint.plugin.EventHandlerPlugin,
                          octoprint.plugin.StartupPlugin,
                          octoprint.plugin.ShutdownPlugin,
                          octoprint.plugin.SettingsPlugin,
                          octoprint.plugin.AssetPlugin,
                          octoprint.plugin.TemplatePlugin,
                          octoprint.plugin.ProgressPlugin,
                          octoprint.plugin.SimpleApiPlugin):

    # extend Octoprint's allowed file types by .zip, .zip.001, .zip.002, ...)
    def get_extension_tree(self, *args, **kwargs):
        allowed_list = ['zip']
        for i in range(0, 100):
            allowed_list.append(str(i).zfill(3))
        return dict(machinecode=dict(discordremote=allowed_list))


    def __init__(self):
        self.discord: Optional[DiscordLink] = None
        self.command: Optional[Command] = None
        self.last_progress_message = None
        self.last_progress_percent = 0
        self.is_muted = False
        self.periodic_signal = None
        self.periodic_thread = None
        self.presence = None
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
                "message": "🖨️ I've started printing {path}"
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
                "name": "Printing progress (Percentage)",
                "enabled": True,
                "with_snapshot": True,
                "message": "📢 Printing is at {progress}%",
                "step": 10
            },
            "printing_progress_periodic": {
                "name": "Printing progress (Periodic)",
                "enabled": False,
                "with_snapshot": True,
                "message": "📢 Printing is at {progress}%",
                "period": 300
            },
            "test": {  # Not a real message, but we will treat it as one
                "enabled": True,
                "with_snapshot": True,
                "message": "Hello hello! If you see this message, it means that the settings are correct!"
            },
            "gcode_sent": {
                "name": "Printing process : Specific gcode sent",
                "enabled": False,
                "with_snapshot": True,
                "message": "📢 {gcode} gcode sent!",
                "gcodes": "M600"
            },
        }
        self.permissions = {
            '1': {'users': '*', 'commands': ''},
            '2': {'users': '', 'commands': ''},
            '3': {'users': '', 'commands': ''},
            '4': {'users': '', 'commands': ''},
            '5': {'users': '', 'commands': ''}
        }

    def configure_discord(self, send_test=False):
        # Configure discord
        if self.command is None:
            self.command = Command(self)

        if self.discord:
            self.discord.shutdown_discord()

        shimaddress = self._settings.get(['shimaddress'], merged=True)
        if shimaddress is None or len(shimaddress) == 0:
            shimaddress = 'opdrshim.uk:23416'
        parts = shimaddress.split(':')
        shimaddress = (parts[0], int(parts[1]))
        self.discord = DiscordLink(shimaddress,
                                   channel_id=self._settings.get(['channelid'], merged=True),
                                   command=self.command,
                                   logger=self._logger,
                                   presence_enabled=self._settings.get(['presence'], merged=True),
                                   cycle_time=self._settings.get(['presence_cycle_time'], merged=True),
                                   command_prefix=self._settings.get(['prefix'], merged=True))
        self.discord.start_discord()

        self.notify_event("startup")
        if send_test:
            self.notify_event("test")

    def on_after_startup(self):
        # Use a different log file for DiscordRemote, as it is very noisy.
        self._logger = logging.getLogger("octoprint.plugins.discordremote")
        from octoprint.logging.handlers import CleaningTimedRotatingFileHandler
        hdlr = CleaningTimedRotatingFileHandler(
            self._settings.get_plugin_logfile_path(), when="D", backupCount=3)

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self._logger.addHandler(hdlr)

        # Initialise DiscordRemote
        self._logger.info("DiscordRemote is started !")
        self.configure_discord(False)

        # Transition settings
        allowed_users = self._settings.get(['allowedusers'], merged=True)
        if allowed_users:
            self._settings.set(["allowedusers"], None, True)
            self._settings.set(['permissions'], {'1': {'users': allowed_users, 'commands': ''}}, True)

            self.send_message(None, "⚠️⚠️⚠️ Allowed users has been changed to a more granular system. "
                                    "Check the DiscordRemote settings and check that it is suitable⚠️⚠️⚠️")

    # ShutdownPlugin mixin
    def on_shutdown(self):
        self._logger.info("DiscordRemote is shutting down.")
        self.discord.shutdown_discord()
        self._logger.info("Discord bot has excited cleanly.")

    # SettingsPlugin mixin
    def get_settings_defaults(self):
        return {
            'bottoken': "",  # Ignored: Used by old bot.
            'shimaddress': "",
            'channelid': "",
            'baseurl': "",
            'presence': True,
            'presence_cycle_time': 10,
            'prefix': "/",
            'show_local_ip': 'auto',
            'show_external_ip': 'auto',
            'use_hostname': False,
            'hostname': "YOUR.HOST.NAME",
            'use_hostname_only': False,
            'events': self.events,
            'permissions': self.permissions,
            'allow_scripts': False,
            'script_before': '',
            'script_after': '',
            'allowed_gcode': ''
        }

    # Restricts some paths to some roles only
    def get_settings_restricted_paths(self):
        # settings.events.tests is a false message, so we should never see it as configurable.
        # settings.bottoken and channelid are admin only.
        return dict(never=[["events", "test"]],
                    admin=[["bottoken"],
                           ["channelid"],
                           ["permissions"],
                           ['baseurl'],
                           ['presence'],
                           ['presence_cycle_time'],
                           ['prefix'],
                           ["show_local_ip"],
                           ["show_external_ip"],
                           ["use_hostname"],
                           ["hostname"],
                           ["use_hostname_only"],
                           ['script_before'],
                           ['script_after'],
                           ['allowed_gcode']])

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
                self.update_presence("Printer Operational")
                return self.notify_event("printer_state_operational")
            elif payload["state_id"] == "ERROR":
                self.update_presence("Printer Errored")
                return self.notify_event("printer_state_error")
            elif payload["state_id"] == "UNKNOWN":
                return self.notify_event("printer_state_unknown")

        if event == "PrintStarted":
            self.update_presence("Print Started")
            self.start_periodic_reporting()
            return self.notify_event("printing_started", payload)
        if event == "PrintPaused":
            self.update_presence("Print Paused")
            return self.notify_event("printing_paused", payload)
        if event == "PrintResumed":
            self.update_presence("Print Resumed")
            return self.notify_event("printing_resumed", payload)
        if event == "PrintCancelled":
            self.update_presence("Complete")
            return self.notify_event("printing_cancelled", payload)

        if event == "PrintDone":
            self.stop_periodic_reporting()
            self.update_presence("Complete")
            payload['time_formatted'] = timedelta(seconds=int(payload["time"]))
            return self.notify_event("printing_done", payload)

        return True

    def parse_gcode_sent(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        if gcode:
            gcodes = self._settings.get(["events", "gcode_sent", "gcodes"]).split(",")
            if gcode in gcodes:
                self.notify_event("gcode_sent", {"gcode": gcode})
        return

    def on_print_progress(self, location, path, progress):
        # Avoid sending duplicate percentage progress messages
        if progress != self.last_progress_percent:
            self.last_progress_percent = progress

            self.update_presence(f"Print Progress: {progress}%")
            self.notify_event("printing_progress", {"progress": progress})

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        self._logger.info("Settings have saved. Send a test message...")
        self.configure_discord()

    # SimpleApiPlugin mixin
    def get_api_commands(self):
        return dict(
            executeCommand=['args'],
            sendMessage=[]
        )

    def on_api_command(self, comm, data):
        if not user_permission.can():
            return make_response("Insufficient rights", 403)

        if comm == 'executeCommand':
            return self.execute_command(data)

        if comm == 'sendMessage':
            return self.unpack_message(data)

    def execute_command(self, data):
        args = ""
        if 'args' in data:
            args = data['args']

        messages = self.command.parse_command(args)
        if messages is None:
            return make_response("Failed to send message", 404)

        self.discord.send(messages=messages)

    def unpack_message(self, data):
        builder = EmbedContent()
        if 'title' in data:
            builder.title = data['title']
        if 'author' in data:
            builder.author = data['author']
        if 'color' in data:
            builder.color = data['color']
        if 'description' in data:
            builder.description = data['description']
        if 'image' in data:
            b64image = data['image']
            imagename = data.get('imagename', 'snapshot.png')
            data = b64decode(b64image)
            builder.snapshot.filename = imagename
            builder.snapshot.data = data

        self.discord.send(messages=Response(embed=builder))
        pass

    def notify_event(self, event_id, data=None):
        self._logger.info("Received event: %s" % event_id)
        if self.is_muted:
            return True

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
        data['timeremaining'] = self.get_print_time_remaining()
        data['timespent'] = self.get_print_time_spent()
        data['eta'] = self.get_print_eta()

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
                done_config = self._settings.get(["events", "printing_done"], merged=True)
                # Don't send last message if the "printing_done" event is enabled.
                if done_config["enabled"]:
                    return False

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

    def get_ip_address(self):
        if self._settings.get(['show_local_ip'], merged=True) == 'hostname':
            return self._settings.get(['hostname'], merged=True)
        elif self._settings.get(['show_local_ip'], merged=True) == 'auto':
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
        else:
            return None

    def get_external_ip_address(self):
        if self._settings.get(['show_local_ip'], merged=True) == 'hostname':
            return self._settings.get(['hostname'], merged=True)
        elif self._settings.get(['show_local_ip'], merged=True) == 'auto':
            return ipgetter.myip()
        else:
            return None

    def get_port(self):
        port = self.get_settings().global_get(["plugins", "discovery", "publicPort"])
        if port:
            return port
        port = self.get_settings().global_get(["server", "port"])
        if port:
            return port

        return 5000  # Default to a sane value

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

        if self.discord is None:
            return

        # Get snapshot if asked for
        snapshot = None
        if with_snapshot:
            snapshot = self.get_snapshot()

        embed = EmbedContent()
        embed.author = self.get_printer_name()
        embed.title = message
        if snapshot:
            embed.snapshot.filename = snapshot.filename
            embed.snapshot.data = snapshot.data

        self.discord.send(Response(embed=embed))

        # exec "after" script if any
        self.exec_script(event_id, "after")

    def transform_image(self,
                        snapshot: bytes,
                        must_flip_h: bool,
                        must_flip_v: bool,
                        must_rotate: bool) -> bytes:
        # Only call Pillow if we need to transpose anything
        if must_flip_h or must_flip_v or must_rotate:
            img = Image.open(BytesIO(snapshot))

            self._logger.info(
                "Transformations : FlipH={}, FlipV={} Rotate={}".format(must_flip_h, must_flip_v, must_rotate))

            if must_flip_h:
                img = img.transpose(Image.FLIP_LEFT_RIGHT)

            if must_flip_v:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)

            if must_rotate:
                img = img.transpose(Image.ROTATE_90)

            tmp = BytesIO()
            img.save(tmp, 'png')
            tmp.seek(0)
            snapshot = tmp.read()
        return snapshot

    def get_snapshot(self) -> Optional[ProtoFile]:
        # Try new method.
        if hasattr(octoprint.plugin.types, "WebcamProviderPlugin"):
            cameras = self.get_plugin_manager().get_implementations(octoprint.plugin.types.WebcamProviderPlugin)
            for camera in cameras:
                configs = camera.get_webcam_configurations()
                for config in configs:
                    try:
                        snapshot = camera.take_webcam_snapshot(config)[0]
                        must_flip_h = config.flipH
                        must_flip_v = config.flipV
                        must_rotate = config.rotate90

                        snapshot = self.transform_image(snapshot, must_flip_h, must_flip_v, must_rotate)

                        return ProtoFile(filename="snapshot.jpg", data=snapshot)
                    except:
                        pass

        # And fall back to old method.
        snapshot = None
        snapshot_url = self._settings.global_get(["webcam", "snapshot"])
        if snapshot_url is None:
            return None
        if "http" in snapshot_url:
            try:
                snapshot = requests.get(snapshot_url).content
            except ConnectionError:
                return None
        if snapshot_url.startswith("file://"):
            snapshot = open(snapshot_url.partition('file://')[2], "rb").read()

        if snapshot is None:
            return None

        # Get the settings used for streaming to know if we should transform the snapshot
        must_flip_h = self._settings.global_get_boolean(["webcam", "flipH"])
        must_flip_v = self._settings.global_get_boolean(["webcam", "flipV"])
        must_rotate = self._settings.global_get_boolean(["webcam", "rotate90"])

        snapshot = self.transform_image(snapshot, must_flip_h, must_flip_v, must_rotate)

        return ProtoFile(filename="snapshot.png", data=snapshot)

    def get_printer_name(self):
        printer_name = self._settings.global_get(["appearance", "name"])
        if printer_name is None or len(printer_name) == 0:
            printer_name = "OctoPrint"
        return printer_name

    def update_discord_status(self, connected: str) -> None:
        self._plugin_manager.send_plugin_message(self._identifier, dict(isConnected=connected))

    def mute(self):
        self.is_muted = True

    def unmute(self):
        self.is_muted = False

    def get_file_manager(self):
        return self._file_manager

    def get_settings(self):
        return self._settings

    def get_printer(self):
        return self._printer

    def get_plugin_manager(self):
        return self._plugin_manager

    def get_print_time_spent(self):
        current_data = self._printer.get_current_data()
        try:
            current_time_val = current_data['progress']['printTime']
            return humanfriendly.format_timespan(current_time_val, max_units=2)
        except (KeyError, ValueError):
            return 'Unknown'

    def get_print_time_remaining(self):
        current_data = self._printer.get_current_data()
        try:
            remaining_time_val = current_data['progress']['printTimeLeft']
            return humanfriendly.format_timespan(remaining_time_val, max_units=2)
        except (KeyError, ValueError):
            return 'Unknown'

    def get_print_eta(self):
        current_data = self._printer.get_current_data()
        try:
            remaining_time_val = current_data['progress']['printTimeLeft']
            return (
                (datetime.now() + timedelta(seconds=remaining_time_val))
                    .isoformat(' ', 'minutes')
            )
        except:
            return 'Unknown'

    def start_periodic_reporting(self):
        self.stop_periodic_reporting()
        self.last_progress_percent = 0

        self.periodic_signal = Event()
        self.periodic_signal.clear()

        self.periodic_thread = Thread(target=self.periodic_reporting)
        self.periodic_thread.start()

    def stop_periodic_reporting(self):
        if self.periodic_signal is None or self.periodic_thread is None:
            return

        self.periodic_signal.set()
        self.periodic_thread.join(timeout=60)
        if self.periodic_thread.is_alive():
            self._logger.error("Periodic thread has hung, leaking it now.")
        else:
            self._logger.info("Periodic thread joined.")
        self.periodic_thread = None
        self.periodic_signal = None

    def periodic_reporting(self):
        if not self._settings.get(["events", "printing_progress_periodic", "enabled"]):
            return
        timeout = self._settings.get(["events", "printing_progress_periodic", "period"])

        while True:
            cur_time = time.time()
            next_time = cur_time + int(timeout)
            while time.time() < next_time:
                time.sleep(1)
                if self.periodic_signal.is_set():
                    return
                if not self._printer.is_printing():
                    return

            self.notify_event("printing_progress_periodic", data={"progress": self.last_progress_percent})

    def update_presence(self, param: str):
        if self.discord is not None:
            response = Response(presence=Presence(presence=param))
            self.discord.send(response)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "DiscordRemote"
__plugin_pythoncompat__ = ">=2.7,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = DiscordRemotePlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.filemanager.extension_tree": __plugin_implementation__.get_extension_tree,
        "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.parse_gcode_sent
    }
