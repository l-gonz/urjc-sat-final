from django.test import TestCase

from miscosas.models import Item, Feed
from miscosas.feeds.feedhandler import YOUTUBE_FEED, LAST_FM_FEED

VALID_YOUTUBE_KEY = "UC300utwSVAYOoRLEqmsprfg"
INVALID_YOUTUBE_KEY = "4v56789r384rgfrtg"

VALID_LAST_FM_KEY = "Cher"
INVALID_LAST_FM_KEY = "nj34jsdgf"


class TestYoutubeFeed(TestCase):

    def test_youtube_new(self):
        ''' Tests adding a new youtube feed with a valid key'''
        key = VALID_YOUTUBE_KEY
        result = YOUTUBE_FEED.load(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)

    def test_youtube_wrong_key(self):
        ''' Tests trying to add a youtube feed with an invalid key'''
        key = INVALID_YOUTUBE_KEY
        result = YOUTUBE_FEED.load(key)
        self.assertFalse(result)

    def test_youtube_update(self):
        ''' Tests updating a youtube feed that already exists '''
        key = VALID_YOUTUBE_KEY
        result = YOUTUBE_FEED.load(key)
        result = YOUTUBE_FEED.load(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)


class TestLastFmFeed(TestCase):

    def test_last_fm_new(self):
        ''' Tests adding a new last fm feed with a valid key'''
        key = VALID_LAST_FM_KEY
        result = LAST_FM_FEED.load(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)

    def test_last_fm_wrong_key(self):
        ''' Tests trying to add a last fm feed with an invalid key'''
        key = INVALID_LAST_FM_KEY
        result = LAST_FM_FEED.load(key)
        self.assertFalse(result)

    def test_last_fm_update(self):
        ''' Tests updating a last fm feed that already exists '''
        key = VALID_LAST_FM_KEY
        result = LAST_FM_FEED.load(key)
        result = LAST_FM_FEED.load(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)
