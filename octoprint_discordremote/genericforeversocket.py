import socket
import threading
import time
from typing import List, Tuple, Callable


class GenericForeverSocket:
    thread: threading.Thread = None
    queued_messages_lock = threading.Lock()
    queued_messages: List[Tuple] = []

    class ConnectionClosed(Exception):
        pass

    class SocketWrapper:
        def __init__(self, s: socket):
            self.socket = s

        def sendsafe(self, data: bytes):
            try:
                if self.socket.sendall(data) == 0:
                    raise GenericForeverSocket.ConnectionClosed()
            except ConnectionResetError:
                raise GenericForeverSocket.ConnectionClosed()
            except BrokenPipeError:
                raise GenericForeverSocket.ConnectionClosed()

        def recvsafe(self, length: int) -> bytes:
            try:
                data = self.socket.recv(length)
                if len(data) == 0:
                    raise GenericForeverSocket.ConnectionClosed()
                return data
            except ConnectionResetError:
                raise GenericForeverSocket.ConnectionClosed()

    def __init__(self, address: str, port: int, init_fn, read_fn, write_fn):
        self.address = address
        self.port = port
        self.init_fn: Callable[[GenericForeverSocket.SocketWrapper], None] = init_fn
        self.read_fn: Callable[[GenericForeverSocket.SocketWrapper], bytes] = read_fn
        self.write_fn: Callable[[GenericForeverSocket.SocketWrapper, Tuple], None] = write_fn
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
            except Exception as e:
                time.sleep(2)
                continue

            safe = GenericForeverSocket.SocketWrapper(s)
            print("Connected")
            if self.init_fn:
                self.init_fn(safe)

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

            except GenericForeverSocket.ConnectionClosed:
                pass
            except Exception as e:
                print(f"Exception: [{e}]")
                pass
            print("Disconnected")
            # To be safe:
            try:
                s.close()
            except:
                pass

    def run(self):
        self.thread.start()
