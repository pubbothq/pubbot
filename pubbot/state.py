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
    def __init__(self, initial=False):
        self.initial = initial


class Transition(object):

    def __init__(self, from_state, to_states):
        self.from_state = from_state
        self.to_states = to_states


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
        self.machine._events[self.machine.state].set()


class MachineType(type):

    def __new__(meta, class_name, bases, new_attrs):
        attrs = dict(kv for kv in new_attrs.items() if not isinstance(kv[1], (State, Transition)))

        attrs['__initial_state__'] = None
        states = attrs['__states__'] = {}
        transitions = attrs['__transitions__'] = {}

        cls = type.__new__(meta, class_name, bases, attrs)

        for b in bases:
            if hasattr(b, "__initial_state__"):
                cls.__initial_state__ = b.__initial_state__
            if hasattr(b, "__states__"):
                states.update(b.__states__)
            if hasattr(b, "__transitions__"):
                transitions.update(b.__transitions__)

        for key, value in new_attrs.items():
            if isinstance(value, State):
                if key in states:
                    raise RuntimeError("Duplicate state %r" % key)
                value.name = key
                states[key] = value
                if getattr(value, "initial", False):
                    if cls.__initial_state__:
                        raise RuntimeError("State '%r' wants to be initial, but state '%r' is already initial" % (key, cls.__initial_state__))
                    cls.__initial_state__ = key

            elif isinstance(value, Transition):
                if key in transitions:
                    raise RuntimeError("Duplicate transition %r" % key)
                value.name = key
                transitions[key] = value

        if states and not cls.__initial_state__:
            raise RuntimeError("%s: One state must be declared as the initial state" % cls)

        return cls


class Machine(six.with_metaclass(MachineType)):

    def __init__(self):
        self.state = self.__initial_state__
        self._events = dict((state, Event()) for state in self.__states__)
        self._in_transition = False

    def wait(self, state, timeout=None):
        if state not in self._events:
            raise RuntimeError("Unable to wait for '{}'".format(state))
        self._events[state].wait(timeout)

    def transition_to(self, new_state):
        if self._in_transition:
            raise RuntimeError("Cannot transition to %r: Already in transition" % new_state)

        if new_state not in self.__states__:
            raise RuntimeError("'{}' is not a valid state".format(new_state))

        for t in self.__transitions__.values():
            if t.from_state != self.state:
                continue
            if new_state in t.to_states:
                return TransitionContext(self, new_state)

        raise RuntimeError("No valid transition from '{}' to '{}'".fomat(self.state, new_state))
