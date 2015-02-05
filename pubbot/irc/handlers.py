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

"""
class FeedHandler(object):

    commands = ['PRIVMSG']

    def __init__(self, botname, channels, regex, signal):
        self.botname = botname
        self.channels = channels
        self.regex = re.compile(regex)
        self.signal = import_string(signal)

    def __call__(self, client, msg):
        if self.botname != msg.prefix.split("!")[0]:
            return

        channel, content = msg.params[0], " ".join(msg.params[1:])
        if channel not in self.channels:
            return

        results = self.regex.search(content)
        if not results:
            return

        self.signal.send(None, **results.groupdict())
"""
