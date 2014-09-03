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

import logging
import time
import random

from django.core.cache import caches

import gevent

from pubbot.dispatch import receiver
from pubbot.conversation import chat_receiver, say
from . import signals


logger = logging.getLogger(__name__)


@receiver(signals.song_started)
def current_song_notification(sender, **kwargs):
    say(
        content="%(title)s - %(artist)s (%(album)s)" % kwargs,
        tags=['current_song_notification'],
        notice=True,
    )


def get_current_skip():
    return caches['default'].get("squeezecenter_skip", None)


def set_current_skip(skip):
    skip['last_update'] = time.time()
    return caches['default'].set("squeezecenter_skip", skip)


def timeout_current_skip():
    skip = get_current_skip()
    while skip:
        staleness = 30 - (time.time() - skip['last_update'])
        logger.debug("Checking if the skip is timed out - staleness is %r" % staleness)
        if staleness <= 0:
            logger.debug("The skip is timed out")
            say(
                content='Vote timed out after 30 seconds',
            )
            # FIXME
            return
        logger.debug("%d seconds to timeout" % staleness)
        gevent.sleep(staleness)
        skip = get_current_skip()


@chat_receiver(r'^skip(\s(?P<number>\d+))?$')
def requested_skip(sender, number, user, **kwargs):
    current_skip = get_current_skip()
    created = False

    if number and current_skip:
            return {
                "content": "Vote already in progress; can't start another",
            }

    if not current_skip:
        if not number:
            number = 1

        number = int(number)

        if number <= 0:
            return {
                "content": "Don't be daft",
            }

        current_skip = {
            "number": number,
            "started_by": user,
            "skip": set(),
            "noskip": set(),
        }
        created = True

    return update_skip(current_skip, user, "skip", created)


@chat_receiver(r'^noskip$')
def requested_noskip(sender, user, **kwargs):
    current_skip = get_current_skip()
    if not current_skip:
        return {
            "content": "There isn't a vote in progres..",
        }
    return update_skip(current_skip, user, "noskip", False)


def update_skip(current_skip, user, skip_type, created):
    skip_count = len(current_skip["skip"]) - len(current_skip["noskip"])
    votes_needed = 3 - skip_count

    # Don't let them both skip and noskip
    opposite_skip_type = "skip" if skip_type == "noskip" else "noskip"
    try:
        current_skip[opposite_skip_type].remove(user)
    except KeyError:
        pass

    # We use a set so they can only be in the list once..
    current_skip[skip_type].add(user)

    set_current_skip(current_skip)

    if not created:
        gevent.spawn(timeout_current_skip)

    if votes_needed > 0:
        logger.debug("%d more tracks needed to skip" % votes_needed)

        return {
            "content": "%s voted to %s! %d more votes required" % (user, skip_type, votes_needed),
        }

    logger.debug("Skipping %d tracks" % current_skip["number"])

    command("playlist index %d" % current_skip["number"])

    return {
        "content": random.choice([
            "Good riddance.",
            "Yay.",
            "Skippy skip skip..",
            "Skippity skip skip..",
        ])
    }


def _escape(text):
    # FIXME: Is full on url style escaping required perhaps?
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
    command("playlist addtracks track.titlesearch=%s" % _escape(doeswantlater))
    return {"had_side_effect": True, }


@chat_receiver(r'^random$')
def random_song(sender, content, **kwargs):
    words = filter(lambda x: len(x) <= 4, open("/usr/share/dict/words").read().split("\n"))
    doeswant(sender, content="doeswant " + random.choice(words), **kwargs)
    return {"had_side_effect": True, }


def command(command):
    print "command: %s" % command
    # app.squeezecenter.send(command)
