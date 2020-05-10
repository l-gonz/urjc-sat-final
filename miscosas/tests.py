from django.test import TestCase
from django.template.loader import render_to_string

from .forms import *
from .models import *
from .feedhandler import load_youtube_feed

VALID_YOUTUBE_KEY = "UC300utwSVAYOoRLEqmsprfg"
INVALID_YOUTUBE_KEY = "4v56789r384rgfrtg"


class TestGetViews(TestCase):

    def test_main_page(self):
        ''' Tests the index page with nothing on the database '''

        response = self.client.get('/')
        self.assertContains(response, "class='no-content'", count=2)
        self.assertContains(response, "<form", count=1)

    def test_feeds_page(self):
        ''' Tests the feeds page with nothing on the database '''

        response = self.client.get('/feeds')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "class='no-content'", count=1)
        self.assertContains(response, "<form", count=1)

    def test_feed_page(self):
        ''' Tests a feed page with nothing on the database '''
        test_strings = ['ksdhgf', '34', '0', '4k_j%4', '-1', '1', '2']

        for key in test_strings:
            response = self.client.get(f'/feed/{key}')
            self.assertEqual(response.status_code, 404)
            self.assertListEqual(
                [t.name for t in response.templates],
                ['miscosas/content/not_found.html', 'miscosas/base.html']
            )

    def test_item_page(self):
        ''' Tests an item page with nothing on the database '''
        test_strings = ['ksdhgf', '34', '0', '4kjj34', '-1', '1', '2']

        for key in test_strings:
            response = self.client.get(f'/item/{key}')
            self.assertEqual(response.status_code, 404)
            self.assertListEqual(
                [t.name for t in response.templates],
                ['miscosas/content/not_found.html', 'miscosas/base.html']
            )


class TestGetViewsContent(TestCase):

    def setUp(self):
        ''' Posts some forms to have content available '''

        form = {'key': VALID_YOUTUBE_KEY}
        self.client.post('/feeds', form)

    def test_main_page(self):
        ''' Tests the index page after some feeds are added '''

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "class='simple-list'", count=2)
        self.assertContains(response, "class='item-brief'", count=Item.objects.all().count())
        self.assertContains(response, "class='feed-brief'", count=Feed.objects.all().count())
        self.assertContains(response, "<form", count=1)

    def test_feeds_page(self):
        ''' Tests the feeds page after some feeds are added '''

        response = self.client.get('/feeds')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "class='simple-list'", count=1)
        self.assertContains(response, "class='feed-brief'", count=Feed.objects.all().count())
        self.assertContains(response, "<form", count=1)

    def test_feed_page(self):
        ''' Tests the feed page after some feeds are added '''

        feeds = Feed.objects.all()
        self.assertGreater(feeds.count(), 0)
        for feed in feeds:
            response = self.client.get(f'/feed/{feed.pk}')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "class='feed-detailed'", count=1)
            self.assertContains(response, "class='simple-list'", count=1)
            self.assertContains(response, "class='item-brief'", count=feed.item_set.count())

    def test_item_page(self):
        ''' Tests an item page after some feeds are added '''

        items = Item.objects.all()
        self.assertGreater(items.count(), 0)
        for item in items:
            response = self.client.get(f'/item/{item.pk}')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "class='feed-brief'", count=1)
            self.assertContains(response, "class='item-detailed'", count=1)


class TestPostViews(TestCase):

    def test_feed_form_right(self):
        ''' Tests posting the feed form with a valid key '''
        form_data = {'key': VALID_YOUTUBE_KEY}
        form = FeedForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertRedirects(response, '/feed/1')
        self.assertEqual(len(Feed.objects.all()), 1)
        self.assertEqual(len(Item.objects.all()), 15)

    def test_feed_form_wrong(self):
        ''' Tests posting the feed form with an invalid key '''
        form_data = {'key': INVALID_YOUTUBE_KEY}
        form = FeedForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertEqual(response.status_code, 404)
        self.assertListEqual(
            [t.name for t in response.templates],
            ['miscosas/content/not_found.html', 'miscosas/base.html'])


class TestFeedHandler(TestCase):

    def test_youtube_new(self):
        ''' Tests adding a new youtube feed with a valid key'''
        key = VALID_YOUTUBE_KEY
        result = load_youtube_feed(key)

        self.assertTrue(result)
        self.assertEqual(len(Feed.objects.all()), 1)
        self.assertEqual(len(Item.objects.all()), 15)

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
        self.assertEqual(len(Feed.objects.all()), 1)
        self.assertEqual(len(Item.objects.all()), 15)
