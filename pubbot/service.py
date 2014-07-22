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


class BaseService(object):

    def __init__(self, name):
        self.name = name
        self.children = {}
 
    def add_child(self, child):
        if child.name in self.children:
            raise KeyError("Cannot have duplicate service name %r" % child.name)
        self.children[child.name] = name

    def start(self):
        for child in self.children.values():
            gevent.spawn(child.start)

    def stop(self):
        for child in self.children.values():
            child.stop()


class PubbotService(object):

    def __init__(self, name='pubbot'):
        super(PubbotService, self).__init__(name)

        for installed_app in settings.INSTALLED_APPS:
            logger.info("Checking {installed_app} for Service".format(installed_app=installed_app))
            try:
                module = import_module('%s.service' % installed_app)
            except ImportError as e:
                logger.exception(e)
                continue

        if hasattr(module, 'Service'):
            t = type('%s.service.Service' % installed_app, (Service, getattr(module, 'Service')), {})
            self.add_child(t())
