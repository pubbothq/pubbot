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

from __future__ import absolute_import

from celery import group, chord

from pubbot.main.celery import app
from pubbot.main.match import match


def get_tasks_with_subscription(subscription):
    """
    Find all celery tasks that subscribe to a given channel
    """
    for task in app.tasks.values():
        # FIXME: The intention is to create a differet default task that
        # precompiles channels to a regex ahead of time
        if match(getattr(task, 'subscribe', []), subscription):
            yield task


def get_broadcast_group_for_message(**kwargs):
    return group(t.s(kwargs) for t in get_tasks_with_subscription(kwargs['kind']))


def broadcast(**kwargs):
    """
    Invoke all tasks that subscribe to channels matching the channel on msg
    """
    return get_broadcast_group_for_message(**kwargs).apply_async()

