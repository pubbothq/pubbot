from django.db import models


class Device(models.Model):

    fullname = models.CharField(max_length=1024)
    host = models.CharField(max_length=1024)
    port = models.PositiveIntegerField(max_length=1024)
    txt = models.CharField(max_length=1024)
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)

