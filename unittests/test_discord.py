import yaml
import logging
import time
from unittest import TestCase

from octoprint_octorant.discord import send, configure_discord


class TestSend(TestCase):
	def setUp(self):
		# Read config file and load test token and channel. Should not be committed.
		with open("config.yaml", "r") as config:
			config = yaml.load(config.read())
		configure_discord(logging,
						  p_bot_token=config['bot_token'],
						  p_channel_id=config['channel_id'],
						  p_command=None)
		time.sleep(5)


	def test_send(self):
		self.assertTrue(send("Test message"))
		with open("unittests/test_pattern.png", "rb") as file:
			self.assertTrue(send("Test message", file))
