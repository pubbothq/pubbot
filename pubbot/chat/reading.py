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

from .tokenizer import tokenizer
from .graph import graph
from .stemmer import stemmer


def group_tokens(tokens):
    a = tokens.next()
    b = tokens.next()
    c = tokens.next()
    yield (a, b, c)

    while True:
        a = b
        b = c
        c = tokens.next()
        yield (a, b, c)


def process_token(token):
    if token not in graph:
        graph.add_node(token)

        stem = stemmer.stem(token)
        if stem:
            if stem not in graph:
                graph.add_node(stem)
            if token not in graph[stem]:
                graph.add_edge(stem, token)


def process_node(node):
    if node not in graph:
        graph.add_node(node)

        process_token(node[2])
        graph.add_edge(node[2], node)


def process_edge(src, dst):
    try:
        graph[src][dst]['weight'] += 1
    except KeyError:
        graph.add_edge(src, dst, weight=1)


def learn_tokens(tokens):
    groups = group_tokens(tokens)

    try:
        prev = None
        cur = groups.next()
    except StopIteration:
        # There aren't enough tokens to form a single group!
        return

    process_node(cur)
    process_edge("START", cur)

    while True:
        prev = cur

        try:
            cur = groups.next()
        except StopIteration:
            process_edge(prev, "END")
            break

        process_node(cur)
        process_edge(prev, cur)


def learn_string(text):
    try:
        tokens = tokenizer.split(text.encode("utf-8"))
    except UnicodeDecodeError:
        return
    learn_tokens(tokens)
