from django.core.management.base import BaseCommand, CommandError
from pubbot.main.celery import app


class Command(BaseCommand):
    args = ''
    help = 'Start irc client in foreground'

    def handle(self, *args, **options):
        app.start(['', 'worker', '-l', 'INFO'])

