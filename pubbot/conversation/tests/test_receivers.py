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


class TestPullRequest(unittest.TestCase):
    pass


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
