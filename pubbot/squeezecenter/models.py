from django.db import models


class Artist(models.Model):

    name = models.CharField(max_length=1024)


class Album(models.Model):

    name = models.CharField(max_length=1024)
    artist = models.ForeignKey(Artist, related_name="albums")


class Song(models.Model):

    name = models.CharField(max_length=1024)
    album = models.ForeignKey(Album, related_name="tracks")

