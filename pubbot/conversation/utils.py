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

import re
import logging

from django.dispatch import receiver

from .signals import message


logger = logging.getLogger(__name__)


def chat_receiver(regex, **kwargs):
    """
    A decorator that hooks up a function to the pubbot.conversation.signals.message signal
    """
    if isinstance(regex, basestring):
        regex = re.compile(regex)

    def _decorator(func):
        @receiver(message)
        def _inner(sender, **kwargs):
            result = regex.search(kwargs['content'])
            if result:
                kwargs.update(result.groupdict())
                return func(sender, **kwargs)
        return _inner

    return _decorator


def say(content, **kwargs):
    return
    from pubbot.irc.models import Room
    rooms = [kwargs.get('room', None)]
    if not rooms:
        if 'tags' in kwargs:
            rooms = Room.objects.filter(subscribes__name__in=kwargs['tags'])
            if not rooms.exists():
                rooms = Room.objects.filter(subscribes__name__in=['default'])
            rooms = rooms.exclude(blocks__name__in=kwargs['tags'])
        else:
            rooms = Room.objects.filter(subscribes__name__in=['default'])

    if kwargs.get("action", False):
        func_name = "action"
    elif kwargs.get("notice", False):
        func_name = "notice"
    else:
        func_name = "say"

    for room in rooms.distinct():
        # getattr(scene, func_name)(msg['content'])
        logger.debug("Saying %r in %r via %r" % (content, room, func_name))
