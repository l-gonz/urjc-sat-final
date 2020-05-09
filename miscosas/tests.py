from django.test import TestCase
from django.template.loader import render_to_string

from .forms import *
from .models import *
from .feedhandler import get_youtube_feed

VALID_YOUTUBE_KEY = "UC300utwSVAYOoRLEqmsprfg"
INVALID_YOUTUBE_KEY = "4v56789r384rgfrtg"

# Create your tests here.


class TestGetViews(TestCase):

    def test_main_page(self):
        ''' Tests the index page with nothing on the database '''

        response = self.client.get('/')
        self.assertContains(response, "class='no-content'",
                            count=2, status_code=200)
        self.assertContains(response, "<form", count=1, status_code=200)

    def test_feeds_page(self):
        ''' Tests the feeds page with nothing on the database '''

        response = self.client.get('/feeds')
        self.assertContains(response, "class='no-content'",
                            count=1, status_code=200)
        self.assertContains(response, "<form", count=1, status_code=200)

    def test_feed_page(self):
        ''' Tests a feed page with nothing on the database '''
        test_strings = ['ksdhgf', '34', '0', '4kjj34', '-1', '1', '2']

        for key in test_strings:
            response = self.client.get(f'/feed/{key}')
            self.assertEqual(response.status_code, 404)
            self.assertListEqual(
                [t.name for t in response.templates],
                ['miscosas/content/not_found.html', 'miscosas/base.html']
            )

    def test_feed_page_content(self):
        ''' Tests the feed page after adding a new feed '''

        form = {'key': VALID_YOUTUBE_KEY}
        response = self.client.post('/feeds', form, follow=True)
        self.assertContains(response, "class='simple-list'",
                            count=1, status_code=200)
        self.assertContains(response, "<li>", count=15)


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
        result = get_youtube_feed(key)

        self.assertTrue(result)
        self.assertEqual(len(Feed.objects.all()), 1)
        self.assertEqual(len(Item.objects.all()), 15)

    def test_youtube_wrong_key(self):
        ''' Tests trying to add a youtube feed with an invalid key'''
        key = INVALID_YOUTUBE_KEY
        result = get_youtube_feed(key)
        self.assertFalse(result)

    def test_youtube_update(self):
        ''' Tests updating a youtube feed that already exists '''
        key = VALID_YOUTUBE_KEY
        result = get_youtube_feed(key)
        result = get_youtube_feed(key)

        self.assertTrue(result)
        self.assertEqual(len(Feed.objects.all()), 1)
        self.assertEqual(len(Item.objects.all()), 15)
