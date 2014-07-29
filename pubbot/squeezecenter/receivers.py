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

from django.utils import timezone
from django.dispatch import receiver

from pubbot.conversation import chat_receiver, say
from . import signals


@receiver(signals.song_started)
def current_song_notification(sender, **kwargs):
    say({
        'content': "%(title)s - %(artist)s (%(album)s)" % kwargs,
        'tags': ['current_song_notification'],
        'notice': True,
    })


@chat_receiver(r'^skip(\s(?P<number>\d+))?$')
def requested_skip(sender, number, **kwargs):
    from .models import Skip
    from pubbot.conversation.models import Participant

    try:
        profile = Participant.objects.get(id=kwargs['participant_id'])
    except KeyError as xxx_todo_changeme:
        Participant.DoesNotExist = xxx_todo_changeme
        profile = None

    if not profile or not profile.profile:
        return {
            "content": "I don't know who you are",
        }

    try:
        current_skip = Skip.objects.get(vote_ended__isnull=True)
        if number:
            return {
                "content": "Skip already in progress; can't start another",
            }
    except Skip.DoesNotExist:
        current_skip = Skip(number=number or 1)
        current_skip.save()
        skip_timeout.apply_async(
            (current_skip.id, ), countdown=Skip.VOTE_DURATION.seconds)
    current_skip.skip(profile.profile)

    if current_skip.needed > 0:
        return {
            "content": "Voted to skip. %d more votes required" %
            current_skip.needed,
        }


@chat_receiver(r'^noskip$')
def requested_noskip(sender, **kwargs):
    from .models import Skip
    from pubbot.conversation.models import Participant

    try:
        profile = Participant.objects.get(id=kwargs['participant_id'])
    except KeyError as xxx_todo_changeme1:
        Participant.DoesNotExist = xxx_todo_changeme1
        profile = None

    if not profile or not profile.profile:
        return {
            "content": "I don't know who you are",
        }

    try:
        current_skip = Skip.objects.get(vote_ended__isnull=True)
    except Skip.DoesNotExist:
        return {
            "content": "There isn't a vote in progress.."
        }

    current_skip.noskip(profile.profile)

    return {
        "content": "Voted to not skip. %d more votes required" %
        current_skip.needed,
    }


def skip_timeout(skip_id):
    from .models import Skip

    try:
        s = Skip.objects.get(id=skip_id)
    except Skip.DoesNotExist:
        return

    if s.vote_ended:
        return

    s.vote_ended = timezone.now()
    s.save()

    say({
        'content': 'Vote timed out after %d seconds' %
        Skip.VOTE_DURATION.seconds,
    })


def skip(num_tracks):
    if num_tracks == 0:
        print "Asked to skip 0 tracks :("
        return
    sign = "+" if num_tracks > 0 else "-"
    print "Calling command()"
    command("playlist index %s%d" % (sign, num_tracks))


def _escape(text):
    #FIXME: Is full on url style escaping required perhaps?
    return text.replace(' ', '+')


@chat_receiver(r'^canhas (?P<canhas>.*)')
def canhas(sender, canhas, **kwargs):
    command("playlist loadtracks contributor.namesearch=%s" % _escape(canhas))
    return {"had_side_effect": True, }


@chat_receiver(r'^canhaslater (?P<canhaslater>.*)')
def canhaslater(sender, canhaslater, **kwargs):
    command("playlist addtracks contributor.namesearch=%s" % _escape(canhaslater))
    return {"had_side_effect": True, }


@chat_receiver(r'^doeswant (?P<doeswant>.*)')
def doeswant(sender, doeswant, **kwargs):
    command("playlist loadtracks track.titlesearch=%s" % _escape(doeswant))
    return {"had_side_effect": True, }


@chat_receiver(r'^doeswantlater (?P<doeswantlater>.*)')
def doeswantlater(sender, doeswantlater, **kwargs):
    command("playlist: addtracks track.titlesearch=%s" % _escape(doeswantlater))
    return {"had_side_effect": True, }


@chat_receiver(r'^random$')
def random(sender, **kwargs):
    words = filter(lambda x: len(x) <= 4, open("/usr/share/dict/words").read().split("\n"))
    doeswant(msg, random.choice(words))
    return {"had_side_effect": True, }


def command(command):
    print "command: %s" % command
    # app.squeezecenter.send(command)
