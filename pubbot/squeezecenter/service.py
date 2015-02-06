# Copyright 2008-2013 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from urllib.parse import unquote_plus
import eventlet.queue
import eventlet
import socket
import greenlet

from pubbot import service
from pubbot.squeezecenter import handlers
from pubbot.utils import force_str, force_bytes


class SqueezeCenterConnection(object):

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

        self._socket = None
        self._recv_queue = eventlet.queue.Queue()
        self._send_queue = eventlet.queue.Queue()
        self._group = []

        self.handlers = []

    def start(self):
        address = (socket.gethostbyname(self.hostname), self.port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(address)

        self.send('listen 1')

        self._group.append(eventlet.spawn(self._send_loop))
        self._group.append(eventlet.spawn(self._process_loop))
        self._group.append(eventlet.spawn(self._recv_loop))

    def send(self, command):
        self._send_queue.put('%s\n' % command)

    def join(self):
        # self._group.join()
        pass

    def stop(self):
        for t in self._group:
            t.kill()
        if self._socket is not None:
            self._socket.shutdown(2)
            self._socket.close()
            self._socket = None

    def reconnect(self, delay=1, flush=True):
        self.stop()
        self.join()
        if flush:
            self._send_queue.queue.clear()
        eventlet.sleep(delay)
        self.start()

    def add_handler(self, handler):
        self.handlers.append(handler)
        if hasattr(handler, 'start'):
            handler.start(self)

    def _recv_loop(self):
        buf = b''
        while True:
            try:
                data = self._socket.recv(512)
            except greenlet.GreenletExit:
                raise
            except Exception:
                eventlet.spawn(self.reconnect)

            buf += data
            pos = buf.find(b"\n")
            while pos >= 0:
                line = unquote_plus(force_str(buf[0:pos]))
                parts = line.split(' ')

                if len(parts) >= 3:
                    parts = line.split(' ', 2)
                    parts.pop(0)
                    self._recv_queue.put(parts)
                else:
                    # print len(parts), line
                    pass

                buf = buf[pos + 1:]
                pos = buf.find("\n")

    def _send_loop(self):
        while True:
            command = force_bytes(self._send_queue.get())
            try:
                self._socket.sendall(command)
            except Exception:
                eventlet.spawn(self.reconnect)
                return

    def _process_loop(self):
        while True:
            data = self._recv_queue.get()
            for handler in self.handlers:
                self._group.append(eventlet.spawn(handler, self, data))


class Service(service.BaseService):

    def start_service(self):
        self.client = SqueezeCenterConnection('music', 9090)

        self.client.add_handler(handlers.CurrentSongHandler())
        self.client.add_handler(handlers.StopHandler())
        # self.client.add_handler(handlers.DebugHandler())

        self.client.start()
