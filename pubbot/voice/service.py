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

from __future__ import absolute_import

import gevent

from pubbot import service
from .say import voice
from .listen import speech_to_text


class Service(service.TaskService):

    def say(self, phrase):
        voice.say(phrase)

    def play(self, path):
        voice.say(path)

    def process(self, path):
        return speech_to_text.process(path)

    def tick(self):
        with self.device.stream() as stream:
            passive_listen = stream.passive_listen()
            if not passive_listen:
                return

            # Transcribe and check for 'pubbot'
            for match in self.process(passive_listen):
                if "pubbot" in match:
                    break
            else:
                return

            self.play("hi.wav")

            active_listen = stream.active_listen()
            if not active_listen:
                return

            self.play("lo.wav")

            message.send(
                content=self.process(active_listen),
                user="HUMAN",
                channel=self,
                direct=True,
            )

    def run(self):
        self.device = Device()
        with self.device:
            while True:
                self.tick()
