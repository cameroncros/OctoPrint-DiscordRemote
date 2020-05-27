# coding: utf-8

# Simple module to send messages through a Discord WebHook
# post a message to discord api via a bot
# bot must be added to the server and have write access to the channel
from __future__ import unicode_literals

import json
from threading import Thread, Event
import time
import requests
import websocket
import logging
import re


# Constants
MAX_ERRORS = 25
CHANNEL_ID_LENGTH = 18
BOT_TOKEN_LENGTH = 59

# OP codes for web socket.
DISPATCH = 0
HEARTBEAT = 1
IDENTIFY = 2
PRESENCE = 3
VOICE_STATE = 4
VOICE_PING = 5
RESUME = 6
RECONNECT = 7
REQUEST_MEMBERS = 8
INVALID_SESSION = 9
HELLO = 10
HEARTBEAT_ACK = 11
GUILD_SYNC = 12


class Discord:
    def __init__(self):
        # enable dev mode on discord, right-click on the channel, copy ID (you can input multiple IDs separated with ",")
        self.channel_ids = None
        self.bot_token = None  # get from the bot page. must be a bot, not a discord app
        self.gateway_url = "https://discordapp.com/api/gateway"
        # URL to post messages to, as the bot
        self.postURL = "https://discordapp.com/api/channels/{}/messages"
        self.heartbeat_sent = 0
        self.heartbeat_interval = None
        self.last_sequence = None
        self.session_id = None
        self.web_socket = None  # WebSocket. Used for heartbeat.
        self.logger = logging  # Logger, uses default logging unless overridden
        # Object containing the headers to send messages with.
        self.headers = None
        # Message queue, stores messages until the bot reconnects.
        self.queue = []
        self.command = None  # Command parser
        # The callback to use when the status changes.
        self.status_callback = None
        self.error_counter = 0  # The number of errors that have occured.
        self.me = None  # The Bots ID.

        # Threads:
        self.manager_thread = None
        self.heartbeat_thread = None
        self.listener_thread = None

        # Events
        self.restart_event = Event()  # Set to restart discord bot.
        self.shutdown_event = Event()  # Set to stop all threads. Must also set restart_event

    def configure_discord(self, bot_token, channel_ids, logger, command, status_callback=None):
        self.shutdown_event.clear()
        self.restart_event.clear()
        self.bot_token = bot_token
        self.channel_ids = channel_ids
        if logger:
            self.logger = logger
        self.command = command
        self.status_callback = status_callback
        self.error_counter = 0

        if self.status_callback:
            self.status_callback(connected="disconnected")

        if self.channel_ids is None:
            self.logger.error(
                "Incorrectly configured: Channel IDs must not be empty.")
            self.shutdown_discord()
            return
        for id in self.channel_ids.split(','):
            if len(id.strip()) != CHANNEL_ID_LENGTH:
                self.logger.error(
                    "Incorrectly configured: Each channel ID must be %d chars long." % CHANNEL_ID_LENGTH)
                self.shutdown_discord()
                return
        if self.bot_token is None or len(self.bot_token) != BOT_TOKEN_LENGTH:
            self.logger.error(
                "Incorrectly configured: Bot Token must be %d chars long." % BOT_TOKEN_LENGTH)
            self.shutdown_discord()
            return

        self.headers = {"Authorization": "Bot {}".format(self.bot_token),
                        "User-Agent": "myBotThing (http://some.url, v0.1)"}

        if not self.manager_thread:
            self.manager_thread = Thread(target=self.monitor_thread)
            self.manager_thread.start()
        else:
            self.restart_event.set()

    def monitor_thread(self):
        while not self.shutdown_event.is_set():
            try:
                socket_url = None

                if self.status_callback:
                    self.status_callback(connected="connecting")

                while not self.shutdown_event.is_set() and socket_url is None:
                    try:
                        r = requests.get(self.gateway_url,
                                         headers=self.headers)
                        socket_url = json.loads(r.content)['url']
                        self.logger.info("Socket URL is %s", socket_url)
                        break
                    except Exception as e:
                        self.logger.error(
                            "Failed to connect to gateway: %s" % e.message)
                        time.sleep(5)
                        continue

                self.heartbeat_sent = 0
                self.web_socket = websocket.WebSocketApp(socket_url,
                                                         on_message=self.on_message,
                                                         on_error=self.on_error,
                                                         on_close=self.on_close)

                self.listener_thread = Thread(
                    target=self.web_socket.run_forever, kwargs={'ping_timeout': 1})
                self.listener_thread.start()
                self.logger.debug("WebSocket listener started")
                time.sleep(1)

                # Wait until we are told to restart
                self.restart_event.clear()
                self.restart_event.wait()
                self.logger.info("Restart Triggered")

            except Exception as e:
                self.logger.error(
                    "Exception occured, catching, ignoring, and restarting: %s", e.message)

            finally:
                if self.status_callback:
                    self.status_callback(connected="disconnected")

                # Clean up resources
                if self.web_socket:
                    try:
                        # Shutdown with status 4000 to prevent the session being closed.
                        self.web_socket.close(status=4000)
                    except websocket.WebSocketConnectionClosedException as e:
                        self.logger.error(
                            "Failed to close websocket: %s" % e.message)
                    self.web_socket = None
                if self.listener_thread:
                    self.logger.info("Waiting for listener thread to join.")

                    self.listener_thread.join(timeout=60)
                    if self.listener_thread.is_alive():
                        self.logger.error(
                            "Listener thread has hung, leaking it now.")
                    else:
                        self.logger.info("Listener thread joined.")
                    self.listener_thread = None

    def shutdown_discord(self):
        self.logger.info("Shutdown has been triggered")
        self.shutdown_event.set()
        self.restart_event.set()

        if self.manager_thread:
            self.manager_thread.join(timeout=60)
            if self.manager_thread.is_alive():
                self.logger.error("Manager thread has hung, leaking it now.")
            else:
                self.logger.info("Manager thread joined.")
        self.manager_thread = None

        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=60)
            if self.heartbeat_thread.is_alive():
                self.logger.error("HeartBeat thread has hung, leaking it now.")
            else:
                self.logger.info("HeartBeat thread joined.")
        self.heartbeat_thread = None

    def heartbeat(self):
        self.check_errors()
        while not self.shutdown_event.is_set():
            # Send heartbeat
            if self.heartbeat_sent > 1:
                self.logger.error(
                    "Haven't received a heartbeat ACK in a while")
                if self.status_callback:
                    self.status_callback(connected="disconnected")
                self.restart_event.set()
            elif self.web_socket:
                out = {'op': HEARTBEAT, 'd': self.last_sequence}
                js = json.dumps(out)
                try:
                    self.web_socket.send(js)
                    self.heartbeat_sent += 1
                    self.logger.info("Heartbeat: %s" % js)
                except Exception as exc:
                    self.logger.error("Exception caught: %s", exc)

            for i in range(int(round(self.heartbeat_interval / 1000))):
                if not self.shutdown_event.is_set():
                    time.sleep(1)

    def on_message(self, message):
        js = json.loads(message)

        if js['op'] == HELLO:
            self.handle_hello(js)
        elif js['op'] == DISPATCH:
            self.handle_dispatch(js)
        elif js['op'] == HEARTBEAT_ACK:
            self.handle_heartbeat_ack()
        elif js['op'] == INVALID_SESSION:
            self.handle_invalid_session(js)
        else:
            self.logger.debug("Unhandled message: %s" % json.dumps(js))

    def handle_dispatch(self, js):
        if 's' in js and js['s'] is not None:
            self.last_sequence = js['s']

        data = js['d']
        dispatch_type = js['t']

        if not data or not dispatch_type:
            self.logger.debug("Invalid message type: %s" % json.dumps(js))
            return

        if dispatch_type == "READY":
            self.me = data['user']['id']
            return self.handle_ready(js)

        if dispatch_type == "RESUMED":
            self.logger.info("Successfully resumed")
            return

        self.logger.debug("Message was: %s" % json.dumps(js))

        if dispatch_type != "MESSAGE_CREATE":
            # Only care about message_create messages
            return

        if not data['channel_id'] in self.channel_ids:
            # Only care about messages from corrects channels
            return

        user = data['author']['id']
        if self.me != None and user == self.me:
            # Don't respond to ourself.
            return

        if 'attachments' in data:
            for upload in data['attachments']:
                filename = upload['filename']
                url = upload['url']
                snapshots, embeds = self.command.download_file(
                    filename, url, user)
                self.send(embeds=embeds)

        if 'content' in data and len(data['content']) > 0:
            snapshots, embeds = self.command.parse_command(
                data['content'], user)
            self.send(channel_id=data['channel_id'], snapshots=snapshots,
                      embeds=embeds)

    def handle_hello(self, js):
        self.logger.info("Received HELLO message")

        # Authenticate/Resume
        if self.session_id:
            self.send_resume()
        else:
            self.send_identify()

        # Setup heartbeat_interval
        self.heartbeat_interval = js['d']['heartbeat_interval']

        # Debug output status of heartbeat thread.
        self.logger.info("Heartbeat thread: %s", self.heartbeat_thread)
        if self.heartbeat_thread:
            self.logger.info("Heartbeat thread is_alive(): %s",
                             self.heartbeat_thread.is_alive())

        # Setup heartbeat_thread
        if not self.heartbeat_thread or not self.heartbeat_thread.is_alive():
            self.logger.info("Starting Heartbeat thread")
            self.heartbeat_thread = Thread(target=self.heartbeat)
            self.heartbeat_thread.start()

        # Signal that we are connected.
        self.process_queue()

    def send_identify(self):
        self.logger.info("Sending IDENTIFY message")
        out = {
            "op": IDENTIFY,
            "d": {
                "token": self.bot_token,
                "properties": {},
                "compress": False,
                "large_threshold": 250
            }
        }
        out_js = json.dumps(out)
        self.web_socket.send(out_js)

    def send_resume(self):
        self.logger.info("Sending RESUME message")
        out = {
            'op': RESUME,
            'd': {
                'seq': self.last_sequence,
                'session_id': self.session_id,
                'token': self.bot_token
            }
        }
        js = json.dumps(out)
        self.web_socket.send(js)

    def handle_heartbeat_ack(self):
        self.logger.info("Received HEARTBEAT_ACK message")
        if self.status_callback:
            self.status_callback(connected="connected")
        if self.error_counter > 0:
            self.error_counter -= 0
        self.heartbeat_sent = 0
        self.process_queue()

    def handle_ready(self, js):
        self.logger.info("Received READY message")
        self.last_sequence = js['s']
        self.session_id = js['d']['session_id']

    def handle_invalid_session(self, js):
        self.logger.info("Received INVALID_SESSION message")
        self.session_id = None
        self.last_sequence = None
        time.sleep(5)
        self.send_identify()

    def process_queue(self):
        while not self.shutdown_event.is_set() and len(self.queue):
            channel_id, snapshot, embed = self.queue.pop()
            if self._dispatch_message(channel_id=channel_id, snapshot=snapshot, embed=embed):
                continue
            else:
                break

    def send(self, channel_id=None, snapshots=None, embeds=None):
        if snapshots is not None:
            for snapshot in snapshots:
                if channel_id == None:
                    for id in self.channel_ids.split(','):
                        if not self._dispatch_message(id.strip(), snapshot=snapshot):
                            return False
                else:
                    if not self._dispatch_message(channel_id, snapshot=snapshot):
                        return False

        if embeds is not None:
            for embed in embeds:
                if channel_id == None:
                    for id in self.channel_ids.split(','):
                        if not self._dispatch_message(id.strip(), embed=embed):
                            return False
                else:
                    if not self._dispatch_message(channel_id, embed=embed):
                        return False
        return True

    def _dispatch_message(self, channel_id, snapshot=None, embed=None):
        data = None
        files = []

        if embed is not None:
            json_str = json.dumps({'embed': embed.get_embed()})
            data = {"payload_json": json_str}
            for attachment in embed.get_files():
                attachment[1].seek(0)
                files.append(("attachment", attachment))

        if snapshot:
            snapshot[1].seek(0)
            files.append(("file", snapshot))

        if len(files) == 0:
            files = None

        if files is None and data is None:
            return False

        while True:
            try:
                r = requests.post(self.postURL.format(channel_id),
                                  headers=self.headers,
                                  data=data,
                                  files=files)
                if r:
                    return True
            except Exception as e:
                self.logger.debug(
                    "Failed to send the message, exception occured: %s", str(e))
                self.error_counter += 1
                self.check_errors()
                self.queue_message(channel_id, snapshot, embed)
                return False

            if int(r.status_code) == 429:  # HTTP 429: Too many requests.
                retry_after = int(r.headers['Retry-After'])
                time.sleep(retry_after / 1000)
                continue
            else:
                self.logger.error("Failed to send message:")
                self.logger.error("\tResponse: %s" %
                                  self.log_safe(str(r.status_code)))
                self.logger.error("\tResponse Content: %s" %
                                  self.log_safe(str(r.content)))
                self.logger.error("\tResponse Headers: %s" %
                                  self.log_safe(str(r.headers)))
                self.logger.error("\tURL: %s" %
                                  self.log_safe(str(self.postURL.format(channel_id))))
                self.logger.error("\tHeaders: %s" %
                                  self.log_safe(str(self.headers)))
                self.logger.error("\tData: %s" % data)
                self.logger.error("\tFiles: %s" % files)
                self.error_counter += 1
                self.check_errors()
                self.queue_message(channel_id, snapshot, embed)
                return False

    def on_error(self, error):
        self.logger.error("Connection error: %s" % error)
        self.restart_event.set()

    def on_close(self):
        self.logger.info("WebSocket Closed")
        self.restart_event.set()

    def queue_message(self, channel_id, snapshot, embed):
        if snapshot is not None or embed is not None:
            self.logger.info("Message queued")
            self.queue.append((channel_id, snapshot, embed))

    def check_errors(self):
        if self.error_counter > MAX_ERRORS:
            # More than MAX_ERRORS errors, in rapid succession,
            # best to shutdown and let the user restart.
            self.logger.error("Had %s/%s errors in rapid succession, this is bad sign. "
                              "Shutting down bot to avoid spam" % (self.error_counter, MAX_ERRORS))
            Thread(target=self.shutdown_discord()).start()

            if self.status_callback:
                self.status_callback(connected="disconnected")

    def log_safe(self, message):
        clean_message = message.replace(self.bot_token, "[bot_token]")
        for channel_id in self.channel_ids:
            clean_message = clean_message.replace(
                channel_id.strip(), "[channel_id]")
        return clean_message
