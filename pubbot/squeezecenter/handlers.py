
from urllib import unquote_plus
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

