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

import Stemmer

from django.conf import settings
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string


class DefaultStemmer(object):

    def __init__(self):
        self.stemmer = Stemmer.Stemmer(getattr(settings, "CHAT_STEMMER_LANGUAGE", "en"))

    def stem_many(self, tokens):
        for token in tokens:
            stem = self.stem(token)
            if stem:
                yield stem

    def stem(self, token):
        # FIXME: Detect URL's, smilies, nicks, phone numbers, prices, dates, etc
        stem = self.stemmer.stemWord(token.lower())
        return stem


class ConfiguredStemmer(LazyObject):

    def _setup(self):
        self._wrapped = import_string(getattr(settings, "CHAT_STEMMER", ".".join((__name__, "DefaultStemmer"))))()


stemmer = ConfiguredStemmer()
