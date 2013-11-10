from django.db import models


class Link(models.Model):

    url = models.CharField(max_length=1024)
    hostname = models.CharField(max_length=1024)

    title = models.CharField(max_length=1024, blank=True, null=True)
    content_type = models.CharField(max_length=1024, blank=True, null=True)
    content_length = models.CharField(max_length=1024, blank=True, null=True)

    first_seen = models.DateTimeField(auto_now_add=True)
