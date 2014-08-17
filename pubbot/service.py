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
import gevent
import logging

from .state import State, Transition, Machine

logger = logging.getLogger(__name__)


class ServiceState(Machine):

    not_running = State(initial=True)
    running = State()

    starting = Transition(from_state='not_running', to_states=['running'])
    stopping = Transition(from_state='running', to_states=['stopping'])


class BaseService(IterableUserDict, object):

    def __init__(self, name):
        self.name = name
        self.data = {}
        self.parent = None
        self.state = ServiceState()
        self.logger = logging.getLogger("%s.%s[%s]" % (self.__module__, self.__class__.__name__, self.name))

    def add_child(self, child):
        if child.name in self.data:
            raise KeyError("Cannot have duplicate service name %r" % child.name)
        self.disown_parent()
        child.parent = self
        self.data[child.name] = child

        if self.state.state == "running":
            child.start()

    def remove_child(self, child):
        if child.name not in self.data:
            raise KeyError("Cannot remove child %r that not parent of" % child.name)
        del self.data[child.name]
        child.parent = None

    def disown_parent(self):
        if self.parent:
            self.parent.remove_child(self)

    def start(self):
        self.logger.debug("Starting")
        with self.state.transition_to("running"):
            self.start_service()
            for child in self.values():
                child.start()
        self.logger.debug("Finished starting")

    def start_and_wait(self):
        self.start()
        self.state.wait("not_running")

    def stop(self):
        with self.state.transition_to("not_running"):
            for child in self.values():
                child.stop()
            self.stop_service()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, **exc):
        self.stop()

    def start_service(self):
        pass

    def stop_service(self):
        pass

    def __repr__(self):
        return "Service(%s)" % self.name


class TaskService(BaseService):

    """ A service that runs a function and when that function returns the service stops """

    def start_service(self):
        self._task = gevent.spawn(self.run)
        self._task.link(self.stop)

    def run(self):
        raise NotImplementedError(self.run)
