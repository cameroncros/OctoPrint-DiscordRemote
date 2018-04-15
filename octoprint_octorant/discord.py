# post a message to discord api via a bot
# bot must be added to the server and have write access to the channel
# you may need to connect with a websocket the first time you run the bot
#   use a library like discord.py to do so
import json
import thread
import time
import requests
import websocket
import logging

from octoprint_octorant.command import parse_command

channel_id = None  # enable dev mode on discord, right-click on the channel, copy ID
bot_token = None  # get from the bot page. must be a bot, not a discord app
gatewayURL = "https://discordapp.com/api/gateway"
postURL = None
heartbeat_interval = None
heartbeat_thread = None
listener_thread = None
last_sequence = None
ws = None
logger = logging
headers = None


def configure_discord(p_logger, p_bot_token, p_channel_id):
	global channel_id, bot_token, logger
	bot_token = p_bot_token
	channel_id = p_channel_id
	logger = p_logger


def listener_func():
	global postURL, ws, headers
	postURL = "https://discordapp.com/api/channels/{}/messages".format(channel_id)
	headers = {"Authorization": "Bot {}".format(bot_token),
				"User-Agent": "myBotThing (http://some.url, v0.1)",
				"Content-Type": "application/json"}

	r = requests.get(gatewayURL, headers=headers)
	socketurl = json.loads(r.content)['url']
	ws = websocket.WebSocketApp(socketurl,
								on_message=on_message,
								on_error=on_error,
								on_close=on_close)
	while True:
		ws.run_forever()


def start_listener():
	global listener_thread
	listener_thread = thread.start_new_thread(listener_func, ())


def heartbeat():
	global last_sequence, heartbeat_interval, ws
	while True:
		# Sleep
		time.sleep(heartbeat_interval / 1000)
		# Send heartbeat
		out = {'op': 1, 'd': last_sequence}
		js = json.dumps(out)
		ws.send(js)
		logger.info("Heartbeat: %s" % js)


def on_message(web_socket, message):
	global bot_token, heartbeat_interval, heartbeat_thread, last_sequence, channel_id
	js = json.loads(message)
	if js['op'] == 10:  # Hello message
		# Authenticate
		out = {"op": 2,
				"d": {
					"token": bot_token,
					"properties": {},
					"compress": False,
					"large_threshold": 250
				}
			}
		outjs = json.dumps(out)
		web_socket.send(outjs)

		# Setup heartbeat_interval
		heartbeat_interval = js['d']['heartbeat_interval']

		# Setup heartbeat_thread
		if not heartbeat_thread:
			heartbeat_thread = thread.start_new_thread(heartbeat, ())
	elif js['op'] == 11:
		pass
	elif js['op'] == 0:
		last_sequence = js['s']
		if "bot" not in js['d']['author'] and js['t'] == "MESSAGE_CREATE" and js['d']['channel_id'] == channel_id:
			send("Received command, did nothing: %s" % js['d']['content'])


def send(message, snapshot=None):
	global postURL, headers
	json_data = json.dumps({"content": message})
	r = requests.post(postURL,
	                  headers=headers,
	                  data=json_data,
	                  files=snapshot)
	if r:
		return True
	return False


def on_error(ws, error):
	global logger
	logger.error("Connection error: {}" % error)


def on_close(ws):
	global logger
	logger.info("Closed")
