# Copyright 2008-2013 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

