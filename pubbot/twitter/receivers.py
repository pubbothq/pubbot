
from django.dispatch import receiver

from pubbot.conversation import say
from pubbot.twitter.signals import tweet


@receiver(tweet)
def broadcast_tweet(self, text, user, **kwargs):
    say(
        content="\n".join([
            "https://twitter.com/%s/status/%s" % (user['screen_name'], id),
            "[ %s: %s ]" % (user['screen_name'], text.replace("\n", ""))
        ]),
        tags=['twitter_stream'],
    )
