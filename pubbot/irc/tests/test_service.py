from django.test import TestCase
from pubbot.bot import bot


class TestIrcServiceAvailable(TestCase):

    def test_in_bot(self):
        self.assertTrue("pubbot.irc" in bot)
