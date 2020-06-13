from time import sleep
from urllib.error import URLError, HTTPError

from django.test import TestCase

from miscosas.models import Item, Feed
from miscosas.apps import MisCosasConfig as Config
from miscosas.feeds.feedhandler import FEEDS_DATA
from miscosas.feeds.feedparser import ParsingError

VALID_YOUTUBE_KEY = "UC300utwSVAYOoRLEqmsprfg"
INVALID_YOUTUBE_KEY = "4v56789r384rgfrtg"

VALID_LAST_FM_KEY = "Linkin Park"
INVALID_LAST_FM_KEY = "nj34jsdgf"

VALID_REDDIT_KEY = "memes"
INVALID_REDDIT_KEY = "gh67g"

VALID_FLICKR_KEY = "fuenlabrada"
INVALID_FLICKR_KEY = "vkldjg48jvg"

VALID_GOODREADS_NAME_KEY = "Trudi Canavan"
VALID_GOODREADS_ID_KEY = "15890"
INVALID_GOODREADS_KEY = "iejlgn4u5t549tgjhg"

VALID_SPOTIFY_NAME_KEY = "Green Day"
VALID_SPOTIFY_ID_KEY = "7oPftvlwr6VrsViSDV7fJY"
INVALID_SPOTIFY_KEY = "iej%n4u5t(549.gjhg"


class TestYoutubeFeed(TestCase):

    def test_youtube_new(self):
        ''' Tests adding a new youtube feed with a valid key'''
        key = VALID_YOUTUBE_KEY
        sleep(0.5)
        result = FEEDS_DATA[Config.YOUTUBE].load(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)

    def test_youtube_wrong_key(self):
        ''' Tests trying to add a youtube feed with an invalid key'''
        key = INVALID_YOUTUBE_KEY
        sleep(0.5)
        with self.assertRaisesMessage(HTTPError, '404: Not Found'):
            FEEDS_DATA[Config.YOUTUBE].load(key)
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_youtube_update(self):
        ''' Tests updating a youtube feed that already exists '''
        key = VALID_YOUTUBE_KEY
        sleep(0.5)
        FEEDS_DATA[Config.YOUTUBE].load(key)
        sleep(0.5)
        result = FEEDS_DATA[Config.YOUTUBE].load(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)


class TestLastFmFeed(TestCase):

    def test_last_fm_new(self):
        ''' Tests adding a new last fm feed with a valid key'''
        key = VALID_LAST_FM_KEY
        sleep(0.5)
        result = FEEDS_DATA[Config.LASTFM].load(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)

    def test_last_fm_wrong_key(self):
        ''' Tests trying to add a last fm feed with an invalid key'''
        key = INVALID_LAST_FM_KEY
        sleep(0.5)
        with self.assertRaisesMessage(HTTPError, '400: Bad Request'):
            FEEDS_DATA[Config.LASTFM].load(key)
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_last_fm_update(self):
        ''' Tests updating a last fm feed that already exists '''
        key = VALID_LAST_FM_KEY
        sleep(0.5)
        FEEDS_DATA[Config.LASTFM].load(key)
        sleep(0.5)
        result = FEEDS_DATA[Config.LASTFM].load(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)


class TestRedditFeed(TestCase):

    def test_reddit_new(self):
        ''' Tests adding a new reddit feed with a valid key'''
        key = VALID_REDDIT_KEY
        sleep(1)
        result = FEEDS_DATA[Config.REDDIT].load(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 26)

    def test_reddit_wrong_key(self):
        ''' Tests trying to add a reddit feed with an invalid key'''
        key = INVALID_REDDIT_KEY
        sleep(0.5)
        with self.assertRaisesMessage(ParsingError, 'Key not found'):
            FEEDS_DATA[Config.REDDIT].load(key)

        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_reddit_update(self):
        ''' Tests updating a reddit feed that already exists '''
        key = VALID_REDDIT_KEY
        sleep(1)
        FEEDS_DATA[Config.REDDIT].load(key)
        sleep(1)
        result = FEEDS_DATA[Config.REDDIT].load(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 26)


