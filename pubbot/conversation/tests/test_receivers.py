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

import unittest
import mock

from pubbot.conversation import receivers


class TestTwitterLink(unittest.TestCase):

    def test_twitter_link(self):
        r1 = mock.Mock()
        r1.text = '<p class="tweet-text">.@elonmusk Just turned on my ice machine. I wonder if I own a bucket..</p>'
        r1.status_code = 200

        with mock.patch("requests.get") as get:
            get.side_effect = [r1]
            result = receivers.twitter_link(None, content="https://twitter.com/notch/status/500690106991513603")
            self.assertEqual(result['content'], '[ notch: .@elonmusk Just turned on my ice machine. I wonder if I own a bucket.. ]')


class TestPullRequest(unittest.TestCase):

    def test_pull_request(self):
        r1 = mock.Mock()
        r1.json.return_value = {"title": "Added login failure events to security logger", "user": {"login": "boylea"}}

        with mock.patch("requests.get") as get:
            get.side_effect = [r1]
            result = receivers.pull_request(None, content='https://github.com/django/django/pull/2013')
            self.assertEqual(result['content'], '[ boylea: Added login failure events to security logger ]')


class TestFight(unittest.TestCase):

    def test_fight(self):
        r1 = mock.Mock()
        r1.text = '<div id="resultStats">About 1000 results<nobr>(0.27 seconds)</nobr></div>'
        r2 = mock.Mock()
        r2.text = '<div id="resultStats">About 100 results<nobr>(0.27 seconds)</nobr></div>'

        with mock.patch("requests.get") as get:
            get.side_effect = [r1, r2]
            result = receivers.fight(None, content="fight: dog vs cat")
            self.assertEqual(result['content'], 'dog (1000) vs cat (100) -- dog wins!')
