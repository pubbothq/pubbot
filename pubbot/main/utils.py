from __future__ import absolute_import

from celery import group, chord

from pubbot.main.celery import app
from pubbot.main.match import Subscriptions


def get_tasks_with_subscription(subscription):
    """
    Find all celery tasks that subscribe to a given channel
    """
    for task in app.tasks.values():
        # FIXME: The intention is to create a differet default task that
        # precompiles channels to a Subscriptions object for us
        if Subscriptions(getattr(task, 'subscribe', [])).match(subscription):
            yield task


def get_broadcast_group_for_message(**kwargs):
    return group(t.s(kwargs) for t in get_tasks_with_subscription(kwargs['kind']))


def broadcast(**kwargs):
    """
    Invoke all tasks that subscribe to channels matching the channel on msg
    """
    return get_broadcast_group_for_message(**kwargs).apply_async()

