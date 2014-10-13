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
import subprocess

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string


class Voice(object):

    def __init__(self, output):
        self.output = output

    def available(self):
        raise NotImplementedError(self.available)

    def say(self, sentence):
        raise NotImplementedError(self.say)


class ESpeakVoice(Voice):

    def available(self):
        return os.path.exists("/usr/bin/espeak")

    def say(self, phrase, pitch_adj=40, wpm=160):
        with tempfile.NamedTemporaryFile(suffix='.wav') as f:
            subprocess.check_call([
                'espeak',
                '-v', getattr(settings, "SPEECH_VOICE", "default+m3"),
                '-p', str(pitch_adj),
                '-s', str(wpm),
                '-w', f.name,
            ])
            self.output.play(f.name)


class OSXVoice(Voice):

    # NOTE: This voice does not support tweaking pitch_adj or wpm

    @classmethod
    def available(cls):
        return platform.system() == "Darwin" and os.path.exists("/usr/bin/say")

    def say(self, sentence, pitch_adj=None, wpm=None):
        cmd = ['say']
        if hasattr(settings, "SPEECH_VOICE"):
            cmd.extend(["-v", settings.SPEECH_VOICE])
        cmd.append(sentence)

        subprocess.check_call(cmd)


class ConfiguredVoice(LazyObject):

    def __init__(self):
        if hasattr(settings, "SPEECH_BACKEND"):
            self._wrapped = import_string(settings.SPEECH_BACKEND)()
            return

        for backend in [OSXVoice, ESpeakVoice]:
            if backend.available:
                self._wrapped = backend()
                return

        raise ImproperlyConfigured("No valid engine for text to speech available")


voice = ConfiguredVoice()
