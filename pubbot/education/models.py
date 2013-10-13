import re

from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError


class Education(models.Model):

    trigger = models.CharField(max_length=1024)
    response = models.CharField(max_length=1024)
    probability = models.FloatField(
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(100),]
        )
    address_speaker = models.BooleanField()
    regex = models.BooleanField()

    def clean(self):
        if self.regex:
            try:
                re.compile(self.trigger)
            except:
                raise ValidationError('Trigger must be a regex if regex checked')

