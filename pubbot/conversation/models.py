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

from django.db import models
from polymorphic import PolymorphicModel

from pubbot.main.models import UserProfile


class RelevanceTag(models.Model):
    name = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name


class Scene(PolymorphicModel):

    name = models.CharField(max_length=128)
    follows_tags = models.ManyToManyField(
        RelevanceTag, related_name='foolow_tags+')
    bans_tags = models.ManyToManyField(RelevanceTag, related_name='bans_tags+')

    def __unicode__(self):
        return self.name


class Participant(PolymorphicModel):

    name = models.CharField(max_length=128)
    profile = models.ForeignKey(
        UserProfile, related_name='chat_accounts', blank=True, null=True)
    scenes = models.ManyToManyField(Scene, related_name='participants')

    @property
    def is_me(self):
        return False

    def __unicode__(self):
        return self.name
