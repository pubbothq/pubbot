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

from __future__ import absolute_import

from celery import Celery
from django.conf import settings
from django.utils.importlib import import_module


app = Celery('pubbot.main')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(settings.INSTALLED_APPS, related_name='tasks')


class Bootstep(object):

    def start(self, worker):
        if self.queue not in worker.app.amqp.queues:
            return
        return super(Bootstep, self).start(worker)

    def stop(self, worker):
        if self.queue not in worker.app.amqp.queues:
            return
        return super(Bootstep, self).stop(worker)


# Find all custom bootsteps and register them with the worker boot process
for installed_app in settings.INSTALLED_APPS:
    try:
        module = import_module('%s.bootsteps' % installed_app)
    except ImportError:
        continue

    # If an app defines .bootsteps.Bootstep then register it against a worker.
    # We adapt it so that its inert unless the queue it is interested in is
    # active
    if hasattr(module, 'Bootstep'):
        t = type('%s.bootsteps.Bootstep' %
                 installed_app, (Bootstep, getattr(module, 'Bootstep')), {})
        app.steps['worker'].add(t)
