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

import itertools
import time

from .tokenizer import tokenizer
from .scoring import scorers
from .models import Grouping


def iteruntil(offset, iterable):
    until = time.time() + offset
    return itertools.takewhile(lambda x: until > time.time(), iterable)


def iter_replies_from_tokens(tokens):
    tokens = set(tokens)
    if not tokens:
        raise StopIteration()

    # Do a graph search to get group nodes from tokens and stems
    # (Expected structure is STEM -> TOKEN -> GROUP -> GROUP -> END)

    seen = set()
    for chain in iteruntil(0.5, itertools.cycle(Grouping.iter_random_groupings(tokens))):
        backwards = chain.get_complete_incoming_chains()
        forwards = chain.get_complete_outgoing_chains()

        reply = tuple(backwards.next()) + (chain, ) + tuple(forwards.next())

        if reply not in seen:
            yield reply
            seen.add(reply)


def reply(text):
    tokens = tokenizer.split(text)

    best_score = -1.0
    best_reply = None

    i = 0

    for i, reply in enumerate(iter_replies_from_tokens(tokens)):
        score = scorers.score(reply)

        if score > best_score:
            best_score = score
            best_reply = reply

    print i + 1, "replies generated"

    if best_reply is None:
        return "You make no sense"

    return " ".join(t.token3.token for t in best_reply)