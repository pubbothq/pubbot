from io import StringIO

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError

from pubbot.chat.receivers import learn


class TestUtter(TestCase):

    def setUp(self):
        learn(None, content="Happiness is important")

    def test_no_args(self):
        buf = StringIO()
        self.assertRaises(CommandError, call_command, "utter", stdout=buf)

    def test_too_many_args(self):
        buf = StringIO()
        self.assertRaises(CommandError, call_command, "utter", "Chocolate", "is", "important", stdout=buf)

    def test_utter(self):
        buf = StringIO()
        call_command("utter", "Chocolate is important", stdout=buf)
        self.assertEqual(buf.getvalue(), "Happiness is important\n")
