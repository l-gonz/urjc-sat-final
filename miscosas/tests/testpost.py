from django.test import TestCase
from django.contrib.auth.models import User

from miscosas.forms import FeedForm
from miscosas.models import Item, Feed, Comment

VALID_YOUTUBE_KEY = "UC300utwSVAYOoRLEqmsprfg"
INVALID_YOUTUBE_KEY = "4v56789r384rgfrtg"


class TestPostFeedViews(TestCase):

    def test_feed_form_right(self):
        ''' Tests posting the feed form with a valid key '''
        form_data = {'key': VALID_YOUTUBE_KEY}
        form = FeedForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertRedirects(response, '/feed/1')
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)

    def test_feed_form_wrong(self):
        ''' Tests posting the feed form with an invalid key '''
        form_data = {'key': INVALID_YOUTUBE_KEY}
        form = FeedForm(form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertEqual(response.status_code, 404)
        self.assertListEqual(
            [t.name for t in response.templates],
            ['miscosas/content/not_found.html', 'miscosas/base.html'])


class TestPostCommentViews(TestCase):

    def setUp(self):
        ''' Set up some items so that comments can be added '''
        form = {'key': VALID_YOUTUBE_KEY}
        self.client.post('/feeds', form)
        user = User.objects.create_user('root', password='toor')
        self.client.force_login(user)

    def test_comment_form_rigth(self):
        ''' Tests posting a new comment '''
        form = {
            'title': 'Hola',
            'content': 'This is my comment',
            'action': 'comment'
        }

        response = self.client.post('/item/1', form)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertContains(response, "class='simple-list'", count=1, status_code=200)

    def test_comment_form_no_user(self):
        ''' Tests posting a new comment without being logged in '''
        self.client.logout()
        form = {
            'title': 'Hola',
            'content': 'This is my comment',
            'action': 'comment'
        }

        response = self.client.post('/item/1', form)
        self.assertContains(response, "class='no-content'", count=1, status_code=200)
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_invalid_item(self):
        ''' Tests posting a new comment on an invalid item '''
        form = {
            'title': 'Hola',
            'content': 'This is my comment',
            'action': 'comment'
        }

        response = self.client.post('/item/f56', form)
        self.assertEqual(response.status_code, 404)
        self.assertListEqual(
            [t.name for t in response.templates],
            ['miscosas/content/not_found.html', 'miscosas/base.html'])

    def test_comment_too_long(self):
        ''' Tests posting a new comment on an invalid item '''
        form = {
            'title': 'Too big title of more than 64 characterssssssssssssssssssssssssssss12345678901234567890',
            'content': 'This is my comment',
            'action': 'comment'
        }

        response = self.client.post('/item/1', form)
        self.assertEqual(Comment.objects.count(), 0)
        self.assertContains(response, "class='no-content'", count=1, status_code=200)


class TestPostVoteForm(TestCase):

    def setUp(self):
        ''' Set up some items so that comments can be added '''
        form = {'key': VALID_YOUTUBE_KEY}
        self.client.post('/feeds', form)
        self.user = User.objects.create_user('root', password='toor')
        self.client.force_login(self.user)
        self.item = Item.objects.get(pk=10)

    def test_vote_no_user(self):
        ''' Tests voting without being logged in '''
        self.client.logout()
        self.client.post(f'/item/{self.item.pk}', {'action': 'downvote'})
        self.assertEqual(self.item.upvote_count, 0)
        self.assertEqual(self.item.downvote_count, 0)


    def test_vote_first_time(self):
        ''' Tests voting without having voted before '''
        self.client.post(f'/item/{self.item.pk}', {'action': 'upvote'})
        self.assertEqual(self.item.upvote_count, 1)
        self.assertEqual(self.item.downvote_count, 0)
        self.assertTrue(self.item.upvotes.filter(pk=self.user.pk).exists())

    def test_vote_again(self):
        ''' Tests voting twice the same item '''
        self.client.post(f'/item/{self.item.pk}', {'action': 'upvote'})
        self.client.post(f'/item/{self.item.pk}', {'action': 'upvote'})
        self.assertEqual(self.item.upvote_count, 1)
        self.assertEqual(self.item.downvote_count, 0)
        self.assertTrue(self.item.upvotes.filter(pk=self.user.pk).exists())

    def test_vote_change(self):
        ''' Tests changing the vote on an item '''
        self.client.post(f'/item/{self.item.pk}', {'action': 'downvote'})
        self.assertEqual(self.item.upvote_count, 0)
        self.assertEqual(self.item.downvote_count, 1)

        self.client.post(f'/item/{self.item.pk}', {'action': 'upvote'})
        self.assertEqual(self.item.upvote_count, 1)
        self.assertEqual(self.item.downvote_count, 0)

    def test_vote_invalid_item(self):
        ''' Tests voting on an invalid item '''
        self.client.post(f'/item/484', {'action': 'downvote'})
        self.assertEqual(self.item.upvote_count, 0)
        self.assertEqual(self.item.downvote_count, 0)