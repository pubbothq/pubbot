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
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string


class DefaultTokenizer(object):

    def split(self, text):
        text = text.strip()

        if not text:
            raise StopIteration

        for token in text.split(" "):
            token = token.strip()
            if token:
                yield token


class ConfiguredTokenizer(LazyObject):

    def _setup(self):
        self._wrapped = import_string(getattr(settings, "CHAT_TOKENIZER", ".".join((__name__, "DefaultTokenizer"))))()


tokenizer = ConfiguredTokenizer()
