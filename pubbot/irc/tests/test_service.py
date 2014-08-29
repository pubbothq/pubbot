import mock

from django.test import TestCase

from pubbot.bot import bot
from pubbot.irc.models import Network, Room
from pubbot.irc.service import Service


class TestIrcServiceAvailable(TestCase):

    def test_in_bot(self):
        self.assertTrue("pubbot.irc" in bot)

    def test_connect(self):
        n = Network.objects.create(server='localhost', port='1234', nick='fred', nickserv_password='password')
        Room.objects.create(server=n, name="#example")

        with mock.patch("gevent.spawn"):
            with mock.patch("pubbot.irc.service.Client"):
                s = Service("irc")
                s.start()
                s.state.wait("running")

        s['localhost'].client.start.assert_called_with()
