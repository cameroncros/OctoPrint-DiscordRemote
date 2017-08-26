# coding=utf-8
from __future__ import absolute_import
from .discord import Webhook,Attachment,Field

import octoprint.plugin

class OctorantPlugin(octoprint.plugin.EventHandlerPlugin,
					 octoprint.plugin.StartupPlugin,
					 octoprint.plugin.SettingsPlugin,
                     octoprint.plugin.AssetPlugin,
                     octoprint.plugin.TemplatePlugin):


	## Init
	def __init__(self):
		self.url = ""
		self.username = ""
		self.avatar = ""

	def on_after_startup(self):
		self._logger.info("Octorant is started !")
		payload = Webhook(self.url,"Octorant is started!")
		payload.post()


	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			# put your plugin's default settings here
			url="",
			username="",
			avatar="",

		)

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/OctoRant.js"],
			css=["css/OctoRant.css"],
			less=["less/OctoRant.less"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			OctoRant=dict(
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
		if event == "Startup":
			content = "Hello! I just woke up!"
		elif event == "Shutdown":
			content = "Going to bed now! See you later!"
		elif event == "PrinterStateChanged":
			if payload["state_id"] == "OPERATIONAL":
				content = "I saw your printer. I'm ready to rock!"
			elif payload["state_id"] == "ERROR":
				content = "Uh-oh. Something bad happened, it seems your printer is gone :("
			elif payload["state_id"] == "UNKNOWN":
				content = "Hmmm... Where's your printer?"
		elif event == "PrintStarted":
			content = "I've just started working on this file : {}!".format(payload["name"])
		elif event == "PrintDone":
			content = "Yeah! I just finished this gem! What do you think?"
		else:
			content = ""

		if content != "":
			call = Webhook(self.url,content)
			call.post()		
		
# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Octorant Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = OctorantPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

