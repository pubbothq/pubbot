#e Copyright 2014 the original author or authors
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
import sys
import random
import collections
import itertools

try:
    import cPickle as pickle
except ImportError:
    import pickle

import networkx as nx

from django.utils.functional import LazyObject

from .stemmer import stemmer


with open(os.path.join(os.path.dirname(__file__), "stopwords.txt")) as fp:
    STOP_WORDS = set(fp.read().split("\n"))


class Graph(nx.DiGraph):

    START = "START"
    END = "END"

    def __init__(self):
        super(Graph, self).__init__()

        self.stems = collections.defaultdict(list)
        self.tokens = collections.defaultdict(list)

        if self.START not in self:
            self.add_node(self.START)
        if self.END not in self:
            self.add_node(self.END)

    def iter_chain_forward(self, source, cutoff=None):
        return nx.all_simple_paths(self, source, self.END, cutoff=cutoff)

    def iter_chain_backward(self, source, cutoff=15):
        if cutoff < 1:
            return
        visited = [source]
        stack = [iter(self.pred[source].keys())]
        while stack:
            children = stack[-1]
            child = next(children, None)
            if child is None:
                stack.pop()
                visited.pop(0)
            elif len(visited) < cutoff:
                if child == self.START:
                    yield [self.START] + visited
                elif child not in visited:
                    visited.insert(0, child)
                    stack.append(iter(self.pred[child].keys()))

            else: #len(visited) == cutoff:
                if child == self.START or self.START in children:
                    yield [self.START] + visited
                stack.pop()
                visited.pop(0)

    def iter_random_chains(self, tokens):
        """
        Given a list of tokens like ["dog", "cat", "freddy"], yield random groups to generate chains from::

            >>> gen = iter_random_chains(["dog", "cat", "freddy"])
            >>> gen.next()
            ... ("have", "a", "cat")
            >>> gen.next()
            ... ("dog", "has", "fur")
            >>> gen.next()
            ... ("freddy", "likes", "herbs")
        """

        # Make a copy of tokens so we don't impact calling code
        tokens = set(tokens)

        # Conflate things. Input might be about "graphing" but by stemming
        # reply can be about "graphs"
        for stem in stemmer.stem_many(tokens):
            tokens.update(self.stems[stem])

        # Filter out stop words
        # FIXME: We can be interesting here and "learn" stop words perhaps?
        tokens = list(t for t in tokens if t.lower() not in STOP_WORDS)

        chains = []
        for token in tokens:
            chains.extend(self.tokens[token])

        random.shuffle(chains)

        for chain in itertools.cycle(chains):
            yield chain

    def save(self):
        path = os.path.join(sys.prefix, "var")
        if not os.path.exists(path):
            os.path.makedirs(path)
        with open(os.path.join(path, "chat.pickle"), "wb") as fp:
            pickle.dump(self, fp)

    @classmethod
    def load(cls):
        path = os.path.join(sys.prefix, "var", "chat.pickle")
        if os.path.exists(path):
            with open(path, "rb") as fp:
                return pickle.load(fp)
        return cls()


class LazyGraph(LazyObject):

    def _setup(self):
        self._wrapped = Graph.load()


graph = LazyGraph()
