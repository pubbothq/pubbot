from unittest import mock

from django.test import TestCase

from pubbot.bot import bot
from pubbot.irc.models import Network, Room
from pubbot.irc.service import Service, ChannelService


class TestIrcChannel(TestCase):

    def setUp(self):
        self.n = Network.objects.create(server='localhost')
        self.r = Room.objects.create(
            name='#example',
            subscribes_tags='default',
            blocks_tags='silly',
            server=self.n,
        )
        self.s = ChannelService(self.r)
        self.s.parent = mock.Mock()

    def test_maybe_say(self):
        self.assertEqual(
            self.s._maybe_say(None, 'Hello', tags=['default']),
            True,
        )
        self.s.parent.client.connection.privmsg.assert_called_with("#example", "Hello")

    def test_maybe_say_action(self):
        self.assertEqual(
            self.s._maybe_say(None, 'Hello', tags=['default'], action=True),
            True,
        )
        self.assertEqual(self.s.parent.client.connection.action.called, 1)

    def test_maybe_say_notice(self):
        self.assertEqual(
            self.s._maybe_say(None, 'Hello', tags=['default'], notice=True),
            True,
        )
        self.assertEqual(self.s.parent.client.connection.notice.called, 1)

    def test_maybe_not_say(self):
        self.assertEqual(
            self.s._maybe_say(None, 'Hello', tags=['serious']),
            False,
        )
        self.assertEqual(self.s.parent.client.msg.called, 0)

    def test_maybe_say_blocked(self):
        self.assertEqual(
            self.s._maybe_say(None, 'Hello', tags=['default', 'silly']),
            False,
        )
        self.assertEqual(self.s.parent.client.msg.called, 0)


class TestIrcServiceAvailable(TestCase):

    def test_in_bot(self):
        self.assertTrue("pubbot.irc" in bot)


class TestIrcService(TestCase):

    def test_connect(self):
        return

        n = Network.objects.create(server='localhost', port='1234', nick='fred', nickserv_password='password')
        Room.objects.create(server=n, name="#example")

        with mock.patch("eventlet.spawn"):
            with mock.patch("pubbot.irc.service.Client"):
                s = Service("irc")
                s.start()
                s.state.wait("running")

        s['localhost'].client.start.assert_called_with()

        with mock.patch("eventlet.sleep") as sleep:
            sleep.side_effect = [None, StopIteration()]
            try:
                s['localhost']._ping_loop()
            except StopIteration:
                pass
            self.assertEqual(s['localhost'].client.send_message.called, 1)
