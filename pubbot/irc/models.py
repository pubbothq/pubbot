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
from pubbot.conversation.models import Scene, Participant


class Network(models.Model):

    nick = models.CharField(max_length=128)
    server = models.CharField(max_length=128)
    port = models.CharField(max_length=5)
    ssl = models.BooleanField()
    nickserv_password = models.CharField(
        max_length=1024, blank=True, null=True)
    nickserv_certfp = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.server


class Room(Scene):
    server = models.ForeignKey(Network, related_name="rooms")


class User(Participant):
    network = models.ForeignKey(Network, related_name='users')
