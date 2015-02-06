from unittest import mock

from django.test import TestCase
from django.core.management import call_command


class TestBotCommand(TestCase):

    def test_run(self):
        with mock.patch("pubbot.main.management.commands.bot.bot") as bot:
            call_command("bot")
            bot.start_and_wait.assert_called_with()
