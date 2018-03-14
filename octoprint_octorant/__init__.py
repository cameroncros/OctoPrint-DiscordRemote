# coding=utf-8
from __future__ import absolute_import
from .discord import Hook

import json
import octoprint.plugin
import octoprint.settings
import requests
from datetime import timedelta
from PIL import Image
from io import BytesIO

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
				"message" : ":alarm_clock: I just woke up! What are we gonna print today?"
			},
			"shutdown" : {
				"name" : "Octoprint Shutdown",
				"enabled" : True,
				"with_snapshot": False,
				"message" : ":zzz: Going to bed now!"
			},
			"printer_state_operational":{
				"name" : "Printer state : operational",
				"enabled" : True,
				"with_snapshot": False,
				"message" : ":white_check_mark: Your printer is operational."
			},
			"printer_state_error":{
				"name" : "Printer state : error",
				"enabled" : True,
				"with_snapshot": False,
				"message" : ":warning: Your printer is in an erroneous state."
			},
			"printer_state_unknown":{
				"name" : "Printer state : unknown",
				"enabled" : True,
				"with_snapshot": False,
				"message" : ":grey_question: Your printer is in an unknown state."
			},
			"printing_started":{
				"name" : "Priting process : started",
				"enabled" : True,
				"with_snapshot": True,
				"message" : ":printer: I've started printing {file}"
			},
			"printing_paused":{
				"name" : "Priting process : paused",
				"enabled" : True,
				"with_snapshot": True,
				"message" : ":pause_button: The printing was paused."
			},
			"printing_resumed":{
				"name" : "Priting process : resumed",
				"enabled" : True,
				"with_snapshot": True,
				"message" : ":play_button: The printing was resumed."
			},
			"printing_cancelled":{
				"name" : "Priting process : cancelled",
				"enabled" : True,
				"with_snapshot": True,
				"message" : ":octagonal_sign: The printing was stopped."
			},
			"printing_done":{
				"name" : "Priting process : done",
				"enabled" : True,
				"with_snapshot": True,
				"message" : ":thumbsup: Printing is done! Took about {time_formatted}"
			},
			"printing_failed":{
				"name" : "Priting process : failed",
				"enabled" : True,
				"with_snapshot": True,
				"message" : ":thumbsdown: Printing has failed! :("
			},
			"printing_progress":{
				"name" : "Priting progress",
				"enabled" : True,
				"with_snapshot": True,
				"message" : ":loudspeaker: Printing is at {progress}%",
				"step" : 10
			},
			"test":{ # Not a real message, but we will treat it as one
				"enabled" : True,
				"with_snapshot": True,
				"message" : "Hello hello! If you see this message, it means that the settings are correct!"
			},
		}
		
	def on_after_startup(self):
		self._logger.info("Octorant is started !")


	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return {
			'url': "",
			'username': "",
			'avatar': "",
			'events' : self.events
		}

	# Restricts some paths to some roles only
	def get_settings_restricted_paths(self):
		# settings.events.tests is a false message, so we should never see it as configurable.
		# settings.url, username and avatar are admin only.
		return dict(never=[["events","test"]],
					admin=[["url"],["username"],["avatar"]])

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
		old_bot_settings = '{}{}{}'.format(\
			self._settings.get(['url'],merged=True),\
			self._settings.get(['avatar'],merged=True),\
			self._settings.get(['username'],merged=True)\
		)
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
		new_bot_settings = '{}{}{}'.format(\
			self._settings.get(['url'],merged=True),\
			self._settings.get(['avatar'],merged=True),\
			self._settings.get(['username'],merged=True)\
		)
	
		if(old_bot_settings != new_bot_settings):
			self._logger.info("Settings have changed. Send a test message...")
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

		return self.send_message(tmpConfig["message"].format(**data), tmpConfig["with_snapshot"])


	def send_message(self,message,withSnapshot=False):

		# return false if no URL is provided
		if "http" not in self._settings.get(["url"],merged=True):
			return False
		
		# Get snapshot if asked for
		snapshot = None
		if 	withSnapshot and "http" in self._settings.global_get(["webcam","snapshot"]) :
			snapshotCall = requests.get(self._settings.global_get(["webcam","snapshot"]))

			# Get the settings used for streaming to know if we should transform the snapshot
			mustFlipH = self._settings.global_get(["webcam","flipH"])
			mustFlipV = self._settings.global_get(["webcam","flipV"])
			mustRotate = self._settings.global_get(["webcam","rotate90"])

			# Only do something if we got the snapshot
			if snapshotCall :
				snapshotImage = BytesIO(snapshotCall.content)				

				# Only call Pillow if we need to transpose anything
				if (mustFlipH or mustFlipV or mustRotate): 
					img = Image.open(snapshotImage)

					self._logger.info("Transformations : FlipH={}, FlipV={} Rotate={}".format(mustFlipH, mustFlipV, mustRotate))

					if mustFlipH:
						img = img.transpose(Image.FLIP_LEFT_RIGHT)
					
					if mustFlipV:
						img = img.transpose(Image.FLIP_TOP_BOTTOM)

					if mustRotate:
						img = img.transpose(Image.ROTATE_90)

					newImage = BytesIO()
					img.save(newImage,'png')			

					snapshotImage = newImage	


				snapshot = {'file': ("snapshot.png", snapshotImage.getvalue())}

		# Send to Discord WebHook
		discordCall = Hook(
			self._settings.get(["url"], merged=True),
			message,
			self._settings.get(["username"],merged=True),
			self._settings.get(['avatar'],merged=True),
			snapshot
		)		
		return discordCall.post()
		
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

