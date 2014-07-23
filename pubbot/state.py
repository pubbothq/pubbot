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

import six
from gevent.event import Event


class State(object):
    pass


class Transition(object):

    def __init__(self, from_state, to_state):
        self.from_state = from_state
        self.to_stat = to_state


class TransitionContext(object):

    def __init__(self, machine, new_state):
        self.machine = machine
        self.new_state = new_state

    def __enter__(self):
        self.machine._in_transition = True
        return self

    def __exit__(self, *exc):
        if self.machine.state in self.machine._events:
            self.machine._events[self.machine.state].clear()
        self.machine.state = self.new_state
        self.machine._in_transition = False
        self._events[self.machine.state].set()


class MachineType(type):

    def __new__(meta, class_name, bases, new_attrs):
        filtered_attrs = dict(kv for kv in new_attrs.items() if not isinstance(kv[1], (State, Transition)))
        cls = type.__new__(meta, class_name, bases, filtered_attrs)

        cls.__initial_state__ = None
        cls.__states__ = {}
        cls.__transitions__ = {}

        for b in bases:
            if hasattr(b, "__initial_state__"):
                cls.__initial_state__ = b.__initial__state
            if hasattr(b, "__states__"):
                cls.__states__.update(b.__states__)
            if hasattr(b, "__transitions__"):
                cls.__transitions__.update(b.__transitions__)

        for key, value in new_attrs.items():
            if isinstance(value, State):
                if key in cls.__states__:
                    raise RuntimeError("Duplicate state %r" % key)
                value.name = key
                cls.__states__[key] = value
                if getattr(value, "initial", False):
                    if cls.__initial_state__:
                        raise RuntimeError("State '%r' wants to be initial, but state '%r' is already initial" % (key, cls.__initial_state__))
                    cls.__initial_state__ = key

            elif isinstance(value, Transition):
                if key in cls.__transitions__:
                    raise RuntimeError("Duplicate transition %r" % key)
                value.name = key
                cls.__transitions__[key] = value

        return cls


class Machine(six.with_metaclass(MachineType)):

    def __init__(self, subject):
        self.state = self.__initial_state__
        self._events = dict((state.name, Event()) for state in self.__states__)
        self._in_transition = False

    def wait(self, state, timeout=None):
        if state not in self._events:
            raise RuntimeError("Unable to wait for '{}'".format(state))
        self._events[state].wait(timeout)

    def transition(self, new_state):
        if self._in_transition:
            raise RuntimeError("Cannot transition to %r: Already in transition" % new_state)

        if new_state not in self.__states__:
            raise RuntimeError("'{}' is not a valid state".format(new_state))

        for t in self.__transitions__:
            if t.from_state != self.state:
                continue
            if new_state in t.to_states:
                return TransitionContext(self, new_state)

        raise RuntimeError("No valid transition from '{}' to '{}'".fomat(self.state, new_state))
