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

import os
import time

from .tokenizer import tokenizer
from .scoring import scorers
from .brain import brain


with open(os.path.join(os.path.dirname(__file__), "stopwords.txt")) as fp:
    STOP_WORDS = set(fp.read().split("\n"))


def iteruntil(offset, iterable):
    yield iterable.next()
    until = time.time() + offset
    while until > time.time():
        yield iterable.next()


def iter_replies_from_tokens(tokens):
    tokens = set(tokens)
    stokens = tokens.difference(STOP_WORDS)
    if stokens:
        tokens = stokens
    tokens = list(tokens)

    for chain, score in iteruntil(0.5, brain.get_chains_from_tokens(tokens)):
        yield chain, score


def reply(text):
    tokens = tokenizer.split(text)

    best_score = -1.0
    best_reply = None

    i = 0

    for i, reply in enumerate(iter_replies_from_tokens(tokens)):
        score = scorers.score(*reply)

        if not best_score or score > best_score:
            best_score = score
            best_reply = reply[0]

    if best_reply is None:
        return "You make no sense"

    return " ".join(t for t in best_reply)
