import mock

from django.test import TestCase
from django.core.cache import caches

from pubbot.squeezecenter import receivers


class TestSongNotification(TestCase):

    def test_notification(self):
        with mock.patch("pubbot.squeezecenter.receivers.say") as say:
            receivers.current_song_notification(
                None,
                title="At The Start",
                album="Cometora",
                artist="Blinkin Lark",
            )
            say.assert_called_with(
                content="At The Start - Blinkin Lark (Cometora)",
                tags=['current_song_notification'],
                notice=True,
            )


class TestSkipping(TestCase):

    def setUp(self):
        caches['default'].clear()

    def test_get(self):
        self.assertEqual(receivers.get_current_skip(), None)

    def test_set(self):
        skip = {"skip": set(["fred"])}
        receivers.set_current_skip(skip)
        skip = receivers.get_current_skip()
        self.assertTrue("last_update" in skip)
        self.assertEqual(skip["skip"], set(["fred"]))

    def test_skip_in_progress(self):
        receivers.set_current_skip({})
        r = receivers.requested_skip(None, content="skip 20", user="fred")
        self.assertEqual(r['content'], "Vote already in progress; can't start another")

    def test_skip_zero(self):
        r = receivers.requested_skip(None, content="skip 0", user="fred")
        self.assertEqual(r['content'], "Don't be daft")

    def test_change_vote_to_skip(self):
        receivers.set_current_skip({
            "number": 1,
            "noskip": set(["fred"]),
            "skip": set(),
        })
        r = receivers.requested_skip(None, content="skip", user="fred")
        self.assertEqual(r['content'], "fred voted to skip! 2 more votes required")

    def test_change_vote_to_noskip(self):
        receivers.set_current_skip({
            "number": 1,
            "skip": set(["fred"]),
            "noskip": set(),
        })
        r = receivers.requested_noskip(None, content="noskip", user="fred")
        self.assertEqual(r['content'], "fred voted to noskip! 4 more votes required")

    def test_noskip_novote(self):
        r = receivers.requested_noskip(None, content="noskip", user="fred")
        self.assertEqual(r['content'], "There isn't a vote in progres..")

    def test_timeout(self):
        with mock.patch("pubbot.squeezecenter.receivers.time") as time:
            with mock.patch("gevent.sleep"):
                time.time.side_effect = [0, 0, 0, 0, 1000000]
                receivers.set_current_skip({})
                receivers.timeout_current_skip()

    def test_create_skip(self):
        with mock.patch("gevent.spawn"):
            receivers.requested_skip(None, content="skip", user="fred")

    def test_actually_skip(self):
        receivers.set_current_skip({
            "number": 1,
            "skip": set(["fred", "tommy", "dave", "sarah"]),
            "noskip": set(),
        })
        with mock.patch("random.choice") as choice:
            choice.side_effect = lambda x: x[0]
            with mock.patch("pubbot.squeezecenter.receivers.command") as command:
                r = receivers.requested_skip(None, content="skip", user="pixel")
                command.assert_called_with("playlist index +1")
        self.assertEqual(r['content'], "Good riddance.")


class TestRemoteControl(TestCase):

    def test_canhas(self):
        with mock.patch("pubbot.squeezecenter.receivers.command") as command:
            r = receivers.canhas(None, content='canhas blinkin lark')
            command.assert_called_with("playlist loadtracks contributor.namesearch=blinkin+lark")
        self.assertEqual(r['had_side_effect'], True)

    def test_canhaslater(self):
        with mock.patch("pubbot.squeezecenter.receivers.command") as command:
            r = receivers.canhaslater(None, content='canhaslater blinkin lark')
            command.assert_called_with("playlist addtracks contributor.namesearch=blinkin+lark")
        self.assertEqual(r['had_side_effect'], True)

    def test_doeswant(self):
        with mock.patch("pubbot.squeezecenter.receivers.command") as command:
            r = receivers.doeswant(None, content='doeswant at the start')
            command.assert_called_with("playlist loadtracks track.titlesearch=at+the+start")
        self.assertEqual(r['had_side_effect'], True)

    def test_doeswantlater(self):
        with mock.patch("pubbot.squeezecenter.receivers.command") as command:
            r = receivers.doeswantlater(None, content='doeswantlater at the start')
            command.assert_called_with("playlist addtracks track.titlesearch=at+the+start")
        self.assertEqual(r['had_side_effect'], True)

    def test_random_song(self):
        with mock.patch("pubbot.squeezecenter.receivers.command") as command:
            with mock.patch("random.choice") as choice:
                choice.side_effect = lambda x: x[0]
                r = receivers.random_song(None, content='random')
            command.assert_called_with("playlist loadtracks track.titlesearch=A")
        self.assertEqual(r['had_side_effect'], True)
