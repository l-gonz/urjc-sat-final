import datetime
import json
from xml.etree import ElementTree

from django.test import TestCase

from miscosas.models import Item, Feed, User, Profile, Vote
from miscosas.apps import MisCosasConfig as Config

VALID_YOUTUBE_KEY = "UC300utwSVAYOoRLEqmsprfg"
INVALID_YOUTUBE_KEY = "4v56789r384rgfrtg"

XML = "?format=xml"
JSON = "?format=json"


class TestGetViewsEmpty(TestCase):

    def test_main_page(self):
        ''' Tests the index page with nothing on the database '''

        response = self.client.get('/')
        self.assertContains(response, "class='no-content'", count=2)
        self.assertContains(response, "class='feed-form'", count=1)

    def test_feeds_page(self):
        ''' Tests the feeds page with nothing on the database '''

        response = self.client.get('/feeds')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "class='no-content'", count=1)
        self.assertContains(response, "class='feed-form'", count=1)

    def test_feed_page(self):
        ''' Tests a feed page with nothing on the database '''
        test_strings = ['ksdhgf', '34', '0', '4k_j%4', '-1', '1', '2']

        for key in test_strings:
            response = self.client.get(f'/feed/{key}')
            self.assertEqual(response.status_code, 404)
            self.assertIn('miscosas/content/not_found.html',
                [t.name for t in response.templates])

    def test_item_page(self):
        ''' Tests an item page with nothing on the database '''
        test_strings = ['ksdhgf', '34', '0', '4kjj34', '-1', '1', '2']

        for key in test_strings:
            response = self.client.get(f'/item/{key}')
            self.assertEqual(response.status_code, 404)
            self.assertIn('miscosas/content/not_found.html',
                [t.name for t in response.templates])

    def test_users_page(self):
        ''' Tests the users page with nothing on the database '''
        response = self.client.get('/users')
        self.assertContains(response, "class='no-content'", count=1, status_code=200)


class TestGetViewsContent(TestCase):

    def setUp(self):
        ''' Posts some forms to have content available '''

        form = {'key': VALID_YOUTUBE_KEY, 'source': Config.YOUTUBE}
        self.client.post('/feeds', form)

    def test_main_page(self):
        ''' Tests the index page after some feeds are added '''

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "class='simple-list'", count=1)
        self.assertContains(response, "class='no-content'", count=1)
        self.assertContains(response, "list-brief", count=Feed.objects.count())
        self.assertContains(response, "class='feed-form'", count=1)
        self.assertContains(response, "class='vote-form'", count=0)

    def test_feeds_page(self):
        ''' Tests the feeds page after some feeds are added '''

        response = self.client.get('/feeds')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "class='simple-list'", count=1)
        self.assertContains(response, "list-brief", count=Feed.objects.count())
        self.assertContains(response, "class='feed-form'", count=1)

    def test_feed_page(self):
        ''' Tests the feed page after some feeds are added '''

        feeds = Feed.objects.all()
        self.assertGreater(feeds.count(), 0)
        for feed in feeds:
            response = self.client.get(f'/feed/{feed.pk}')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "class='feed-detailed'", count=1)
            self.assertContains(response, "class='simple-list'", count=1)
            self.assertContains(response, "list-brief", count=10)
            self.assertContains(response, "class='vote-form'", count=0)

    def test_item_page(self):
        ''' Tests an item page after some feeds are added '''

        items = Item.objects.all()
        self.assertGreater(items.count(), 0)
        for item in items:
            response = self.client.get(f'/item/{item.pk}')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "list-brief", count=1)
            self.assertContains(response, "class='item-detailed'", count=1)
            self.assertContains(response, "class='vote-form'", count=0)
            self.assertContains(response, "class='comment-form'", count=0)


