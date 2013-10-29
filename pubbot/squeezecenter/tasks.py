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

from pubbot.main.celery import app
from pubbot.conversation.tasks import parse_chat_text, mouth

@app.task(subscribe=['music.start'])
def current_song_notification(msg):
    mouth({
        'content': "%(title)s - %(artist)s (%(album)s)" % msg,
        'tags': ['current_song_notification'],
        'notice': True,
        })


@parse_chat_text(r'^skip(\s(?P<number>\d+))?$')
def requested_skip(msg, number):
    from .models import Skip

    try:
        profile = UserProfile.objects.get(id=msg['profile_id'])
    except KeyError, UserProfile.DoesNotExist:
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
        current_skip = Skip()
        current_skip.save()

    current_skip.skip(profile)

    return {
        "content": "Voted to skip. %d more votes required" % (3 - skip.count())
        }


@parse_chat_text(r'^noskip$')
def requested_skip(msg):
    from .models import Skip

    try:
        profile = UserProfile.objects.get(id=msg['profile_id'])
    except KeyError, UserProfile.DoesNotExist:
        return {
            "content": "I don't know who you are",
            }

    try:
        current_skip = Skip.objects.get(vote_ended__isnull=True)
    except Skip.DoesNotExist:
        return {
            "content": "There isn't a vote in progress.."
            }

    current_skip.noskip(profile)

    return {
        "content": "Voted to not skip. %d more votes required" % (3 - skip.count())
        }



@app.task(queue='squeeze')
def skip(num_tracks):
    if num_tracks == 0:
        return
    sign = "+" if num_tracks > 0 else "-"
    command.apply("playlist index %s%d" % (sign, num_tracks))


@app.task(queue='squeeze')
def command(command):
    app.squeezecenter.send(command)

