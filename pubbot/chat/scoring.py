# Copyright 2014 the original author or authors
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

from django.conf import settings
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string


class Scorers(object):

    def __init__(self):
        self.scorers = []

    def add(self, weight, scorer):
        self.scorers.append((weight, scorer))

    def score(self, reply):
        return 1.0


class BaseScorer(object):

    def __init__(self):
        pass

    def score(self, reply):
        return NotImplementedError(self.score)


class LengthScorer(BaseScorer):

    def score(self, reply):
        if len(reply) < 5:
            return 0.5
        if len(reply) > 20:
            return 0
        return len(reply)


DEFAULT_SCORING = [
    (1.0, ".".join((__name__, "LengthScorer")))
]


class ConfiguredScorers(LazyObject):

    def _setup(self):
        scorers = Scorers()
        for weight, scorer in getattr(settings, "CHAT_SCORERS", DEFAULT_SCORING):
            scorers.add(weight, import_string(scorer)())
        self._wrapped = scorers


scorers = ConfiguredScorers()
