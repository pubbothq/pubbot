# Copyright 2008-2013 the original author or authors
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

import unittest
from pubbot.main.match import match


# Message matching happens like in RabbitMQ:
#
#   * (star) can substitute for exactly one word.
# (hash) can substitute for zero or more words.

class TestMatch(unittest.TestCase):

    def assert_match(self, routing_key, message_type):
        self.assertEqual(match([routing_key], message_type), True)

    def assert_no_match(self, routing_key, message_type):
        self.assertEqual(match([routing_key], message_type), False)

    def test_direct_match(self):
        self.assert_match('foo', 'foo')

        self.assert_no_match('foo', 'bar')
        self.assert_no_match('foo', 'foo.bar')
        self.assert_no_match('foo', 'bar.foo')
        self.assert_no_match('foo', 'foo.foo')

    def test_hash(self):
        self.assert_match('#', 'foo')

    def test_hash_then_word(self):
        self.assert_match('#.foo', 'foo.foo')

        self.assert_no_match('#.foo', 'foo.barbar')
        self.assert_no_match('#.foo', 'foo.baz')

    def test_hash_then_star(self):
        self.assert_match('#.*', 'foo.bar')
        self.assert_match('#.*', 'foo.bar.baz')
        self.assert_match('#.*', 'foo.bar.baz.qux')
        self.assert_match('#.*', 'foo.bar.baz.qux.quux')
        self.assert_match('#.*', 'foo.bar.baz.qux.quux.corge')
        self.assert_match('#.*', 'foo.bar.baz.qux.quux.corge.grault')
        self.assert_match('#.*', 'foo.bar.baz.qux.quux.corge.garply')
        self.assert_match('#.*', 'foo.bar.baz.qux.quux.corge.garply.waldo')
        self.assert_match(
            '#.*', 'foo.bar.baz.qux.quux.corge.garply.waldo.fred')
        self.assert_match(
            '#.*', 'foo.bar.baz.qux.quux.corge.garply.waldo.fred.plugh')

        self.assert_no_match('#.*', 'foo')
