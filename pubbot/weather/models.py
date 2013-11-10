from django.db import models


class Point(models.Model):
    api = models.CharField(max_length=64)
    lat = models.FloatField()
    lon = models.FloatField()
    tag = models.CharField(max_length=64)
