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


from . import signals


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
                signals.song_start.send(
                    sender=conn,
                    artist=self.artist,
                    album=self.album,
                    title=self.title
                )
                self.title = self.artist = self.title = None

        elif message[0] == 'playlist' and message[1].startswith('newsong '):
            self.request_track_details(conn)


class StopHandler(object):

    def __call__(self, conn, message):
        if message[0] == 'playlist' and message[1] == 'stop':
            signals.music_stop.send(
                sender=conn,
            )
