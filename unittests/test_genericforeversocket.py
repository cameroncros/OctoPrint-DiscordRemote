import time
from unittest import TestCase

from octoprint_discordremote.genericforeversocket import GenericForeverSocket


class TestDiscordLink(TestCase):

    def test_start_stop_rapid(self):
        gfs = GenericForeverSocket(address='127.0.0.1', port=34567, read_fn=(), write_fn=(),
                                   init_fn=())
        gfs.run()
        gfs.stop()

    def test_basic_never_connected(self):
        gfs = GenericForeverSocket(address='127.0.0.1', port=34567, read_fn=(), write_fn=(),
                                   init_fn=())
        gfs.run()

        for i in range(3):
            gfs.send((f'{i}\n'.encode(),))
            time.sleep(1)

        gfs.stop()

        self.assertEqual(3, len(gfs.queued_messages))
