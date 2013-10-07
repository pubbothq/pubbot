import gevent.queue
import gevent.pool
from gevent import socket


class LineProtocol(object):

    """ A mixin for implementing line based protocols """

    delimeter = '\n'

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

        self._socket = None
        self._recv_queue = gevent.queue.Queue()
        self._send_queue = gevent.queue.Queue()
        self._group = gevent.pool.Group()

    def start(self):
        address = (socket.gethostbyname(self.hostname), self.port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect(address)

        self._group.spawn(self._send_loop)
        self._group.spawn(self._process_loop)
        self._group.spawn(self._recv_loop)

    def send(self, line):
        self._send_queue.put(''.join((line, self.delimeter)))

    def line_received(self, line):
        pass

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
                line = buf[0:pos]
                self._recv_queue.put(line)
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
            self.line_received(self._recv_queue.get())

