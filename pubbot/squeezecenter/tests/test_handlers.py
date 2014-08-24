import mock
import unittest

from pubbot.squeezecenter.handlers import CurrentSongHandler, StopHandler


class TestCurrentSongHandler(unittest.TestCase):

    def test_start(self):
        conn = mock.Mock()
        c = CurrentSongHandler()
        c.start(conn)
        self.assertEqual(conn.send.call_args_list, [
            mock.call('title ?'),
            mock.call('album ?'),
            mock.call('artist ?'),
        ])

    def test_song_changed(self):
        conn = mock.Mock()
        c = CurrentSongHandler()
        c(conn, ["playlist", "newsong :D"])
        self.assertEqual(conn.send.call_args_list, [
            mock.call('title ?'),
            mock.call('album ?'),
            mock.call('artist ?'),
        ])

    def test_song_started(self):
        conn = mock.Mock()
        c = CurrentSongHandler()

        with mock.patch("pubbot.squeezecenter.signals.song_started") as song_started:
            c(conn, ["artist", "Blinkin Lark"])
            c(conn, ["album", "Cometora"])
            c(conn, ["title", "At The Start"])

            song_started.send_robust.assert_called_with(
                sender=conn,
                artist="Blinkin Lark",
                album="Cometora",
                title="At The Start",
            )


class TestStopHandler(unittest.TestCase):

    def test_song_stopped(self):
        s = StopHandler()
        conn = mock.Mock()
        with mock.patch("pubbot.squeezecenter.signals.music_stopped") as music_stopped:
            s(conn, ["playlist", "stop"])

            music_stopped.send_robust.assert_called_with(
                sender=conn,
            )
