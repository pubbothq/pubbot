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

from .models import Scene
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
        def _inner(*args, **kwargs):
            result = regex.search(kwargs['content'])
            if result:
                return func(*args, **result.groupdict())
        return _inner

    return _decorator


def say(msg):
    if 'content' not in msg:
        # FIXME: Some sort of logging would be good
        return

    active_scenes = Scene.objects.get_query_set()

    if 'scene_id' in msg:
        scenes = active_scenes.filter(pk=msg['scene_id'])
    elif 'tags' in msg:
        scenes = active_scenes.filter(follows_tags__name__in=msg['tags'])
        if not scenes.exists():
            scenes = active_scenes.filter(follows_tags__name='default')
    else:
        scenes = active_scenes.filter(follows_tags__name='default')

    if msg.get("action", False):
        func_name = "action"
    elif msg.get("notice", False):
        func_name = "notice"
    else:
        func_name = "say"

    for scene in scenes.exclude(bans_tags__name__in=msg.get('tags', [])).distinct():
        # getattr(scene, func_name)(msg['content'])
        logger.debug("Saying %r in %r via %r" % (msg, scene, func_name))
