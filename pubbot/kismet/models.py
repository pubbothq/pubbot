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

from pubbot.main.models import UserProfile


class Network(models.Model):

    bssid = models.CharField(max_length=17)
    name = models.CharField(max_length=64)
    enabled = models.BooleanField(default=True)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.bssid)

    class Meta:
        ordering = ['name']


class Device(models.Model):

    mac = models.CharField(max_length=17)
    user = models.ForeignKey(UserProfile, related_name="devices", blank=True, null=True)
    name = models.CharField(max_length=64)
    opt_out = models.BooleanField()


class Times(models.Model):

    device = models.ForeignKey(Device, related_name="times")
    date = models.DateField()
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField(blank=True, null=True)

