import os
import socket
import subprocess
import threading
import time
from typing import Optional

from . import Command
from .proto.messages_pb2 import Response, Request, Presence, Settings


class DiscordLink:
    process = None
    client: Optional[socket.socket] = None
    command: Command

    def __init__(self, bot_token: str, command: Command, logger):
        self.lock = threading.Lock()
        self.command = command
        self.bot_token = bot_token
        self.shutdown = False
        self._logger = logger

    def spawn_discordshim(self, port: int):
        my_env = os.environ.copy()
        my_env["BOT_TOKEN"] = self.bot_token
        my_env["DISCORD_LINK_PORT"] = str(port)

        path_guess = os.path.abspath(__file__).split('/')[0:-5]
        path_guess.append('bin')
        venv_path = '/git'.join(path_guess)
        my_env['PATH'] = f'{venv_path}:{my_env["PATH"]}'
        self._logger.info(f"env: [{my_env}]")
        self._logger.info(f"cwd: [{os.getcwd()}]")
        self._logger.info(f"file_path: [{__file__}]")
        self.process = subprocess.Popen(["python3", "-m", "octoprint_discordremote.discordshim"], env=my_env)
        self._logger.info("Started discordshim");

    def start_discord(self):
        self.shutdown = False
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(10)
        server.bind(('127.0.0.1', 0))
        sock_details = server.getsockname()
        server.listen()

        self.spawn_discordshim(sock_details[1])

        while self.client is None:
            try:
                self.client, _ = server.accept()
                server.close()
            except socket.timeout:
                pass

        threading.Thread(target=self.listener).start()

    def shutdown_discord(self):
        self.shutdown = True
        self._stop_discord()

    def _stop_discord(self):
        if self.process:
            self.process.kill()
            self.process.wait(timeout=5)
            self.process = None
        if self.client:
            self.client.close()
            self.client = None

    def send(self, messages: Response):
        self.lock.acquire()
        cmdproto = messages.SerializeToString()
        try:
            self.client.send(len(cmdproto).to_bytes(length=4, byteorder='little'))
            self.client.send(cmdproto)
        except:
            pass
        self.lock.release()

    def update_presence(self, status: str):
        resp = Response(presence=Presence(presence=status))
        self.send(resp)

    def update_settings(self, settings: Settings):
        resp = Response(settings=settings)
        self.send(resp)

    def listener(self):
        while True:
            while self.client is None:
                if self.shutdown is True:
                    return
                time.sleep(1)

            # Check process is still running
            try:
                self.process.wait(timeout=0.001)
                if self.process.returncode is not None:
                    break
            except subprocess.TimeoutExpired:
                pass

            # Try listening for message
            try:
                assert self.client is not None

                length_bytes = self.client.recv(4)
                if len(length_bytes) == 0:
                    break  # Socket has closed.
                length = int.from_bytes(length_bytes, byteorder='little')

                data_bytes = self.client.recv(length)
                data = Request()
                data.ParseFromString(data_bytes)

                if data.command:
                    messages = self.command.parse_command(data.command, data.user)
                    self.send(messages=messages)
                if data.HasField('file'):
                    messages = self.command.download_file(data.file, data.user)
                    self.send(messages=messages)
            except socket.timeout:
                continue
            except TimeoutError:
                continue
            except Exception as e:
                self._logger.error(f"Listener failed with: [{e}]")
                break
        self._stop_discord()
        if not self.shutdown:
            time.sleep(5)
            self.start_discord()
