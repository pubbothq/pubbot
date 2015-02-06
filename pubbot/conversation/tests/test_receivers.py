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

import json
import os
import unittest
from unittest import mock

from pubbot.conversation import receivers


class TestHello(unittest.TestCase):

    def test_hello(self):
        channel = mock.Mock()
        receivers.hello(None, "Freddy", channel, False)
        self.assertTrue("Freddy" in channel.msg.call_args[0][0])

    def test_no_hello(self):
        channel = mock.Mock()
        receivers.hello(None, "Freddy", channel, True)
        self.assertEqual(channel.msg.called, False)


class TestTwitterLink(unittest.TestCase):

    def test_404(self):
        with mock.patch("requests.get") as get:
            get.return_value.status_code = 404
            r = receivers.twitter_link(None, content="https://twitter.com/notch/status/500690106991513603")
            self.assertEqual(r, None)

    def test_twitter_link(self):
        r1 = mock.Mock()
        r1.text = '<div class="permalink-inner permalink-tweet-container"><div><p class="tweet-text">.@elonmusk Just turned on my ice machine. I wonder if I own a bucket..</p></div></div>'
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


class TestAppDotNet(unittest.TestCase):

    def test_simple_post(self):
        r1 = mock.Mock()
        r1.json.return_value = {"data": {"text": "A test post", "user": {"username": "Jc2k"}}}

        with mock.patch("requests.get") as get:
            get.side_effect = [r1]
            result = receivers.on_appdotnet_link(None, content='https://alpha.app.net/Jc2k/post/12345')
            self.assertEqual(result['content'], '[ Jc2k: A test post ]')


class TestImageSearch(unittest.TestCase):

    def test_simple_image_search(self):
        r1 = mock.Mock()
        r1.json.return_value = {"responseData": {"results": [{"url": "http://localhost/funny.gif"}]}}

        with mock.patch("requests.get") as get:
            get.side_effect = [r1]
            result = receivers.image_search(None, content='img me funny')
            self.assertEqual(result['content'], 'http://localhost/funny.gif')

    def test_no_results(self):
        r1 = mock.Mock()
        r1.json.return_value = {"responseData": {"results": []}}

        with mock.patch("requests.get") as get:
            get.side_effect = [r1]
            result = receivers.image_search(None, content='img me funny')
            self.assertEqual(result['content'], "There are no images matching 'funny'")


class TestDoge(unittest.TestCase):

    def test_so_silly(self):
        mock_content = json.loads(open(os.path.join(
            os.path.dirname(__file__),
            "test_receivers_doge_1.json"
        )).read())

        with mock.patch("requests.get") as get:
            get.return_value.json.return_value = mock_content
            with mock.patch("random.choice") as choice:
                choice.side_effect = lambda x: x[0]
                r = receivers.doge(None, content="so silly")
                self.assertEqual(r['content'], 'much "playful"')


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


class TestBlame(unittest.TestCase):

    def test_no_nicks(self):
        channel = mock.Mock()
        channel.users = []
        r = receivers.blame(None, content="blame", channel=channel)
        self.assertEqual(r['content'], "It's all my fault!")

    def test_1_nick(self):
        channel = mock.Mock()
        channel.users = ['fred']
        r = receivers.blame(None, content="blame", channel=channel)
        self.assertEqual(r['content'], "It's all fred's fault!")


class TestChristmas(unittest.TestCase):

    def setUp(self):
        self.today = (2010, 1, 1)
        import datetime

        class _datetime(datetime.datetime):
            @classmethod
            def today(cls):
                return cls(*self.today)
        self.patcher = mock.patch("pubbot.conversation.receivers.datetime")
        self.patcher.start().datetime = _datetime

        from django.core.cache import caches
        caches['default'].clear()

    def tearDown(self):
        self.patcher.stop()

    def test_its_christmas(self):
        self.today = (2014, 12, 25)
        result = receivers.christmas(None, content="It's nearly christmas")
        self.assertEqual(result['content'], "It's christmas \o/")

    def test_its_nearly_christmas(self):
        self.today = (2014, 12, 24)
        result = receivers.christmas(None, content="It's nearly christmas")
        self.assertEqual(result['content'], "only 1 days 'til Christmas!")

    def test_im_fedup_of_christmas(self):
        self.today = (2014, 12, 26)
        result = receivers.christmas(None, content="It's nearly christmas")
        self.assertEqual(result, None)

    def test_not_the_season(self):
        self.today = (2014, 1, 25)
        result = receivers.christmas(None, content="It's nearly christmas")
        self.assertEqual(result, None)
