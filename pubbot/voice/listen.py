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

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string

try:
    import pocketsphinx
except ImportError:
    pocketsphinx = None


class Listener(object):

    @classmethod
    def available(cls):
        raise NotImplementedError(self.available)

    def process(self, stream):
        """ Given a stream of audio, returns a listen of possible interpretations """
        raise NotImplementedError(self.process)


class PocksetSphinxListener(Listener):

    def __init__(self):
        self.decoder = pocketsphinx.Decoder(
            hmm=hmm_dir,
            lm=lmd,
            dict=dictd,
            logfn,
        )

    @classmethod
    def available(cls):
        return pocketsphinx != None

    def process(self, stream):
        # FIXME: Investigate decode_raw
        self.decoder.start_utt()
        self.decoder.process_raw(stream.read(), False, True)
        self.decoder.end_utt()
        return [self.decoder.get_hyp()[0]]


class ConfiguredListener(LazyObject):

    def _setup(self):
        if hasattr(settings, "VOICE_INPUT_BACKEND"):
            self._wrapped = import_string(settings.VOICE_INPUT_BACKEND)()
            return

        for backend in [PocketSphinxListener]:
            if backend.available:
                self._wrapped = backend()
                return

        raise ImproperlyConfigured("No valid engine for speech to text available")


speech_to_text = ConfiguredListener()
