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

import datetime
from django.db import models

from pubbot.main.models import UserProfile
from pubbot.squeezecenter.tasks import skip


class Artist(models.Model):

    name = models.CharField(max_length=1024)


class Album(models.Model):

    name = models.CharField(max_length=1024)
    artist = models.ForeignKey(Artist, related_name="albums")


class Song(models.Model):

    name = models.CharField(max_length=1024)
    album = models.ForeignKey(Album, related_name="tracks")


class Skip(models.Model):

    VOTE_DURATION = datetime.timedelta(seconds=30)

    vote_started = models.DateTimeField(auto_now_add=True)
    vote_ended = models.DateTimeField(blank=True)
    number = models.IntegerField(default=0)
    songs = models.ManyToManyField(Song, related_name="skips")

    skip = models.ManyToManyField(UserProfile)
    noskip = models.ManyToManyField(UserProfile)

    @property
    def count(self):
        return self.skip.count() - self.noskip.count()

    @property
    def should_skip(self):
        return self.count >= 3

    def noskip(self, user):
        if self.vote_ended or datetime.datetime.now >= self.vote_started + VOTE_DURATION:
            return
        self.skip.remove(user)
        self.noskip.add(user)

    def skip(self, user):
        if self.vote_ended or datetime.datetime.now >= self.vote_started + VOTE_DURATION:
            return
        self.noskip.remove(user)
        self.skip.add(user)

        if self.should_skip:
            self.vote_ended = datetime.datetime.now()
            self.save()

            skip.delay(self.number)

