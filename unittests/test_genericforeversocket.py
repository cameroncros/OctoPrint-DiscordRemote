import contextlib
import time
from socket import socket
from unittest import TestCase

from octoprint_discordremote.genericforeversocket import GenericForeverSocket


class TestDiscordLink(TestCase):

    def test_start_stop_rapid(self):
        gfs = GenericForeverSocket(address='127.0.0.1', port=34567, read_fn=(), write_fn=(),
                                   init_fn=())
        gfs.run()
        with self.timer(3):
            gfs.stop()

    def test_basic_never_connected(self):
        gfs = GenericForeverSocket(address='127.0.0.1', port=34567, read_fn=(), write_fn=(),
                                   init_fn=())
        gfs.run()

        for i in range(3):
            gfs.send((f'{i}\n'.encode(),))
            time.sleep(1)

        with self.timer(1):
            gfs.stop()

        self.assertEqual(3, len(gfs.queued_messages))

    def test_non_blocking(self):
        gfs = GenericForeverSocket(address='127.0.0.1', port=34567, read_fn=(), write_fn=(),
                                   init_fn=())
        gfs.run()

        s = socket()
        s.bind(('127.0.0.1', 34567))
        s.listen()
        client, addr = s.accept()
        # gfs connected, and we have accepted the connection.

        with self.timer(1):
            gfs.stop()
        client.close()
        s.close()

    def test_partial_recv(self):
        def read_fn(s: GenericForeverSocket.BufferedSocketWrapper):
            data = s.peek(4)

        gfs = GenericForeverSocket(address='127.0.0.1', port=34567, read_fn=read_fn, write_fn=(),
                                   init_fn=())
        gfs.run()

        s = socket()
        s.bind(('127.0.0.1', 34567))
        s.listen()
        client, addr = s.accept()
        client.send(b'123')  # Expecting 4 bytes, but only sent 4
        # gfs connected, and we have accepted the connection.

        with self.timer(1):
            gfs.stop()
        client.close()
        s.close()

    @contextlib.contextmanager
    def timer(self, seconds):
        # Start the timer
        start = time.time()
        yield

        # End the timer
        end = time.time()
        if end-start > seconds:
            self.fail(f"Test took too long - Expected [{seconds}s], was [{end-start}s]")
