from django.test import TestCase

from pubbot.irc.models import Network


class TestNetwork(TestCase):

    def test_repr(self):
        n = Network.objects.create(nick='pubbot', server='localhost', port=8080)
        self.assertEqual(repr(n), "<Network: localhost>")

    def test_str(self):
        n = Network.objects.create(nick='pubbot', server='localhost', port=8080)
        self.assertEqual(str(n), "localhost")
