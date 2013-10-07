from django.db import models


class Device(models.Model):

    mac = models.CharField(max_length=7)
    opt_out = models.BooleanField()


class Times(models.Model):

    device = models.ForeignKey(Device, related_name="times")
    date = models.DateField()
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField(blank=True, null=True)


