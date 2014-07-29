from datetime import date

from django.core.cache import cache
from django.dispatch import receiver

from pubbot.conversation import chat_receiver, say
from pubbot.vcs.signals import commit


@chat_receiver(r'\x0303(?P<committer>\w+) \x0302(?P<repository>[\w\d]+) \x0310r(?P<revision>\d+)(?P<message>.*)\x0314')
def ch1mp(sender, committer, repository, revision, path, message, **kwargs):
    commit.send_robust(
        committer=committer,
        repository=repository,
        revision=int(revision),
        message=message,
    )


@receiver(commit)
def svnwoot(sender, revision, **kwargs):
    if revision in (1337, 1000, 2000, 1, 100, 200, 13337, 666, 700, 777, 501):
        say(
            content="r%d - \o/",
            at=0,
        )


@receiver(commit)
def notlikely(sender, message, **kwargs):
    if 'final' in message.lower():
        say(
            content="Final? Not likely, %(name)s",
            at=0,
        )


@receiver(commit)
def multikill(sender, committer, **kwargs):
    if date.today().weekday() > 4:
        # No cheeky weekend killing sprees! ;-)
        return

    killer = cache.get("multikill_killer")
    if killer and killer != committer:
        say({
            'content': '%s ended the killing spree! poor %s' % (committer, killer),
            'tags': ['multikill'],
        })

        cache.set("multikill_killer", committer)
        cache.set("multikill_kills", 1)
        return

    kills = cache.get("multikill_kills", 0) + 1
    cache.set("multikill_kills", kills)

    if kills == 2:
        say({'content': "Double Kill", 'tags': ['multikill']})
    elif kills == 3:
        say({'content': "Multi Kill", 'tags': ['multikill']})
    elif kills == 4:
        say({'content': "Ultra Kill", 'tags': ['multikill']})
        # play_sound("ultrakill.wav")
    elif kills == 5:
        say({'content': "Megakill", 'tags': ['multikill']})
        # play_sound("megakill.wav")
    elif kills == 6:
        say({'content': "MONSTTTTTTTEEER KILLLLL", 'tags': ['multikill']})
        # play_sound("monsterkill.wav")

    # elif kills >= 10 and self.kills % 5 == 0:
    #     self.play_sound(
    #         random.choice([
    #             "dominating.wav",
    #             "killingspree.wav",
    #             "humiliation.wav",
    #             "unstoppable.wav",
    #             "rampage.wav"
    #         ])
    #     )
