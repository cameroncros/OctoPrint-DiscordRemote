import logging
import socket
import sys
import threading
import time
from typing import List, Tuple, Callable, Optional


class GenericForeverSocket:
    thread: threading.Thread = None
    queued_messages_lock = threading.Lock()
    queued_messages: List[Tuple] = []

    class ConnectionClosed(Exception):
        pass

    class BufferedSocketWrapper:
        def __init__(self, s: socket.socket):
            self.socket: socket.socket = s

        def sendsafe(self, data: bytes):
            try:
                if self.socket.sendall(data) == 0:
                    raise GenericForeverSocket.ConnectionClosed()
            except ConnectionResetError:
                raise GenericForeverSocket.ConnectionClosed()
            except BrokenPipeError:
                raise GenericForeverSocket.ConnectionClosed()

        def peek(self, length: int) -> bytes:
            try:
                tmp = self.socket.recv(length, socket.MSG_PEEK)
                if len(tmp) == 0:
                    raise GenericForeverSocket.ConnectionClosed()
                if len(tmp) < length:
                    raise TimeoutError("Data not ready yet")
                return tmp
            except ConnectionResetError:
                raise GenericForeverSocket.ConnectionClosed()

        def recvblocking(self, length: int) -> bytes:
            """
            Use this sparingly, if ever.
            Ideally, you do not want to block on reading unless
            you know for sure that there is data.
            """
            data = b''
            while len(data) < length:
                try:
                    tmp = self.socket.recv(length-len(data))
                    if len(tmp) == 0:
                        raise GenericForeverSocket.ConnectionClosed()
                    data += tmp
                except ConnectionResetError:
                    raise GenericForeverSocket.ConnectionClosed()
            return data

        def skipahead(self, length):
            """
            This should be used after a series of `peek` calls, to advance the socket.
            """
            self.recvblocking(length)

    def __init__(self,
                 address: str,
                 port: int,
                 init_fn: Callable[[BufferedSocketWrapper], None],
                 read_fn: Callable[[BufferedSocketWrapper], None],
                 write_fn: Callable[[BufferedSocketWrapper, Tuple], None],
                 logger: Optional[logging.Logger] = None):
        self.address = address
        self.port = port
        self.init_fn: Callable[[GenericForeverSocket.BufferedSocketWrapper], None] = init_fn
        self.read_fn: Callable[[GenericForeverSocket.BufferedSocketWrapper], None] = read_fn
        self.write_fn: Callable[[GenericForeverSocket.BufferedSocketWrapper, Tuple], None] = write_fn
        if logger is None:
            self.logger = logging.getLogger("GenericForeverSocket")
        else:
            self.logger = logger
        self.running = True
        self.thread = threading.Thread(target=self.thread_fn)

    def stop(self):
        self.running = False
        try:
            self.thread.join()
        except RuntimeError:
            pass

    def send(self, data: Tuple):
        with self.queued_messages_lock:
            self.queued_messages.append(data)

    def thread_fn(self):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.address, self.port))
                s.setblocking(True)
                s.settimeout(0.1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                if sys.platform != "darwin":
                    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 300)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 300)
                s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2)
            except Exception as e:
                print(e)
                time.sleep(2)
                continue

            safe = GenericForeverSocket.BufferedSocketWrapper(s)
            self.logger.info("Connected")
            if self.init_fn:
                self.init_fn(safe)
            self.logger.info("Initialised")

            try:
                while True:
                    try:
                        self.read_fn(safe)
                    except TimeoutError:
                        pass
                    except socket.timeout:
                        pass

                    if len(self.queued_messages) != 0:
                        with self.queued_messages_lock:
                            self.write_fn(safe, self.queued_messages[0])
                            self.queued_messages.pop()

                    if not self.running:
                        s.close()
                        return

            except GenericForeverSocket.ConnectionClosed as e:
                self.logger.error(e)
                pass
            except Exception as e:
                self.logger.error(f"Exception: [{e}]")
                pass
            self.logger.info("Disconnected")
            # To be safe:
            try:
                s.close()
            except:
                pass

    def run(self):
        self.thread.start()
