# coding=utf-8
from __future__ import absolute_import

from octoprint_octorant.command import Command
from .discord import configure_discord, start_listener, send

import json
import octoprint.plugin
import octoprint.settings
import requests
from datetime import timedelta
from PIL import Image
from io import BytesIO
import subprocess
import os


class OctorantPlugin(octoprint.plugin.EventHandlerPlugin,
					 octoprint.plugin.StartupPlugin,
					 octoprint.plugin.SettingsPlugin,
                     octoprint.plugin.AssetPlugin,
                     octoprint.plugin.TemplatePlugin,
					 octoprint.plugin.ProgressPlugin):

	def __init__(self):
		# Events definition here (better for intellisense in IDE)
		# referenced in the settings too.
		self.events = {
			"startup" : {
				"name" : "Octoprint Startup",
				"enabled" : True,
				"with_snapshot": False,
				"message" : "⏰ I just woke up! What are we gonna print today?"
			},
			"shutdown" : {
				"name" : "Octoprint Shutdown",
				"enabled" : True,
				"with_snapshot": False,
				"message" : "💤 Going to bed now!"
			},
			"printer_state_operational":{
				"name" : "Printer state : operational",
				"enabled" : True,
				"with_snapshot": False,
				"message" : "✅ Your printer is operational."
			},
			"printer_state_error":{
				"name" : "Printer state : error",
				"enabled" : True,
				"with_snapshot": False,
				"message" : "⚠️ Your printer is in an erroneous state."
			},
			"printer_state_unknown":{
				"name" : "Printer state : unknown",
				"enabled" : True,
				"with_snapshot": False,
				"message" : "❔ Your printer is in an unknown state."
			},
			"printing_started":{
				"name" : "Printing process : started",
				"enabled" : True,
				"with_snapshot": True,
				"message" : "🖨️ I've started printing {file}"
			},
			"printing_paused":{
				"name" : "Printing process : paused",
				"enabled" : True,
				"with_snapshot": True,
				"message" : "⏸️ The printing was paused."
			},
			"printing_resumed":{
				"name" : "Printing process : resumed",
				"enabled" : True,
				"with_snapshot": True,
				"message" : "▶️ The printing was resumed."
			},
			"printing_cancelled":{
				"name" : "Printing process : cancelled",
				"enabled" : True,
				"with_snapshot": True,
				"message" : "🛑 The printing was stopped."
			},
			"printing_done":{
				"name" : "Printing process : done",
				"enabled" : True,
				"with_snapshot": True,
				"message" : "👍 Printing is done! Took about {time_formatted}"
			},
			"printing_failed":{
				"name" : "Printing process : failed",
				"enabled" : True,
				"with_snapshot": True,
				"message" : "👎 Printing has failed! :("
			},
			"printing_progress":{
				"name" : "Printing progress",
				"enabled" : True,
				"with_snapshot": True,
				"message" : "📢 Printing is at {progress}%",
				"step" : 10
			},
			"test":{ # Not a real message, but we will treat it as one
				"enabled" : True,
				"with_snapshot": True,
				"message" : "Hello hello! If you see this message, it means that the settings are correct!"
			},
		}
		self.command = None

	def on_after_startup(self):
		self._logger.info("Octorant is started !")
		if self.command is None:
			self.command = Command(self)
		# Configure discord
		configure_discord(self._logger,
		                  self._settings.get(['bottoken'],merged=True),
		                  self._settings.get(['channelid'],merged=True),
		                  self.command)

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return {
			'bottoken': "",
			'channelid': "",
			'events' : self.events,
			'allow_scripts': False,
			'script_before': '',
			'script_after': ''
		}

	# Restricts some paths to some roles only
	def get_settings_restricted_paths(self):
		# settings.events.tests is a false message, so we should never see it as configurable.
		# settings.bottoken and channelid are admin only.
		return dict(never=[["events","test"]],
		            admin=[["bottoken"],["channelid"],['script_before'],['script_after']])

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/octorant.js"],
			css=["css/octorant.css"],
			less=["less/octorant.less"]
		)


	##~~ TemplatePlugin mixin
	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False)
		]

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			octorant=dict(
				displayName="Octorant Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="bchanudet",
				repo="OctoPrint-Octorant",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/bchanudet/OctoPrint-Octorant/archive/{target_version}.zip"
			)
		)

	##~~ EventHandlerPlugin hook

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
			return self.notify_event("printing_started",payload)
		if event == "PrintPaused":
			return self.notify_event("printing_paused",payload)
		if event == "PrintResumed":
			return self.notify_event("printing_resumed",payload)
		if event == "PrintCancelled":
			return self.notify_event("printing_cancelled",payload)

		if event == "PrintDone":
			payload['time_formatted'] = str(timedelta(seconds=int(payload["time"])))
			return self.notify_event("printing_done", payload)

		return True

	def on_print_progress(self,location,path,progress):
		self.notify_event("printing_progress",{"progress": progress})

	def on_settings_save(self, data):
		old_bot_settings = '{}{}'.format(\
			self._settings.get(['bottoken'],merged=True),\
			self._settings.get(['channelid'],merged=True)\
		)
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
		new_bot_settings = '{}{}'.format(\
			self._settings.get(['bottoken'],merged=True),\
			self._settings.get(['channelid'],merged=True)\
		)

		if(old_bot_settings != new_bot_settings):
			self._logger.info("Settings have changed. Send a test message...")
			# Configure discord
			if self.command is None:
				self.command = Command(self._printer, self._file_manager)
			configure_discord(self._logger,
			                  self._settings.get(['bottoken'],merged=True),
			                  self._settings.get(['channelid'],merged=True),
			                  self.command)
			self.notify_event("test")


	def notify_event(self,eventID,data={}):
		if(eventID not in self.events):
			self._logger.error("Tried to notifiy on inexistant eventID : ", eventID)
			return False

		tmpConfig = self._settings.get(["events", eventID],merged=True)

		if tmpConfig["enabled"] != True:
			self._logger.debug("Event {} is not enabled. Returning gracefully".format(eventID))
			return False

		# Special case for progress eventID : we check for progress and stepss
		if eventID == 'printing_progress' and (\
			int(data["progress"]) == 0 \
			or int(data["progress"]) % int(tmpConfig["step"]) != 0 \
		) :
			return False

		return self.send_message(eventID, tmpConfig["message"].format(**data), tmpConfig["with_snapshot"])

	def exec_script(self, eventName, which=""):

		# I want to be sure that the scripts are allowed by the special configuration flag
		scripts_allowed = self._settings.get(["allow_scripts"],merged=True)
		if scripts_allowed is None or scripts_allowed == False:
			return ""

		# Finding which one should be used.
		script_to_exec = None
		if which == "before":
			script_to_exec = self._settings.get(["script_before"], merged=True)

		elif which == "after":
			script_to_exec = self._settings.get(["script_after"], merged=True)

		# Finally exec the script
		out = ""
		self._logger.info("{}:{} File to start: '{}'".format(eventName, which, script_to_exec))

		try:
			if script_to_exec is not None and len(script_to_exec) > 0 and os.path.exists(script_to_exec):
				out = subprocess.check_output(script_to_exec)
		except (OSError, subprocess.CalledProcessError) as err:
				out = err
		finally:
			self._logger.info("{}:{} > Output: '{}'".format(eventName, which, out))
			return out


	def send_message(self, eventID, message, withSnapshot=False):
		# exec "before" script if any
		self.exec_script(eventID, "before")

		# Get snapshot if asked for
		snapshot = None
		if withSnapshot:
			snapshot = self.get_snapshot()

		# Send to Discord WebHook
		out = send(message, snapshot)

		# exec "after" script if any
		self.exec_script(eventID, "after")

		return out

	def get_snapshot(self):
		snapshotUrl = self._settings.global_get(["webcam", "snapshot"])
		if snapshotUrl is  None or "http" not in snapshotUrl:
			return None

		snapshotCall = requests.get(snapshotUrl)
		if not snapshotCall:
			return None

		snapshot = BytesIO(snapshotCall.content)

		# Get the settings used for streaming to know if we should transform the snapshot
		mustFlipH = self._settings.global_get_boolean(["webcam", "flipH"])
		mustFlipV = self._settings.global_get_boolean(["webcam", "flipV"])
		mustRotate = self._settings.global_get_boolean(["webcam", "rotate90"])


		# Only call Pillow if we need to transpose anything
		if mustFlipH or mustFlipV or mustRotate:
			img = Image.open(snapshot)

			self._logger.info(
				"Transformations : FlipH={}, FlipV={} Rotate={}".format(mustFlipH, mustFlipV, mustRotate))

			if mustFlipH:
				img = img.transpose(Image.FLIP_LEFT_RIGHT)

			if mustFlipV:
				img = img.transpose(Image.FLIP_TOP_BOTTOM)

			if mustRotate:
				img = img.transpose(Image.ROTATE_90)

			newImage = BytesIO()
			img.save(newImage, 'png')

			return newImage
		return snapshot


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "OctoRant"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = OctorantPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

