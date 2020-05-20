from django.test import TestCase

from miscosas.models import Item, Feed, User, Profile

VALID_YOUTUBE_KEY = "UC300utwSVAYOoRLEqmsprfg"
INVALID_YOUTUBE_KEY = "4v56789r384rgfrtg"


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

    def test_users_page(self):
        ''' Tests the users page with nothing on the database '''
        response = self.client.get('/users')
        self.assertContains(response, "class='no-content'", count=1, status_code=200)


class TestGetViewsContent(TestCase):

    def setUp(self):
        ''' Posts some forms to have content available '''

        form = {'key': VALID_YOUTUBE_KEY, 'origin': 'YouTube'}
        self.client.post('/feeds', form)

    def test_main_page(self):
        ''' Tests the index page after some feeds are added '''

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "class='simple-list'", count=1)
        self.assertContains(response, "class='no-content'", count=1)
        self.assertContains(response, "class='item-brief'", count=0)
        self.assertContains(response, "class='feed-brief'", count=Feed.objects.count())
        self.assertContains(response, "class='feed-form'", count=1)
        self.assertContains(response, "class='vote-form'", count=0)

    #TODO
    #def test_main_page_with_votes(self):

    def test_feeds_page(self):
        ''' Tests the feeds page after some feeds are added '''

        response = self.client.get('/feeds')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "class='simple-list'", count=1)
        self.assertContains(response, "class='feed-brief'", count=Feed.objects.count())
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
            self.assertContains(response, "class='item-brief'", count=feed.items.count())
            self.assertContains(response, "class='vote-form'", count=0)

    def test_item_page(self):
        ''' Tests an item page after some feeds are added '''

        items = Item.objects.all()
        self.assertGreater(items.count(), 0)
        for item in items:
            response = self.client.get(f'/item/{item.pk}')
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "class='feed-brief'", count=1)
            self.assertContains(response, "class='item-detailed'", count=1)
            self.assertContains(response, "class='vote-form'", count=0)
            self.assertContains(response, "class='comment-form'", count=0)


class TestGetViewsAuthenticated(TestCase):

    def setUp(self):
        ''' Posts some forms to have content available '''

        form = {'key': VALID_YOUTUBE_KEY, 'origin': 'YouTube'}
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

    #TODO
    #def test_main_page_with_votes(self):

    def test_feed_page(self):
        ''' Tests vote forms on feed page '''
        response = self.client.get('/feed/1')
        self.assertContains(response, "class='vote-form'", count=self.feed.items.count())

    def test_item_page(self):
        ''' Tests vote and comment forms on item page '''
        response = self.client.get('/item/' + str(self.item.pk))
        self.assertContains(response, "class='vote-form'", count=1)
        self.assertContains(response, "class='comment-form'", count=1)

    def test_users_page(self):
        ''' Tests user list '''
        response = self.client.get('/users')
        self.assertContains(response, "class='user-brief'", count=2)
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
        self.assertContains(response, "class='item-brief' href='/item/1'", count=1)
        self.assertContains(response, "class='item-brief' href='/item/3'", count=2)
        self.assertContains(response, "class='item-brief' href='/item/10'", count=1)
        self.assertContains(response, "class='vote-form'", count=4)

    def test_other_user_page(self):
        ''' Tests user page of a different user '''
        response = self.client.get('/user/' + self.other_user.username)
        self.assertContains(response, "class='settings-form'", count=0)
