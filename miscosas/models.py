"""
Models for app MisCosas
"""

import os

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Feed(models.Model):
    key = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    origin = models.CharField(max_length=32)
    chosen = models.BooleanField(default=True)

    def __str__(self):
        return self.origin + ': ' + self.title


class Item(models.Model):
    key = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    feed = models.ForeignKey(Feed, models.CASCADE, related_name="items")
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
    item = models.ForeignKey(Item, models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, models.CASCADE, related_name='comments')

    def __str__(self):
        return self.title


class Profile(models.Model):
    DEFAULT_PICTURE = 'blank-profile-picture.png'

    LIGHTMODE = 'LM'
    DARKMODE = 'DM'
    THEMES = [
        (LIGHTMODE, 'Light mode'),
        (DARKMODE, 'Dark mode'),
    ]

    SMALL_FONT = 'sm'
    MEDIUM_FONT = 'md'
    LARGE_FONT = 'lg'
    FONT_SIZES = [
        (SMALL_FONT, 'Small'),
        (MEDIUM_FONT, 'Medium'),
        (LARGE_FONT, 'Large'),
    ]

    user = models.OneToOneField(User, models.CASCADE)
    _picture = models.ImageField(blank=True, null=True)
    theme = models.CharField(max_length=2, choices=THEMES, default=LIGHTMODE)
    font_size = models.CharField(max_length=2, choices=FONT_SIZES, default=MEDIUM_FONT)

    def __str__(self):
        return str(self.user)

    @property
    def picture(self):
        try:
            if os.path.isfile(self._picture.path):
                return self._picture
            Profile.objects.filter(pk=self.pk).update(_picture=None)
            return self.DEFAULT_PICTURE
        except ValueError:
            return self.DEFAULT_PICTURE

    @property
    def vote_count(self):
        return self.user.upvotes.count() + self.user.downvotes.count()

    @property
    def comment_count(self):
        return self.user.comments.count()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(models.signals.post_delete, sender=Profile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding Profile object is deleted.
    """
    if instance.picture and instance.picture != Profile.DEFAULT_PICTURE:
        if os.path.isfile(instance.picture.path):
            os.remove(instance.picture.path)

@receiver(models.signals.pre_save, sender=Profile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding Profile object is updated
    with new file.
    """
    try:
        old_file = Profile.objects.get(pk=instance.pk).picture
        new_file = instance.picture
        if old_file != new_file and old_file != Profile.DEFAULT_PICTURE:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except Profile.DoesNotExist:
        return False
