import contextlib
import random
import time
from socket import socket
from unittest import TestCase

from octoprint_discordremote.genericforeversocket import GenericForeverSocket

null_init = lambda x: None
null_read = lambda x: None
null_write = lambda x, y: None

class TestDiscordLink(TestCase):

    def rand_port(self):
        return random.randint(10000, 65534)

    def test_start_stop_rapid(self):
        gfs = GenericForeverSocket(address='127.0.0.1', port=self.rand_port(), read_fn=null_read, write_fn=null_write,
                                   init_fn=null_init)
        gfs.run()
        with self.timer(3):
            gfs.stop()

    def test_basic_never_connected(self):
        gfs = GenericForeverSocket(address='127.0.0.1', port=self.rand_port(), read_fn=null_read, write_fn=null_write,
                                   init_fn=null_init)
        gfs.run()

        for i in range(3):
            gfs.send((f'{i}\n'.encode(),))
            time.sleep(1)

        with self.timer(2):
            gfs.stop()

        self.assertEqual(3, len(gfs.queued_messages))

    def test_non_blocking(self):
        port = self.rand_port()
        gfs = GenericForeverSocket(address='127.0.0.1', port=port, read_fn=null_read, write_fn=null_write,
                                   init_fn=null_init)
        gfs.run()

        s = socket()
        s.bind(('127.0.0.1', port))
        s.listen()
        client, addr = s.accept()
        # gfs connected, and we have accepted the connection.

        with self.timer(2):
            gfs.stop()
        client.close()
        s.close()

    def test_partial_recv(self):
        def read_fn(s: GenericForeverSocket.BufferedSocketWrapper):
            data = s.peek(4)
        port = self.rand_port()
        gfs = GenericForeverSocket(address='127.0.0.1', port=port, read_fn=read_fn, write_fn=null_write,
                                   init_fn=null_init)
        gfs.run()

        s = socket()
        s.bind(('127.0.0.1', port))
        s.listen()
        client, addr = s.accept()
        client.send(b'123')  # Expecting 4 bytes, but only sent 4
        # gfs connected, and we have accepted the connection.

        with self.timer(2):
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
