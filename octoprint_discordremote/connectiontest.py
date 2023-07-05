import logging
import sys
from typing import Tuple

try:
    from .genericforeversocket import GenericForeverSocket
    from .proto.messages_pb2 import Response, Settings, Request, EmbedContent
except:
    from octoprint_discordremote.genericforeversocket import GenericForeverSocket
    from octoprint_discordremote.proto.messages_pb2 import Response, Settings, Request, EmbedContent

channelid = 0


def init_fn(s: GenericForeverSocket.BufferedSocketWrapper):
    response = Response(
        settings=Settings(channel_id=int(channelid),
                          presence_enabled=False,
                          cycle_time=1,
                          command_prefix='/')
    )
    cmdproto = response.SerializeToString()
    s.sendsafe(len(cmdproto).to_bytes(length=4, byteorder='little'))
    s.sendsafe(cmdproto)


def send_fn(s: GenericForeverSocket.BufferedSocketWrapper, data: Tuple):
    response = data[0]
    cmdproto = response.SerializeToString()
    s.sendsafe(len(cmdproto).to_bytes(length=4, byteorder='little'))
    s.sendsafe(cmdproto)


def recv_fn(s: GenericForeverSocket.BufferedSocketWrapper):
    length_bytes = s.peek(4)
    length = int.from_bytes(length_bytes, byteorder='little')
    logger.info(f"Message was {len(length_bytes)} long, next message will be {length} bytes long")

    data_bytes = s.peek(4 + length)
    logger.info(f"Message was {len(data_bytes)} long")
    data = Request()
    data.ParseFromString(data_bytes[4:])

    s.skipahead(4 + length)

    print(f'Received: {data}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} CHANNEL_ID")
        exit(-1)
    channelid = int(sys.argv[1])

    logger = logging.Logger("gfstester")
    gfs = GenericForeverSocket(address='opdrshim.uk',
                               port=23416,
                               init_fn=init_fn,
                               read_fn=recv_fn,
                               write_fn=send_fn,
                               logger=logger)
    gfs.run()

    while True:
        text = input("> ")
        resp = Response(embed=EmbedContent(title=text, description=text))

        gfs.send((resp,))
