# coding: utf-8

# Simple module to send messages through a Discord WebHook
# post a message to discord api via a bot
# bot must be added to the server and have write access to the channel

import json
from threading import Thread, Event
import time
import requests
import websocket
import logging

# OP codes for web socket.
DISPATCH = 0
HEARTBEAT = 1
IDENTIFY = 2
READY = 2
PRESENCE = 3
VOICE_STATE = 4
VOICE_PING = 5
RESUME = 6
RECONNECT = 7
REQUEST_MEMBERS = 8
INVALIDATE_SESSION = 9
HELLO = 10
HEARTBEAT_ACK = 11
GUILD_SYNC = 12


def split_text(text):
    if not text or len(text) == 0:
        return []

    parts = text.split('\n')
    chunks = [parts[0]]
    for part in parts[1:]:
        if len(chunks[-1]) + len(part) + len('`')*2 + len('\n') < 2000:
            chunks[-1] = "%s\n%s" % (chunks[-1], part)
        else:
            chunks.append(part)
    return chunks


class Discord:
    def __init__(self):
        pass

    channel_id = None  # enable dev mode on discord, right-click on the channel, copy ID
    bot_token = None  # get from the bot page. must be a bot, not a discord app
    gateway_url = "https://discordapp.com/api/gateway"
    postURL = None  # URL to post messages to, as the bot
    heartbeat_sent = 0
    heartbeat_interval = None
    last_sequence = None
    session_id = None
    web_socket = None  # WebSocket. Used for heartbeat.
    logger = logging  # Logger, uses default logging unless overridden
    headers = None  # Object containing the headers to send messages with.
    queue = []  # Message queue, stores messages until the bot reconnects.
    command = None  # Command parser
    status_callback = None  # The callback to use when the status changes.

    # Threads:
    manager_thread = None
    heartbeat_thread = None
    listener_thread = None

    # Events
    restart_event = Event()  # Set to restart discord bot.
    shutdown_event = Event()  # Set to stop all threads

    def configure_discord(self, bot_token, channel_id, logger, command, status_callback=None):
        self.shutdown_event.clear()
        self.restart_event.clear()
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.logger = logger
        self.command = command
        self.status_callback = status_callback
        if self.status_callback:
            self.status_callback(connected="disconnected")

        if self.channel_id is None or len(self.channel_id) != 18 or \
                self.bot_token is None or len(self.bot_token) != 59:
            self.shutdown_discord()
            return

        self.postURL = "https://discordapp.com/api/channels/{}/messages".format(self.channel_id)
        self.headers = {"Authorization": "Bot {}".format(self.bot_token),
                        "User-Agent": "myBotThing (http://some.url, v0.1)"}

        if not self.manager_thread:
            self.manager_thread = Thread(target=self.monitor_thread)
            self.manager_thread.start()
        else:
            self.restart_event.set()

    def monitor_thread(self):
        while not self.shutdown_event.is_set():
            socket_url = None

            if self.status_callback:
                self.status_callback(connected="connecting")

            while not self.shutdown_event.is_set() and socket_url is None:
                try:
                    r = requests.get(self.gateway_url, headers=self.headers)
                    socket_url = json.loads(r.content)['url']
                    self.logger.info("Socket URL is %s", socket_url)
                    break
                except Exception as e:
                    self.logger.error("Failed to connect to gateway: %s" % e.message)
                    time.sleep(5)
                    continue

            self.heartbeat_sent = 0
            self.web_socket = websocket.WebSocketApp(socket_url,
                                                     on_message=self.on_message,
                                                     on_error=self.on_error,
                                                     on_close=self.on_close)

            self.listener_thread = Thread(target=self.web_socket.run_forever)
            self.listener_thread.start()
            self.logger.debug("WebSocket listener started")
            time.sleep(1)

            if self.session_id:
                self.send_resume()

            # Wait until we are told to restart
            self.restart_event.clear()
            self.restart_event.wait()
            self.logger.info("Restart Triggered")

            if self.status_callback:
                self.status_callback(connected="disconnected")

            # Clean up resources
            if self.web_socket:
                try:
                    self.web_socket.close()
                except websocket.WebSocketConnectionClosedException as e:
                    self.logger.error("Failed to close websocket: %s" % e.message)
                self.web_socket = None
            if self.listener_thread:
                self.logger.info("Waiting for listener thread to join.")
                self.listener_thread.join()
                self.logger.info("Listener thread joined.")
                self.listener_thread = None

    def shutdown_discord(self):
        # Shutdown event must be set first.
        self.shutdown_event.set()
        self.restart_event.set()
        if self.manager_thread:
            self.manager_thread.join()
            self.manager_thread = None
        if self.heartbeat_thread:
            self.heartbeat_thread.join()
            self.heartbeat_thread = None

    def heartbeat(self):
        self.shutdown_event.clear()
        while not self.shutdown_event.is_set():
            # Send heartbeat
            if self.heartbeat_sent > 1:
                self.logger.error("Haven't received a heartbeat ACK in a while")
                if self.status_callback:
                    self.status_callback(connected="disconnected")
                self.restart_event.set()
            elif self.web_socket:
                out = {'op': 1, 'd': self.last_sequence}
                js = json.dumps(out)
                self.web_socket.send(js)
                self.heartbeat_sent += 1
                self.logger.info("Heartbeat: %s" % js)

            for i in range(self.heartbeat_interval / 1000):
                if not self.shutdown_event.is_set():
                    time.sleep(1)

    def on_message(self, web_socket, message):
        js = json.loads(message)

        if js['op'] == HELLO:
            self.handle_hello(js)
        elif js['op'] == READY:
            self.handle_ready(js)
        elif js['op'] == DISPATCH:
            self.handle_dispatch(js)
        elif js['op'] == HEARTBEAT_ACK:
            self.handle_heartbeat_ack()
        elif js['op'] == INVALIDATE_SESSION:
            self.handle_invalid_session(js)
        else:
            self.logger.debug("Unhandled message: %s" % json.dumps(js))

    def handle_dispatch(self, js):
        self.last_sequence = js['s']
        data = js['d']
        dispatch_type = js['t']

        if not data or not dispatch_type:
            self.logger.debug("Invalid message type: %s" % json.dumps(js))
            return

        if 'session_id' in data:
            self.session_id = data['session_id']

        self.logger.debug("Message was: %s" % json.dumps(js))

        if dispatch_type != "MESSAGE_CREATE":
            # Only care about message_create messages
            return

        if data['channel_id'] != self.channel_id:
            # Only care about messages from correct channel
            return

        if "bot" in data['author']:
            # Only care about real people messages
            # TODO: Add user authentication here?
            return

        if 'attachments' in data:
            for upload in data['attachments']:
                filename = upload['filename']
                url = upload['url']
                self.send(message=self.command.upload_file(filename, url))

        if 'content' in data:
            (message, snapshot) = self.command.parse_command(data['content'])
            self.send(message=message, snapshot=snapshot)


    def handle_hello(self, js):
        self.logger.info("Received HELLO message")
        # Authenticate
        self.send_identify()

        # Setup heartbeat_interval
        self.heartbeat_interval = js['d']['heartbeat_interval']

        # Setup heartbeat_thread
        if not self.heartbeat_thread:
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
        self.heartbeat_sent = 0
        self.process_queue()

    def handle_ready(self, js):
        self.logger.info("Received READY message")
        self.session_id = js['session_id']

    def handle_invalid_session(self, js):
        self.logger.info("Received INVALID_SESSION message")
        time.sleep(5)
        if js['d']:
            self.send_resume()
        else:
            self.send_identify()

    def process_queue(self):
        while len(self.queue):
            (message, snapshot) = self.queue.pop()
            self.send(message=message, snapshot=snapshot)

    def send(self, message=None, snapshot=None):
        if message:
            chunks = split_text(message)
            for chunk in chunks[0:-1]:
                if not self._dispatch_message(message="`%s`" % chunk):
                    return False
            if not self._dispatch_message(message="`%s`" % chunks[-1], snapshot=snapshot):
                return False
        else:
            if not self._dispatch_message(snapshot=snapshot):
                return False
        return True

    def _dispatch_message(self, message=None, snapshot=None):
        data = None
        files = None
        if message is not None and len(message) != 0:
            json_str = json.dumps({"content": message})
            data = {"payload_json": json_str}

        if snapshot:
            snapshot.seek(0)
            files = [("file", ("snapshot.png", snapshot))]

        if files is None and data is None:
            return False

        while True:
            try:
                r = requests.post(self.postURL,
                                  headers=self.headers,
                                  data=data,
                                  files=files)
                if r:
                    return True
            except Exception as e:
                self.logger.debug("Failed to send the message, exception occured: %s", e)
                self.queue_message(message, snapshot)
                return False

            if int(r.status_code) == 429:  # HTTP 429: Too many requests.
                retry_after = int(r.headers['Retry-After'])
                time.sleep(retry_after / 1000)
                continue
            else:
                self.logger.error("%s: %s - %s" % (str(r), r.content, r.headers))
                self.queue_message(message, snapshot)
                return False

    def on_error(self, ws, error):
        self.logger.error("Connection error: %s" % error)
        self.restart_event.set()

    def on_close(self, ws):
        self.logger.info("WebSocket Closed")
        self.restart_event.set()

    def queue_message(self, message, snapshot):
        if message is not None or snapshot is not None:
            self.logger.info("Message queued 2")
            self.queue.append((message, snapshot))
