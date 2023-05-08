import os
import socket
import subprocess

from proto.messages_pb2 import Response, EmbedContent, Presence


class DiscordLink:
    process = None
    client = None

    def __init__(self, bot_token, channel_id):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(10)
        server.bind(('127.0.0.1', 23456))
        server.listen()

        self.start_discordshim(bot_token, channel_id)

        try:
            self.client, _ = server.accept()
            server.close()
        except socket.timeout:
            pass

    def start_discordshim(self, bot_token, channel_id):
        my_env = os.environ.copy()
        my_env["BOT_TOKEN"] = bot_token
        my_env["CHANNEL_ID"] = channel_id
        self.process = subprocess.Popen(["python", "-m", "octoprint_discordshim"], env=my_env)

    def shutdown_discord(self):
        if self.process:
            self.process.kill()
            self.process.wait()
            self.process = None
        if self.client:
            self.client.close()
            self.client = None

    def send(self, messages: EmbedContent):
        cmdproto = Response(embed=messages).SerializeToString()
        self.client.send(len(cmdproto).to_bytes(length=4, byteorder='little'))
        self.client.send(cmdproto)

    def configure_presence(self, presence: str, ):
        cmdproto = Response(presence=Presence(presence)).SerializeToString()
        self.client.send(len(cmdproto).to_bytes(length=4, byteorder='little'))
        self.client.send(cmdproto)
