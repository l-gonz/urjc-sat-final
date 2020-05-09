"""
Models for app MisCosas
"""

from django.db import models
from django.contrib.auth.models import User


class Feed(models.Model):
    key = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    origin = models.CharField(max_length=32)

    def __str__(self):
        return self.origin + ': ' + self.title


class Item(models.Model):
    key = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    feed = models.ForeignKey(Feed, models.CASCADE)
    upvotes = models.ManyToManyField(User, related_name="upvotes")
    downvotes = models.ManyToManyField(User, related_name="downvotes")
    description = models.TextField(blank=True, default='')
    picture = models.URLField(blank=True, default='')

    def __str__(self):
        return str(self.feed) + ", " + self.title


class Comment(models.Model):
    title = models.CharField(max_length=64)
    content = models.CharField(max_length=256)
    date = models.DateTimeField(auto_now=True)
    item = models.ForeignKey(Item, models.CASCADE)
    user = models.ForeignKey(User, models.PROTECT)

    def __str__(self):
        return self.title


class UserData(models.Model):
    picture = models.URLField()
    django_user = models.OneToOneField(User, models.PROTECT)

    def __str__(self):
        return str(self.django_user)
