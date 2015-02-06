import os
from io import StringIO

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError


class TestRead(TestCase):

    def test_no_log_specified(self):
        buf = StringIO()
        self.assertRaises(CommandError, call_command, 'read', stdout=buf)

    def test_only_one_log_file(self):
        buf = StringIO()
        self.assertRaises(CommandError, call_command, 'read', 'foo.log', 'bar.log', stdout=buf)

    def test_logfile_not_found(self):
        buf = StringIO()
        self.assertRaises(CommandError, call_command, 'read', 'foo.log', stdout=buf)

    def test_read_irssi_log(self):
        buf = StringIO()
        call_command('read', os.path.join(os.path.dirname(__file__), "test_management_commands_read.log"), ignored_nick=['tom'], stdout=buf)
