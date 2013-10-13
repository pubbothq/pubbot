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


class WordManager(models.Manager):

    def get_next_word(self):
        return self.get_queryset().extra(select={'weight': 'random() * count'}).extra(order_by='weight')[0].right

    def get_previous_word(self):
        return self.get_queryset().extra(select={'weight': 'random() * count'}).extra(order_by='weight')[0].left


class Word(models.Model):
    objects = WordManager()

    word = models.CharField(max_length=255, unique=True)
    count = models.IntegerField(default=1)

    def __unicode__(self):
        return self.word


class Chain(models.Model):
    left = models.ForeignKey(Word, related_name='right')
    right = models.ForeignKey(Word, related_name='left')
    count = models.IntegerField(default=1)

    def __unicode__(self):
        return "%s -> %s" % (self.left, self.right)

    class Meta:
        unique_together = ('left', 'right')

