import StringIO as StringIO

from django.test import TestCase
from django.core.management import call_command

from pubbot.chat.receivers import learn


class TestUtter(TestCase):

    def setUp(self):
        learn(None, content="Happiness is important")

    def test_read_irssi_log(self):
        buf = StringIO.StringIO()
        call_command("utter", "Chocolate is important", stdout=buf)
        self.assertEqual(buf.getvalue(), "Happiness is important\n")
