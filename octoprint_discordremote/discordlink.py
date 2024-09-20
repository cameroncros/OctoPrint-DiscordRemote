import socket
import threading
from typing import Optional, Tuple

from .genericforeversocket import GenericForeverSocket
from . import Command
from .proto.messages_pb2 import Response, Request, Settings


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

        self.discordshim_conn = GenericForeverSocket(address=self.shim_address[0],
                                                     port=self.shim_address[1],
                                                     init_fn=self._init_fn,
                                                     write_fn=self._write_fn,
                                                     read_fn=self._read_fn,
                                                     logger=self._logger)

    def _init_fn(self, s: GenericForeverSocket.BufferedSocketWrapper):
        response = Response(
            settings=Settings(channel_id=int(self.channel_id),
                              presence_enabled=self.presence_enabled,
                              cycle_time=self.cycle_time,
                              command_prefix=self.command_prefix)
        )
        cmdproto = response.SerializeToString()
        s.sendsafe(len(cmdproto).to_bytes(length=4, byteorder='little'))
        s.sendsafe(cmdproto)

    def _write_fn(self, s: GenericForeverSocket.BufferedSocketWrapper, data: Tuple):
        response = data[0]
        cmdproto = response.SerializeToString()
        s.sendsafe(len(cmdproto).to_bytes(length=4, byteorder='little'))
        s.sendsafe(cmdproto)

    def _read_fn(self, s: GenericForeverSocket.BufferedSocketWrapper):
        length_bytes = s.peek(4)
        length = int.from_bytes(length_bytes, byteorder='little')

        data_bytes = s.peek(4 + length)
        data = Request()
        data.ParseFromString(data_bytes[4:])
        s.skipahead(4 + length)

        if data.command:
            messages = self.command.parse_command(data.command, data.user)
            self.send(messages=messages)
        if data.HasField('file'):
            messages = self.command.download_file(data.file, data.user)
            self.send(messages=messages)

    def start_discord(self):
        self.discordshim_conn.run()

    def shutdown_discord(self):
        self.discordshim_conn.stop()

    def send(self, messages: Response):
        if messages is not None:
            self.discordshim_conn.send((messages,))