class TestGetViewsAuthenticated(TestCase):

    def setUp(self):
        ''' Posts some forms to have content available '''

        form = {'key': VALID_YOUTUBE_KEY, 'source': Config.YOUTUBE}
        self.client.post('/feeds', form)
        self.user = User.objects.create_user('root', password='toor')
        self.other_user = User.objects.create_user('aaa', password='aaa')
        self.client.force_login(self.user)
        self.item = Item.objects.get(pk=10)
        self.feed = Feed.objects.get(pk=1)

    def test_main_page(self):
        ''' Tests user lists on main menu '''
        scores = [
            i.upvote_count - i.downvote_count
            for i in Item.objects.all()
            if i.upvote_count > 0 and i.downvote_count > 0
        ][:10]

        response = self.client.get('/')
        self.assertContains(response, "class='vote-form'", count=len(scores))
        self.assertContains(response, "class='simple-list'", count=1)
        self.assertContains(response, "class='no-content'", count=2)

    def test_main_page_with_votes(self):
        ''' Tests main page after some items have been voted '''
        user_votes = [[1, 5, 6, 10, 14, 15], [2, 3, 7, 12]]
        other_user_votes = [[2, 3, 5, 12], [4, 6, 10, 13]]
        for i in user_votes:
            for j in i:
                Vote(item=Item.objects.get(pk=j), user=self.user, positive=(i == user_votes[0])).save()
        for i in other_user_votes:
            for j in i:
                Vote(item=Item.objects.get(pk=j), user=self.other_user, positive=(i == other_user_votes[0])).save()

        response = self.client.get('/')
        self.assertContains(response, "class='simple-list'", count=3)
        self.assertContains(response, "list-brief", count=16)

    def test_feed_page(self):
        ''' Tests vote forms on feed page '''
        response = self.client.get('/feed/1')
        self.assertContains(response, "class='vote-form'", count=10)

    def test_item_page(self):
        ''' Tests vote and comment forms on item page '''
        response = self.client.get('/item/' + str(self.item.pk))
        self.assertContains(response, "class='vote-form'", count=1)
        self.assertContains(response, "class='comment-form'", count=1)

    def test_users_page(self):
        ''' Tests user list '''
        response = self.client.get('/users')
        self.assertContains(response, "class='user-brief", count=2)
        self.assertContains(response, "img", count=2)

    def test_own_user_page(self):
        ''' Tests user page of logged user '''
        response = self.client.get('/user/' + self.user.username)
        self.assertContains(response, "class='settings-form'", count=1)
        self.assertContains(response, Profile.DEFAULT_PICTURE, count=1)

    def test_own_user_page_items(self):
        ''' Tests items in the user page of logged user '''

        self.client.post('/item/1', {'action': 'upvote'})
        self.client.post('/item/3', {'action': 'upvote'})
        self.client.post('/item/10', {'action': 'downvote'})
        self.client.post('/item/3', {'title': 'Hey', 'content': 'This is body', 'action': 'comment'})
        response = self.client.get('/user/' + self.user.username)

        self.assertContains(response, "class='upvoted-items'", count=1)
        self.assertContains(response, "class='downvoted-items'", count=1)
        self.assertContains(response, "class='commented-items'", count=1)
        self.assertContains(response, "list-brief", count=4)
        self.assertContains(response, "class='vote-form'", count=4)
        self.assertContains(response, "href='/item/1'", count=1)
        self.assertContains(response, "href='/item/3'", count=2)
        self.assertContains(response, "href='/item/10'", count=1)

    def test_other_user_page(self):
        ''' Tests user page of a different user '''
        response = self.client.get('/user/' + self.other_user.username)
        self.assertContains(response, "class='settings-form'", count=0)


