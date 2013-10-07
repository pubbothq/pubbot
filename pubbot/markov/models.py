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

