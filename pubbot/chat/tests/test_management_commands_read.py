import os
import StringIO as StringIO

from django.test import TestCase
from django.core.management import call_command

from pubbot.chat.models import Token, Grouping


class TestRead(TestCase):

    def test_read_irssi_log(self):
        buf = StringIO.StringIO()
        call_command('read', os.path.join(os.path.dirname(__file__), "test_management_commands_read.log"), stdout=buf)
        self.assertEqual(Token.objects.count(), 11)
        self.assertEqual(Grouping.objects.count(), 13)
