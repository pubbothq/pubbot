
from urllib import unquote_plus
from django.core.management.base import BaseCommand, CommandError
import gevent.queue
import gevent.pool
from gevent import socket

from pubbot.main.utils import broadcast


class DebugHandler(object):

    def __call__(self, conn, message):
        # print message
        pass


class CurrentSongHandler(object):

    def __init__(self):
        self.title = self.album = self.artist = None

    def start(self, conn):
        self.request_track_details(conn)

    def request_track_details(self, conn):
        self.title = self.artist = self.title = None
        conn.send('title ?')
        conn.send('album ?')
        conn.send('artist ?')

    def __call__(self, conn, message):
        if message[0] in ('artist', 'album', 'title'):
            setattr(self, message[0], message[1])

            if self.title and self.album and self.artist:
                broadcast(
                    kind="music.start",
                    artist=self.artist,
                    album=self.album,
                    title=self.title
                    )
                self.title = self.artist = self.title = None

        elif message[0] =='playlist' and message[1].startswith('newsong '):
            self.request_track_details(conn)


class StopHandler(object):

    def __call__(self, conn, message):
        if message[0] == 'playlist' and message[1] == 'stop':
            broadcast(
                kind='music.stop',
                )


class SqueezeCenterConnection(object):

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

        self._socket = None
        self._recv_queue = gevent.queue.Queue()
        self._send_queue = gevent.queue.Queue()
        self._group = gevent.pool.Group()

        self.handlers = []
        self.add_handler(CurrentSongHandler())
        self.add_handler(StopHandler())
        self.add_handler(DebugHandler())

    def start(self):
        address = (socket.gethostbyname(self.hostname), self.port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(address)

        self.send('listen 1')

        self._group.spawn(self._send_loop)
        self._group.spawn(self._process_loop)
        self._group.spawn(self._recv_loop)

    def send(self, command):
        self._send_queue.put('%s\n' % command)

    def join(self):
        self._group.join()

    def stop(self):
        self._group.kill()
        if self._socket is not None:
            self._socket.shutdown(2)
            self._socket.close()
            self._socket = None

    def reconnect(self, delay=1, flush=True):
        self.stop()
        self.join()
        if flush:
            self._send_queue.queue.clear()
        gevent.sleep(delay)
        self.start()

    def add_handler(self, handler):
        self.handlers.append(handler)
        if hasattr(handler, 'start'):
            handler.start(self)

    def _recv_loop(self):
        buf = ''
        while 1:
            try:
                data = self._socket.recv(512)
            except gevent.GreenletExit:
                raise
            except Exception as e:
                gevent.spawn(self.reconnect)

            buf += data
            pos = buf.find("\n")
            while pos >= 0:
                line = unquote_plus(buf[0:pos])
                parts = line.split(' ')

                if len(parts) >= 3:
                    parts = line.split(' ', 2)
                    parts.pop(0)
                    self._recv_queue.put(parts)
                else:
                    #print len(parts), line
                    pass

                buf = buf[pos + 1:]
                pos = buf.find("\n")

    def _send_loop(self):
        while 1:
            command = self._send_queue.get()
            try:
                enc_cmd = command.decode('utf8')
            except UnicodeDecodeError:
                try:
                    enc_cmd = command.decode('latin1')
                except UnicodeDecodeError:
                    continue

            enc_cmd = enc_cmd.encode('utf8', 'ignore')
            try:
                self._socket.sendall(enc_cmd)
            except Exception as e:
                gevent.spawn(self.reconnect)
                return

    def _process_loop(self):
        while 1:
            data = self._recv_queue.get()
            for handler in self.handlers:
                self._group.spawn(handler, self, data)


class Command(BaseCommand):
    args = ''
    help = 'Connect to a squeeze center an emit events about its doings'

    def handle(self, hostname, port, **options):
        c = SqueezeCenterConnection(hostname, port)
        c.start()
        c.join()

