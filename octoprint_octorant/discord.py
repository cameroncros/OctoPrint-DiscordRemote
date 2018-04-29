#coding: utf-8

# Simple module to send messages through a Discord WebHook
# post a message to discord api via a bot
# bot must be added to the server and have write access to the channel

import json
import thread
import time
import requests
import websocket
import logging

channel_id = None  # enable dev mode on discord, right-click on the channel, copy ID
bot_token = None  # get from the bot page. must be a bot, not a discord app
gatewayURL = "https://discordapp.com/api/gateway"
postURL = None  # URL to post messages to, as the bot
heartbeat_interval = None
heartbeat_thread = None
listener_thread = None
last_sequence = None
ws = None  # Websocket. Used for heartbeat.
logger = logging  # Logger, uses default logging unless overridden
headers = None  # Object containing the headers to send messages with.
running = None  # True if the bot is connected and running.
queue = []  # Message queue, stores messages until the bot reconnects.


def configure_discord(p_logger, p_bot_token, p_channel_id):
	global channel_id, bot_token, logger
	bot_token = p_bot_token
	channel_id = p_channel_id
	logger = p_logger
	start_listener()


def listener_func():
	global postURL, ws, headers
	postURL = "https://discordapp.com/api/channels/{}/messages".format(channel_id)
	headers = {"Authorization": "Bot {}".format(bot_token),
				"User-Agent": "myBotThing (http://some.url, v0.1)"}

	r = requests.get(gatewayURL, headers=headers)
	socketurl = json.loads(r.content)['url']
	ws = websocket.WebSocketApp(socketurl,
				    on_message=on_message,
				    on_error=on_error,
				    on_close=on_close)
	while True:
		ws.run_forever()


def start_listener():
	global listener_thread, running
	running = None
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
	global bot_token, heartbeat_interval, heartbeat_thread, last_sequence, channel_id, running
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

		# Signal that we are connected.
		running = True
		process_queue()
	elif js['op'] == 11:
		pass
	elif js['op'] == 0:
		last_sequence = js['s']
		if "bot" not in js['d']['author'] and js['t'] == "MESSAGE_CREATE" and js['d']['channel_id'] == channel_id:
			send("Received command, did nothing: %s" % js['d']['content'])


def process_queue():
	global queue
	while len(queue):
		(message, snapshot) = queue.pop()
		send(message, snapshot)


def send(message, snapshot=None):
	global postURL, headers, running
	if not running:
		queue.append((message, snapshot))
		return True

	json_data = json.dumps({"content": message})
	if snapshot:
		r = requests.post(postURL,
	                  headers=headers,
	                  data={"payload_json": json_data},
	                  files=[("file", ("snapshot.png", snapshot))])
	else:
		r = requests.post(postURL,
		                  headers=headers,
		                  data={"payload_json": json_data})
	if r:
		return True
	return False


def on_error(ws, error):
	global logger, running
	logger.error("Connection error: {}" % error)
	running = False


def on_close(ws):
	global logger
	logger.info("Closed")
