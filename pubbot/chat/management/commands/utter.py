
from django.core.management.base import BaseCommand, CommandError

from pubbot.chat.writing import reply


class Command(BaseCommand):
    args = '<msg>'
    help = 'Generate a reply to <msg>'

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("No input text")
        elif len(args) > 1:
            raise CommandError("Make sure your input is quite")
        self.stdout.write(reply(args[0]))
