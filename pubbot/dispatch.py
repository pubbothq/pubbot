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
from django.dispatch.dispatcher import NO_RECEIVERS


__all__ = ["Signal", "receiver"]

logger = logging.getLogger(__name__)


class Signal(dispatch.Signal):

    def send(self, sender=None, **kwargs):
        logger.debug("%r: send called with kwargs = %r" % (self.__class__, kwargs))

        # We can't use send_robust directly as it is unable to give us
        # Exception.__traceback__ until Django 1.8
        responses = []
        if not self.receivers or self.sender_receivers_cache.get(sender) is NO_RECEIVERS:
            return responses

        for handler in self._live_receivers(sender):
            try:
                response = handler(signal=self, sender=sender, **kwargs)
            except Exception:
                logger.exception("Receiver failed")
                continue

            if response:
                responses.append((handler, response))

        return responses
