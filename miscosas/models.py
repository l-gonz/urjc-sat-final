"""
Models for app MisCosas
"""

import os

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .apps import MisCosasConfig as Config
from .feeds.feedhandler import FEEDS_DATA


class Feed(models.Model):
    SOURCES = {
        Config.YOUTUBE: 'YouTube',
        Config.LASTFM: 'last.fm',
    }
    key = models.CharField(max_length=64,
        help_text=_('Name or id to identify the feed'),
        verbose_name=_('key'))
    title = models.CharField(max_length=64, verbose_name=_('title'))
    source = models.CharField(max_length=32,
        choices=list(SOURCES.items()),
        default=Config.YOUTUBE,
        verbose_name=_('source'))
    chosen = models.BooleanField(default=True, verbose_name=_('chosen'))

    class Meta:
        verbose_name = _('feed')
        verbose_name_plural = _('feeds')

    def __str__(self):
        return self.SOURCES[self.source] + ': ' + self.title

    @property
    def source_pretty(self):
        return Feed.SOURCES[self.source]

    @property
    def score(self):
        upvotes = Vote.objects.filter(item__feed=self, positive=True).count()
        downvotes = Vote.objects.filter(item__feed=self, positive=False).count()
        return upvotes - downvotes

    @property
    def link(self):
        return FEEDS_DATA[self.source].get_feed_url(self.key)


class Item(models.Model):
    key = models.CharField(max_length=64, verbose_name=_('key'))
    title = models.CharField(max_length=64, verbose_name=_('title'))
    feed = models.ForeignKey(Feed, models.CASCADE,
        related_name="items",
        verbose_name=_('feed'))
    description = models.TextField(blank=True, default='', verbose_name=_('description'))
    picture = models.URLField(blank=True, default='', verbose_name=_('picture'))

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')

    def __str__(self):
        return str(self.feed) + ", " + self.title

    @property
    def upvote_count(self):
        ''' Upvote count property for templates '''
        return self.votes.filter(positive=True).count()

    @property
    def downvote_count(self):
        ''' Downvote count property for templates '''
        return self.votes.filter(positive=False).count()

    @property
    def upvoters(self):
        ups = self.votes.filter(positive=True)
        return [vote.user.pk for vote in ups]

    @property
    def downvoters(self):
        downs = self.votes.filter(positive=False)
        return [vote.user.pk for vote in downs]

    @property
    def link(self):
        return FEEDS_DATA[self.feed.source].get_item_url(self.feed.key, self.key)


class Vote(models.Model):
    positive = models.BooleanField(verbose_name=_('positive'))
    date = models.DateTimeField(auto_now=True, verbose_name=_('date'))
    user = models.ForeignKey(User, models.CASCADE,
        related_name='votes', verbose_name=_('user'))
    item = models.ForeignKey(Item, models.CASCADE,
        related_name='votes', verbose_name=_('item'))

    class Meta:
        unique_together = ('user', 'item',)
        verbose_name = _('vote')
        verbose_name_plural = _('votes')


class Comment(models.Model):
    title = models.CharField(max_length=64, verbose_name=_('title'))
    content = models.CharField(max_length=256, verbose_name=_('content'))
    date = models.DateTimeField(auto_now=True, verbose_name=_('date'))
    item = models.ForeignKey(Item, models.CASCADE,
        related_name='comments', verbose_name=_('item'))
    user = models.ForeignKey(User, models.CASCADE,
    related_name='comments', verbose_name=_('user'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')


class Profile(models.Model):
    DEFAULT_PICTURE = 'blank-profile-picture.png'

    user = models.OneToOneField(User, models.CASCADE, verbose_name=_('user'))
    _picture = models.ImageField(blank=True, null=True, verbose_name=_('picture'))
    theme = models.CharField(max_length=2, choices=Config.THEMES,
        default=Config.LIGHTMODE, verbose_name=_('theme'))
    font_size = models.CharField(max_length=2, choices=Config.FONT_SIZES,
        default=Config.MEDIUM_FONT, verbose_name=_('font size'))

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return str(self.user)

    @property
    def picture(self):
        try:
            if os.path.isfile(self._picture.path):
                return self._picture.name
            Profile.objects.filter(pk=self.pk).update(_picture=None)
            return self.DEFAULT_PICTURE
        except ValueError:
            return self.DEFAULT_PICTURE

    @property
    def vote_count(self):
        return self.user.votes.count()

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
        if os.path.isfile(instance._picture.path):
            os.remove(instance._picture.path)

@receiver(models.signals.pre_save, sender=Profile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding Profile object is updated
    with new file.
    """
    try:
        old_profile = Profile.objects.get(pk=instance.pk)
        new_file = instance.picture
        if old_profile.picture != new_file and old_profile.picture != Profile.DEFAULT_PICTURE:
            if os.path.isfile(old_profile._picture.path):
                os.remove(old_profile._picture.path)
    except Profile.DoesNotExist:
        return False
