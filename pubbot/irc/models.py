from django.db import models


class Network(models.Model):

    server = models.CharField(max_length=128)
    port = models.CharField(max_length=5)


class Room(models.Model):

    server = models.ForeignKey(Network, related_name="rooms")
    room = models.CharField(max_length=128)

