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
import random

from django.db import models
from django.db.models import Q

from .stemmer import stemmer


with open(os.path.join(os.path.dirname(__file__), "stopwords.txt")) as fp:
    STOP_WORDS = set(fp.read().split("\n"))


class Token(models.Model):

    token = models.TextField(db_index=True)
    stem = models.TextField(db_index=True)


class Grouping(models.Model):

    token1 = models.ForeignKey(Token, null=True, related_name='+')
    token2 = models.ForeignKey(Token, null=True, related_name='+')
    token3 = models.ForeignKey(Token, null=True, related_name='+')
    count = models.IntegerField(default=1)

    class Meta:
        index_together = (
            ('token1', 'token2'),
            ('token2', 'token3'),
        )
        unique_together = (
            ('token1', 'token2', 'token3'),
        )

    def __repr__(self):
        t1 = getattr(self.token1, "token", "")
        t2 = getattr(self.token2, "token", "")
        t3 = getattr(self.token3, "token", "")
        return repr((t1, t2, t3))

    @classmethod
    def iter_random_groupings(cls, tokens):
        """
        Given a list of tokens like ["dog", "cat", "freddy"], yield random groups to generate chains from::

            >>> gen = Grouping.iter_random_groupings(["dog", "cat", "freddy"])
            >>> gen.next()
            ... ("have", "a", "cat")
            >>> gen.next()
            ... ("dog", "has", "fur")
            >>> gen.next()
            ... ("freddy", "likes", "herbs")
        """
        not_a_stop_word = lambda x: x not in STOP_WORDS
        tokens = set(filter(not_a_stop_word, tokens))
        stems = set(filter(not_a_stop_word, stemmer.stem_many(tokens)))

        groupings = list(Grouping.objects.filter(
            Q(token3__token__in=tokens) | Q(token3__stem__in=stems)
        ).distinct())

        random.shuffle(groupings)

        for grouping in groupings:
            yield grouping

    def is_start(self):
        return self.token1 is None and self.token2 is None

    def is_end(self):
        return self.token3 is None

    def get_incoming_groups(self):
        return Grouping.objects.filter(token2=self.token1, token3=self.token2)

    def get_outgoing_groups(self):
        return Grouping.objects.filter(token1=self.token2, token2=self.token3)

    def get_complete_incoming_chains(self, cutoff=15):
        if cutoff < 1:
            return
        visited = [self]
        stack = [iter(self.get_incoming_groups())]
        while stack:
            children = stack[-1]
            child = next(children, None)
            if child is None:
                stack.pop()
                visited.pop(0)
            elif len(visited) < cutoff:
                if child.is_start():
                    yield [child] + visited[:-1]
                elif child not in visited:
                    visited.insert(0, child)
                    stack.append(iter(child.get_incoming_groups()))
            else:
                if child.is_start():
                    yield [child] + visited[:-1]
                for c in children:
                    if c.is_start():
                        yield [c] + visited[:-1]
                stack.pop()
                visited.pop(0)

    def get_complete_outgoing_chains(self, cutoff=15):
        if cutoff < 1:
            return
        visited = [self]
        stack = [iter(self.get_outgoing_groups())]
        while stack:
            children = stack[-1]
            child = next(children, None)
            if child is None:
                stack.pop()
                visited.pop(0)
            elif len(visited) < cutoff:
                if child.is_end():
                    yield visited[1:]
                elif child not in visited:
                    visited.append(child)
                    stack.append(iter(child.get_outgoing_groups()))
            else:
                if child.is_end():
                    yield visited[1:]
                for c in children:
                    if c.is_end():
                        yield visited[1:]
                stack.pop()
                visited.pop(0)
