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
    fmt = '\x0303%(author)s \x0302%(repname)s \x0310%(rev)s\x0314\x0f: %(msg)s'

    org, rep = payload.repo
    repname = '/'.join(payload.repo)
    payload = payload.payload

    for c in payload.get('commits', [])[:4]:
        if not c["distinct"]:
            continue

        author = c['author']['name']
        rev = c['sha'][:6]
        msg = c['message']

        trailer = ' ...'
        ircmsg = fmt % locals()
        ircmsg = ircmsg[:240 - len(trailer)] + trailer

        say(
            content=ircmsg,
            tags=['github:' + repname, 'github:' + org],
        )
