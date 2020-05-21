from django.test import TestCase
from django.contrib.auth.models import User

from miscosas.forms import FeedForm
from miscosas.models import Item, Feed, Comment, Profile, Vote
from miscosas.feeds.feedhandler import YOUTUBE_FEED, LAST_FM_FEED

VALID_YOUTUBE_KEY = "UC300utwSVAYOoRLEqmsprfg"
INVALID_YOUTUBE_KEY = "4v56789r384rgfrtg"

VALID_LAST_FM_KEY = 'Cher'
INVALID_LAST_FM_KEY = 'hfds8f7d'


class TestPostFeedViews(TestCase):

    def test_feed_youtube_right(self):
        ''' Tests posting the feed form with a valid key '''
        form_data = {'key': VALID_YOUTUBE_KEY, 'origin': YOUTUBE_FEED.name}
        form = FeedForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertRedirects(response, '/feed/1')
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)

    def test_feed_youtube_wrong(self):
        ''' Tests posting the feed form with an invalid key '''
        form_data = {'key': INVALID_YOUTUBE_KEY, 'origin': YOUTUBE_FEED.name}
        form = FeedForm(form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertEqual(response.status_code, 404)
        self.assertListEqual(
            [t.name for t in response.templates],
            ['miscosas/content/not_found.html', 'miscosas/base.html'])

    def test_feed_last_fm_right(self):
        ''' Tests posting the feed form with a valid key '''
        form_data = {'key': VALID_LAST_FM_KEY, 'origin': LAST_FM_FEED.name}
        form = FeedForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertRedirects(response, '/feed/1')
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)

    def test_feed_last_fm_wrong(self):
        ''' Tests posting the feed form with an invalid key '''
        form_data = {'key': INVALID_LAST_FM_KEY, 'origin': LAST_FM_FEED.name}
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
        form = {'key': VALID_YOUTUBE_KEY, 'origin': YOUTUBE_FEED.name}
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
        ''' Set up some items so that votes can be added '''
        form = {'key': VALID_YOUTUBE_KEY, 'origin': YOUTUBE_FEED.name}
        self.client.post('/feeds', form)
        self.user = User.objects.create_user('root', password='toor')
        self.client.force_login(self.user)
        self.item = Item.objects.get(pk=10)

    def test_vote_no_user(self):
        ''' Tests voting without being logged in '''
        self.client.logout()
        self.client.post(f'/item/{self.item.pk}', {'action': 'downvote'})
        self.assertEqual(Vote.objects.count(), 0)
        self.assertEqual(self.item.upvote_count, 0)
        self.assertEqual(self.item.downvote_count, 0)

    def test_vote_first_time(self):
        ''' Tests voting without having voted before '''
        self.client.post(f'/item/{self.item.pk}', {'action': 'upvote'})
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.get().item, self.item)
        self.assertEqual(Vote.objects.get().user, self.user)
        self.assertEqual(self.item.upvote_count, 1)
        self.assertEqual(self.item.downvote_count, 0)
        self.assertEqual(self.user.profile.vote_count, 1)

    def test_vote_again(self):
        ''' Tests voting twice the same item '''
        self.client.post(f'/item/{self.item.pk}', {'action': 'upvote'})
        self.client.post(f'/item/{self.item.pk}', {'action': 'upvote'})
        self.assertEqual(self.item.upvote_count, 1)
        self.assertEqual(self.item.downvote_count, 0)
        self.assertEqual(self.user.profile.vote_count, 1)
        self.assertEqual(Vote.objects.count(), 1)

    def test_vote_change(self):
        ''' Tests changing the vote on an item '''
        self.client.post(f'/item/{self.item.pk}', {'action': 'downvote'})
        self.assertFalse(Vote.objects.get().positive)

        self.client.post(f'/item/{self.item.pk}', {'action': 'upvote'})
        self.assertTrue(Vote.objects.get().positive)

        self.assertEqual(Vote.objects.count(), 1)

    def test_vote_invalid_item(self):
        ''' Tests voting on an invalid item '''
        self.client.post(f'/item/484', {'action': 'downvote'})
        self.assertEqual(Vote.objects.count(), 0)


class TestPostProfileForm(TestCase):

    def setUp(self):
        ''' Add some users to test profile '''

        self.user = User.objects.create_user('root', password='toor')
        self.other_user = User.objects.create_user('aaa', password='aaa')
        self.client.force_login(self.user)

    def test_change_font_size(self):
        form = {
            'theme': self.user.profile.theme,
            'font_size': Profile.LARGE_FONT,
        }

        response = self.client.post('/user/' + self.user.username, form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(username=self.user.username).profile.font_size, Profile.LARGE_FONT)

    def test_change_theme(self):
        form = {
            'theme': Profile.DARKMODE,
            'font_size': self.user.profile.font_size,
        }

        response = self.client.post('/user/' + self.user.username, form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(username=self.user.username).profile.theme, Profile.DARKMODE)

    def test_post_wrong_user(self):
        form = {
            'theme': Profile.DARKMODE,
            'font_size': Profile.LARGE_FONT,
        }

        response = self.client.post('/user/' + self.other_user.username, form)
        self.assertEqual(response.status_code, 200)
        profile = User.objects.get(username=self.other_user.username).profile
        self.assertEqual(profile.font_size, Profile.MEDIUM_FONT)
        self.assertEqual(profile.theme, Profile.LIGHTMODE)


class TestPostFeedChoose(TestCase):

    def setUp(self):
        ''' Set up some feeds so that votes can be added '''
        form = {'key': VALID_YOUTUBE_KEY, 'origin': YOUTUBE_FEED.name}
        self.client.post('/feeds', form)
        form = {'key': VALID_LAST_FM_KEY, 'origin': LAST_FM_FEED.name}
        self.client.post('/feeds', form)

    def test_unchoose_feed(self):
        ''' Tests form for unchoosing feed '''
        form = {'action': 'unchoose'}
        self.client.post('/feed/1', form)
        self.assertFalse(Feed.objects.get(pk=1).chosen)
        self.assertTrue(Feed.objects.get(pk=2).chosen)

        response = self.client.get('/')
        self.assertContains(response, "class='feed-brief'", 1)

    def test_rechoose_feed(self):
        form = {'action': 'unchoose'}
        self.client.post('/feed/1', form)
        form = {'key': VALID_YOUTUBE_KEY, 'origin': YOUTUBE_FEED.name}
        self.client.post('/feeds', form)

        self.assertTrue(Feed.objects.get(pk=1).chosen)
        self.assertTrue(Feed.objects.get(pk=2).chosen)

        response = self.client.get('/')
        self.assertContains(response, "class='feed-brief'", 2)

    #TODO
    #def test_user_chosen_feeds(self):
