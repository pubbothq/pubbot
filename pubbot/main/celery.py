from __future__ import absolute_import

from celery import Celery
from django.conf import settings

app = Celery('pubbot.main')
app.config_from_object(settings)
app.autodiscover_tasks(settings.INSTALLED_APPS, related_name='tasks')

from pubbot.irc.bootsteps import IrcStep
app.steps['worker'].add(IrcStep)

from pubbot.squeezecenter.bootsteps import SqueezeCenterStep
app.steps['worker'].add(SqueezeCenterStep)

