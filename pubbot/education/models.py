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

import re

from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError


class Education(models.Model):

    trigger = models.CharField(max_length=1024)
    response = models.CharField(max_length=1024)
    probability = models.FloatField(
        validators=[validators.MinValueValidator(
            0), validators.MaxValueValidator(100), ]
    )
    address_speaker = models.BooleanField(default=False)
    regex = models.BooleanField(default=False)

    def clean(self):
        if self.regex:
            try:
                re.compile(self.trigger)
            except:
                raise ValidationError('Trigger must be a valid regex if regex checked')

    def __unicode__(self):
        return '%r -> %r' % (self.trigger, self.response)