class TestGetPagesAsXml(TestCase):

    def setUp(self):
        form = {'key': VALID_YOUTUBE_KEY, 'source': Config.YOUTUBE}
        self.client.post('/feeds', form)
        self.user = User.objects.create_user('root', password='toor')

    def test_main_page(self):
        response = self.client.get('/' + XML)
        self.assertEqual(response['content-type'], 'text/xml')
        self.assertEqual(response.status_code, 200)
        ElementTree.fromstring(response.content)

    def test_main_page_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get('/' + XML)
        self.assertEqual(response['content-type'], 'text/xml')
        self.assertEqual(response.status_code, 200)
        ElementTree.fromstring(response.content)

    def test_main_page_no_content(self):
        Feed.objects.get().delete()
        response = self.client.get('/' + XML)
        self.assertEqual(response['content-type'], 'text/xml')
        self.assertEqual(response.status_code, 200)
        ElementTree.fromstring(response.content)

    def test_feeds_page(self):
        response = self.client.get('/feeds' + XML)
        self.assertEqual(response['content-type'], 'text/xml')
        self.assertEqual(response.status_code, 200)
        ElementTree.fromstring(response.content)

    def test_feed_page_no_content(self):
        Feed.objects.get().delete()
        response = self.client.get('/feed/1' + XML)
        self.assertEqual(response.status_code, 404)
        self.assertIn('miscosas/content/not_found.html',
            [t.name for t in response.templates])

    def test_feed_page(self):
        response = self.client.get('/feed/1' + XML)
        self.assertEqual(response['content-type'], 'text/xml')
        self.assertEqual(response.status_code, 200)
        ElementTree.fromstring(response.content)

    def test_item_page(self):
        response = self.client.get('/item/1' + XML)
        self.assertEqual(response['content-type'], 'text/xml')
        self.assertEqual(response.status_code, 200)
        ElementTree.fromstring(response.content)

    def test_item_page_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get('/item/1' + XML)
        self.assertEqual(response['content-type'], 'text/xml')
        self.assertEqual(response.status_code, 200)
        ElementTree.fromstring(response.content)

    def test_users_page(self):
        response = self.client.get('/users' + XML)
        self.assertEqual(response['content-type'], 'text/xml')
        self.assertEqual(response.status_code, 200)
        ElementTree.fromstring(response.content)

    def test_user_page(self):
        response = self.client.get('/user/' + self.user.username + XML)
        self.assertEqual(response['content-type'], 'text/xml')
        self.assertEqual(response.status_code, 200)
        ElementTree.fromstring(response.content)

    def test_own_user_page(self):
        self.client.force_login(self.user)
        response = self.client.get('/user/' + self.user.username + XML)
        self.assertEqual(response['content-type'], 'text/xml')
        self.assertEqual(response.status_code, 200)
        ElementTree.fromstring(response.content)


class TestGetPagesAsJson(TestCase):

    def setUp(self):
        form = {'key': VALID_YOUTUBE_KEY, 'source': Config.YOUTUBE}
        self.client.post('/feeds', form)
        self.user = User.objects.create_user('root', password='toor')

    def test_main_page(self):
        response = self.client.get('/' + JSON)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        json.loads(response.content)

    def test_main_page_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get('/' + JSON)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        json.loads(response.content)

    def test_main_page_no_content(self):
        Feed.objects.get().delete()
        response = self.client.get('/' + JSON)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        json.loads(response.content)

    def test_feeds_page(self):
        response = self.client.get('/feeds' + JSON)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        json.loads(response.content)

    def test_feed_page_no_content(self):
        Feed.objects.get().delete()
        response = self.client.get('/feed/1' + JSON)
        self.assertEqual(response.status_code, 404)
        self.assertIn('miscosas/content/not_found.html',
            [t.name for t in response.templates])

    def test_feed_page(self):
        response = self.client.get('/feed/1' + JSON)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        json.loads(response.content)

    def test_item_page(self):
        response = self.client.get('/item/1' + JSON)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        json.loads(response.content)

    def test_item_page_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get('/item/1' + JSON)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        json.loads(response.content)

    def test_users_page(self):
        response = self.client.get('/users' + JSON)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        json.loads(response.content)

    def test_user_page(self):
        response = self.client.get('/user/' + self.user.username + JSON)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        json.loads(response.content)

    def test_own_user_page(self):
        self.client.force_login(self.user)
        response = self.client.get('/user/' + self.user.username + JSON)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        json.loads(response.content)
