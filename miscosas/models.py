"""
Models for app MisCosas
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    @property
    def upvote_count(self):
        ''' Upvote count property for templates '''
        return self.upvotes.count()

    @property
    def downvote_count(self):
        ''' Downvote count property for templates '''
        return self.downvotes.count()


class Comment(models.Model):
    title = models.CharField(max_length=64)
    content = models.CharField(max_length=256)
    date = models.DateTimeField(auto_now=True)
    item = models.ForeignKey(Item, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE, related_name='comments')

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    picture = models.URLField(default='https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_640.png')
    feeds = models.ManyToManyField(Feed, related_name='feeds')

    def __str__(self):
        return str(self.user)

    @property
    def vote_count(self):
        return self.user.upvotes.count() + self.user.downvotes.count()

    @property
    def feed_count(self):
        return self.feeds.count()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
