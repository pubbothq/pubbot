import gevent.queue
import gevent.pool
from gevent import socket
from urllib import unquote_plus
from websocket import create_connection
import json


class BuildbotConnection(object):

    def __init__(self, url):
        self.url = url
        self._group = gevent.pool.Group()

    def start(self):
        self._group.spawn(self._recv_loop)

    def join(self):
        self._group.join()

    def stop(self):
        self._group.kill()

    def _recv_loop(self):
        self.running = True

        ws = create_connection(self.url)
        while self.running:
            build = json.loads(ws.recv())
            self.owner.mq.post(topic='ci', **build)

        ws.stop()


