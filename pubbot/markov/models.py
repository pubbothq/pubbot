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


class Word(models.Model):

    word = models.CharField(max_length=510)
    count = models.IntegerField(default=0)

    def __unicode__(self):
        return self.word


class Chain(models.Model):

    left1 = models.ForeignKey(Word, related_name='left1')
    left2 = models.ForeignKey(Word, related_name='left2')
    right = models.ForeignKey(Word, related_name='right')
    count = models.IntegerField(default=0)

    def get_next_chain(self):
        return Chain.objects.\
            filter(left1=self.left2, left2=self.right).\
            extra(select={'weight': 'random() * count'}).\
            extra(order_by=['-weight'])[0]

    def get_previous_chain(self):
        return Chain.objects.\
            filter(right=self.left2, left2=self.left1).\
            extra(select={'-weight': 'random() * count'}).\
            extra(order_by=['weight'])[0]

    def __unicode__(self):
        return "%s -> %s -> %s" % (self.left1, self.left2, self.right)

    class Meta:
        unique_together = ('left1', 'left2', 'right')
