# Copyright 2014 John Carr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from django import dispatch
from django.dispatch import receiver


__all__ = ["Signal", "receiver"]

logger = logging.getLogger(__name__)


class Signal(dispatch.Signal):

    def send(self, sender=None, **kwargs):
        logger.debug("%r: send called with kwargs = %r" % (self.__class__, kwargs))
        for handler, response in self.send_robust(sender, **kwargs):
            if not response:
                logger.debug("%r: ignored signal" % receiver)
                continue

            if isinstance(response, Exception):
                logger.error(
                    "%r: raised exception" % receiver, exc_info=(
                        response.__class__,
                        response,
                        response.__traceback__,
                    ),
                )
                continue

            yield (handler, response)
