from django.test import TestCase

from miscosas.models import Item, Feed
from miscosas.feeds.feedhandler import load_youtube_feed

VALID_YOUTUBE_KEY = "UC300utwSVAYOoRLEqmsprfg"
INVALID_YOUTUBE_KEY = "4v56789r384rgfrtg"


class TestFeedHandler(TestCase):

    def test_youtube_new(self):
        ''' Tests adding a new youtube feed with a valid key'''
        key = VALID_YOUTUBE_KEY
        result = load_youtube_feed(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)

    def test_youtube_wrong_key(self):
        ''' Tests trying to add a youtube feed with an invalid key'''
        key = INVALID_YOUTUBE_KEY
        result = load_youtube_feed(key)
        self.assertFalse(result)

    def test_youtube_update(self):
        ''' Tests updating a youtube feed that already exists '''
        key = VALID_YOUTUBE_KEY
        result = load_youtube_feed(key)
        result = load_youtube_feed(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)
