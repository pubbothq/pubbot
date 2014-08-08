# Copyright 2008-2014 the original author or authors
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

from gevent import monkey
monkey.patch_all()

from gevent_psycopg2 import monkey_patch
monkey_patch()

from django.core.management.base import BaseCommand

from pubbot import service


class Command(BaseCommand):
    args = ''
    help = 'Apply any migrations to this site'

    def handle(self, *args, **options):
        pubbot = service.PubbotService()
        pubbot.start_and_wait()