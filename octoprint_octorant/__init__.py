# coding=utf-8
from __future__ import absolute_import
from .discord2 import Hook

import json
import octoprint.plugin
import octoprint.settings
import requests

class OctorantPlugin(octoprint.plugin.EventHandlerPlugin,
					 octoprint.plugin.StartupPlugin,
					 octoprint.plugin.SettingsPlugin,
                     octoprint.plugin.AssetPlugin,
                     octoprint.plugin.TemplatePlugin,
					 octoprint.plugin.ProgressPlugin):


	def on_after_startup(self):
		self._logger.info("Octorant is started ! url : {}".format(self._settings.get(["url"])))


	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return {
			'url': "test_url",
			'username': "",
			'avatar': "",
			'include_snapshot' : True,
			'events' : {
				"startup" : {
					"enabled" : True,
					"with_snapshot": False,
					"message" : ":alarm_clock: I just woke up! What are we gonna print today?"
				},
				"shutdown" : {
					"enabled" : True,
					"with_snapshot": False,
					"message" : ":zzz: Going to bed now!"
				},
				"printer_state_operational":{
					"enabled" : True,
					"with_snapshot": False,
					"message" : ""
				},
				"printer_state_error":{
					"enabled" : True,
					"with_snapshot": False,
					"message" : ""
				},
				"printer_state_unknown":{
					"enabled" : True,
					"with_snapshot": False,
					"message" : ""
				},
				"printing_started":{
					"enabled" : True,
					"with_snapshot": False,
					"message" : ""
				},
				"printing_paused":{
					"enabled" : True,
					"with_snapshot": False,
					"message" : ""
				},
				"printing_resumed":{
					"enabled" : True,
					"with_snapshot": False,
					"message" : ""
				},
				"printing_cancelled":{
					"enabled" : True,
					"with_snapshot": False,
					"message" : ""
				},
				"printing_done":{
					"enabled" : True,
					"with_snapshot": False,
					"message" : ""
				},
				"printing_progress":{
					"enabled" : True,
					"with_snapshot": False,
					"message" : "",
					"step" : 10
				},
				"test":{ # Not a real message, but we will treat it as one
					"enabled" : True,
					"with_snapshot": False,
					"message" : "Hello hello! If you see this message, it means that the settings are correct!"
				},
			}
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
		self._logger.info("OCTORANT - RECIEVED EVENT {} / {}".format(event, payload))
		content = ""
		needSnapshot = False
		if event == "Startup":
			content = ":alarm_clock: Hello! I just woke up!"
		elif event == "Shutdown":
			content = ":zzz: Going to bed now! See you later!"
		elif event == "PrinterStateChanged":
			if payload["state_id"] == "OPERATIONAL":
				content = ":ok: I saw your printer. I'm ready to rock!"
			elif payload["state_id"] == "ERROR":
				content = ":sos: Uh-oh. Something bad happened, it seems your printer is gone :("
			elif payload["state_id"] == "UNKNOWN":
				content = ":question: Hmmm... Where's your printer?"
		elif event == "PrintStarted":
			content = "I've just started working on this file : {}!".format(payload["name"])
			needSnapshot = True
		elif event == "PrintDone":
			content = ":ballot_box_with_check: Yeah! I just finished this gem! What do you think?"
			needSnapshot = True
		else:
			content = ""

		if content != "" and "http" in self._settings.get(['url']):
			attached = None

			if self._settings.get_boolean(["include_snapshot"]) \
				and "http" in self._settings.global_get(["webcam","snapshot"]):
				snapshot = requests.get(self._settings.global_get(["webcam","snapshot"]))
				attached = {'file': ("snapshot.jpg", snapshot.content)}
	
			call = Hook( \
				  self._settings.get(['url']) \
				, content \
				, self._settings.get(['username']) \
				, self._settings.get(['avatar']),attached)
			call.post()		

	def on_print_progress(self,location,path,progress):
		return True

	def on_settings_save(self, data):
		old_bot_settings = '{}{}{}'.format(self._settings.get(['url']),self._settings.get(['avatar']),self._settings.get(['username']))
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
		new_bot_settings = '{}{}{}'.format(self._settings.get(['url']),self._settings.get(['avatar']),self._settings.get(['username']))
	
		if(old_bot_settings != new_bot_settings):
			#TODO : send a test message to check new settings
			self._logger.info("Settings have changed. Send a test message ?")
			return True



	def notify_event(self,eventID,data={}):
		#TODO: handle eventID
		return True


	def send_message(self,message,withSnapshot=False):
		#TODO: call creation and snapshot get
		return True
		
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

