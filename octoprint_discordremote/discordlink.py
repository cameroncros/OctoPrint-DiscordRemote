import os
import socket
import subprocess
import threading
import time
from typing import Optional, Tuple

from . import Command
from .proto.messages_pb2 import Response, Request, Presence, Settings


class DiscordLink:
    client: Optional[socket.socket] = None
    command: Command

    def __init__(self, shim_address: Tuple[str, int],
                 channel_id: str,
                 command: Command,
                 logger,
                 presence_enabled: bool,
                 cycle_time: int,
                 command_prefix: str
                 ):
        self.lock = threading.Lock()
        self.command = command
        self.shim_address = shim_address
        self.channel_id = channel_id
        self.shutdown = False
        self._logger = logger
        self.presence_enabled = presence_enabled
        self.cycle_time = cycle_time
        self.command_prefix = command_prefix

    def start_discord(self):
        self.shutdown = False
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.shim_address)

        response = Response(
            settings=Settings(channel_id=int(self.channel_id),
                              presence_enabled=self.presence_enabled,
                              cycle_time=self.cycle_time,
                              command_prefix=self.command_prefix)
        )
        self.send(response)

        threading.Thread(target=self.listener).start()

    def shutdown_discord(self):
        self.shutdown = True
        self._stop_discord()

    def _stop_discord(self):
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

    def listener(self):
        while True:
            while self.client is None:
                if self.shutdown is True:
                    return
                time.sleep(1)

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
