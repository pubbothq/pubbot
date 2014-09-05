import os
import itertools

from pubbot.conversation import say
from pubbot.dispatch import receiver
from pubbot.vcs.signals import commit
from .signals import push


@receiver(push)
def push_to_commit(sender, payload, **kwargs):
    for c in payload.payload.get('commits', []):
        if not c['distinct']:
            continue

        commit.send(
            revision=c['sha'],
            message=c['message'],
            committer=c['author']['name'],
        )


@receiver(push)
def push_to_chat(sender, payload, **kwargs):
    fmt = '\x0303%(author)s \x0302%(repname)s \x0310r%(rev)s\x0314%(prefix)s%(changes)s\x0f: %(msg)s'

    repname = '/'.join(payload.repo)
    payload = payload.payload

    for commit in payload.get('comments', [])[:4]:
        if not commit["distinct"]:
            continue

        author = commit['author']['name']
        rev = commit['sha'][:6]
        msg = commit['message']

        trailer = ' ...'
        ircmsg = fmt % locals()
        ircmsg = ircmsg[:240 - len(trailer)] + trailer

        say(
            content=ircmsg,
            tags=['github:'+repname],
        )
