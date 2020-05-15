from django.test import TestCase

from miscosas.models import Item, Feed

VALID_YOUTUBE_KEY = "UC300utwSVAYOoRLEqmsprfg"
INVALID_YOUTUBE_KEY = "4v56789r384rgfrtg"


class TestGetViewsEmpty(TestCase):

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

        form = {'key': VALID_YOUTUBE_KEY, 'origin': 'YouTube'}
        self.client.post('/feeds', form)

    def test_main_page(self):
        ''' Tests the index page after some feeds are added '''

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "class='simple-list'", count=2)
        self.assertContains(response, "class='item-brief'", count=Item.objects.count())
        self.assertContains(response, "class='feed-brief'", count=Feed.objects.count())
        self.assertContains(response, "<form", count=1)

    def test_feeds_page(self):
        ''' Tests the feeds page after some feeds are added '''

        response = self.client.get('/feeds')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "class='simple-list'", count=1)
        self.assertContains(response, "class='feed-brief'", count=Feed.objects.count())
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


class TestGetViewsAuthenticated(TestCase):
    pass