class TestFlickrFeed(TestCase):

    def test_flickr_new(self):
        ''' Tests adding a new flickr feed with a valid key'''
        key = VALID_FLICKR_KEY
        sleep(0.5)
        result = FEEDS_DATA[Config.FLICKR].load(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 20)

    def test_flickr_wrong_key(self):
        ''' Tests trying to add a flickr feed with an invalid key'''
        key = INVALID_FLICKR_KEY
        sleep(0.5)

        with self.assertRaisesMessage(ParsingError, 'Feed has no items'):
            FEEDS_DATA[Config.FLICKR].load(key)

        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_flickr_update(self):
        ''' Tests updating a flickr feed that already exists '''
        key = VALID_FLICKR_KEY
        sleep(0.5)
        FEEDS_DATA[Config.FLICKR].load(key)
        sleep(0.5)
        result = FEEDS_DATA[Config.FLICKR].load(key)

        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 20)


class TestGoodreadsFeed(TestCase):

    def test_goodreads_name_new(self):
        ''' Tests adding a new goodreads feed with a valid name key'''
        sleep(1.5)
        key = VALID_GOODREADS_NAME_KEY
        result = FEEDS_DATA[Config.GOODREADS].load(key)

        self.assertTrue(result)
        feed = Feed.objects.get()
        self.assertEqual(feed.key, VALID_GOODREADS_ID_KEY)
        self.assertEqual(feed.title, VALID_GOODREADS_NAME_KEY)
        self.assertEqual(Item.objects.count(), 14)

    def test_goodreads_id_new(self):
        ''' Tests adding a new goodreads feed with a valid id key'''
        sleep(1.5)
        key = VALID_GOODREADS_ID_KEY
        result = FEEDS_DATA[Config.GOODREADS].load(key)

        self.assertTrue(result)
        feed = Feed.objects.get()
        self.assertEqual(feed.key, VALID_GOODREADS_ID_KEY)
        self.assertEqual(feed.title, VALID_GOODREADS_NAME_KEY)
        self.assertEqual(Item.objects.count(), 14)

    def test_goodreads_wrong_key(self):
        ''' Tests trying to add a goodreads feed with an invalid key'''
        sleep(1.5)
        key = INVALID_GOODREADS_KEY
        with self.assertRaisesMessage(ParsingError, 'Key not found'):
            FEEDS_DATA[Config.GOODREADS].load(key)

        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_goodreads_update(self):
        ''' Tests updating a goodreads feed that already exists '''
        sleep(1.5)
        key = VALID_GOODREADS_NAME_KEY
        feed = FEEDS_DATA[Config.GOODREADS].load(key)
        self.assertEqual(feed.key, VALID_GOODREADS_ID_KEY)

        sleep(1.5)
        result = FEEDS_DATA[Config.GOODREADS].load(feed.key)
        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 14)


class TestSpotifyFeed(TestCase):

    def test_spotify_name_new(self):
        ''' Tests adding a new spotify feed with a valid name key'''
        sleep(1.5)
        key = VALID_SPOTIFY_NAME_KEY
        result = FEEDS_DATA[Config.SPOTIFY].load(key)

        self.assertTrue(result)
        feed = Feed.objects.get()
        self.assertEqual(feed.key, VALID_SPOTIFY_ID_KEY)
        self.assertEqual(feed.title, VALID_SPOTIFY_NAME_KEY)
        self.assertEqual(Item.objects.count(), 10)

    def test_spotify_id_new(self):
        ''' Tests adding a new spotify feed with a valid id key'''
        sleep(1.5)
        key = VALID_SPOTIFY_ID_KEY
        result = FEEDS_DATA[Config.SPOTIFY].load(key)

        self.assertTrue(result)
        feed = Feed.objects.get()
        self.assertEqual(feed.key, VALID_SPOTIFY_ID_KEY)
        self.assertEqual(feed.title, VALID_SPOTIFY_NAME_KEY)
        self.assertEqual(Item.objects.count(), 10)

    def test_spotify_wrong_key(self):
        ''' Tests trying to add a spotify feed with an invalid key'''
        key = INVALID_SPOTIFY_KEY
        sleep(0.5)
        with self.assertRaisesMessage(HTTPError, '400: Bad Request'):
            result = FEEDS_DATA[Config.SPOTIFY].load(key)

        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_spotify_update(self):
        ''' Tests updating a spotify feed that already exists '''
        key = VALID_SPOTIFY_NAME_KEY
        feed = FEEDS_DATA[Config.SPOTIFY].load(key)
        self.assertEqual(feed.key, VALID_SPOTIFY_ID_KEY)

        sleep(1)
        result = FEEDS_DATA[Config.SPOTIFY].load(feed.key)
        self.assertTrue(result)
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 10)
