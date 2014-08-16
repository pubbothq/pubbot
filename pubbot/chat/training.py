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

from django.db import connection

from .models import Token, Grouping
from .tokenizer import tokenizer
from .stemmer import stemmer


class Trainer(object):

    """
    An object to train the model with lines of text.

    As an optimisation you can use a context manager to enable extra buffering and delay commits::

        with Learner() as learner:
            for line in corpus:
                learner.learn_text(line)
    """

    def __init__(self, batch_mode=False):
        self.token_cache = {}
        self.grouping_cache = {}
        self.batch_mode = batch_mode
        self._explicit_save = True
        self.cursor = connection.cursor()

    def __enter__(self):
        self._explicit_save = True
        if self.batch_mode:
            self.cursor.execute("PRAGMA journal_mode = memory;")
        return self

    def __exit__(self, *exc):
        [g.save(update_fields=['count']) for g in self.grouping_cache.values()]
        self._explicit_save = False
        if self.batch_mode:
            self.cursor.execute("PRAGMA journal_mode = truncate;")

    def get_token(self, token):
        try:
            return self.token_cache[token]
        except KeyError:
            t = self.token_cache[token] = Token.objects.get_or_create(
                token=token,
                defaults={"stem": stemmer.stem(token)},
            )[0]
            return t

    def get_grouping(self, token1, token2, token3):
        try:
            g = self.grouping_cache[(token1, token2, token3)]
        except KeyError:
            g, created = self.grouping_cache[(token1, token2, token3)], _ = Grouping.objects.get_or_create(
                token1=token1,
                token2=token2,
                token3=token3,
            )
            if created:
                return
        g.count += 1
        if not self._explicit_save:
            g.save()
        return g

    def group_tokens(self, tokens):
        a = None
        b = None
        c = self.get_token(tokens.next())
        yield (a, b, c)

        while c:
            a = b
            b = c
            try:
                c = self.get_token(tokens.next())
            except StopIteration:
                c = None
            yield (a, b, c)

    def learn_tokens(self, tokens):
        for cur in self.group_tokens(tokens):
            self.get_grouping(*cur)

    def learn_string(self, text):
        try:
            tokens = tokenizer.split(text.encode("utf-8"))
        except UnicodeDecodeError:
            return
        return self.learn_tokens(tokens)
