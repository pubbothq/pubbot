from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from pubbot.main.celery import app


class Command(BaseCommand):
    args = ''
    help = 'Start a celery worker'

    option_list = BaseCommand.option_list + (
        make_option('--queues',
            action='append',
            dest='queues',
            default=[],
            help='Queues to process',
            ),
        make_option('--name',
            action='store',
            dest='name',
            default=None,
            help='Name of worker',
            ),
        )

    def handle(self, *args, **options):
        command = ['', 'worker', '-l', 'INFO']
        if options['queues']:
            command.extend(('-Q', ','.join(options['queues'])))
        if options['name']:
            command.extend(('-n', options['name']))
        app.start(command)

