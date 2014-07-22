# Copyright 2014 John Carr
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

from UserDict import IterableUserDict
from gevent.pool import Group
from gevent.event import AsyncResult
import gevent
import logging

from django.conf import settings
from django.utils.importlib import import_module


logger = logging.getLogger(__name__)


class BaseService(IterableUserDict, object):

    def __init__(self, name):
        self.name = name
        self.data = {}
        self.parent = None
        self.stopping = False
        self.result = AsyncResult()

    def spawn(self, func, *args, **kwargs):
        return self.parent.spawn(func, *args, **kwargs)

    def add_child(self, child):
        if child.name in self.data:
            raise KeyError("Cannot have duplicate service name %r" % child.name)
        self.disown_parent()
        child.parent = self
        self.data[child.name] = child

    def remove_child(self, child):
        if child.name not in self.data:
            raise KeyError("Cannot remove child %r that not parent of" % child.name)
        del self.data[child.name]
        child.parent = None

    def disown_parent(self):
        if self.parent:
            self.parent.remove_child(self)

    def start(self):
        for child in self.values():
            child.start()
        gevent.spawn(self.run).rawlink(self.result)

    def stop(self):
        for child in self.values():
            child.stop()
        self.stopping = True

    def wait(self):
        """ Start a service and wait for it to finish running """
        return self.result.get()

    def run(self):
        pass


class PubbotService(BaseService):

    def __init__(self, name='pubbot'):
        super(PubbotService, self).__init__(name)

        for installed_app in settings.INSTALLED_APPS:
            logger.info("Checking {installed_app} for Service".format(installed_app=installed_app))
            try:
                module = import_module('%s.service' % installed_app)
            except ImportError:
                continue

            if hasattr(module, 'Service'):
                Service = getattr(module, 'Service')
                self.add_child(Service(name=installed_app))

    def run(self):
        while not self.stopping:
            gevent.sleep(100)
