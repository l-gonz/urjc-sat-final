from time import sleep

from django.test import TestCase
from django.contrib.auth.models import User

from miscosas.forms import FeedForm
from miscosas.models import Item, Feed, Comment, Vote
from miscosas.apps import MisCosasConfig as Config

VALID_YOUTUBE_KEY = "UC300utwSVAYOoRLEqmsprfg"
INVALID_YOUTUBE_KEY = "4v56789r384rgfrtg"

VALID_LAST_FM_KEY = 'Linkin Park'
INVALID_LAST_FM_KEY = 'hfds8f7d'

VALID_REDDIT_KEY = "memes"
INVALID_REDDIT_KEY = "gh67g"

VALID_FLICKR_KEY = "fuenlabrada"
INVALID_FLICKR_KEY = "vkldjg48jvg"

VALID_GOODREADS_KEY = "Trudi Canavan"
INVALID_GOODREADS_KEY = "iejlgn4u5t549tgjhg"

VALID_SPOTIFY_KEY = "Green Day"
INVALID_SPOTIFY_KEY = "iej%n4u5t(549.gjhg"


class TestPostFeedViews(TestCase):

    def setUp(self):
        # Some APIs refuse the connection if too many requests
        # are made too close together
        sleep(1)

    def test_feed_youtube_right(self):
        ''' Tests posting the feed form with a valid key '''
        form_data = {'key': VALID_YOUTUBE_KEY, 'source': Config.YOUTUBE}
        form = FeedForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertRedirects(response, '/feed/1')
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)

    def test_feed_youtube_wrong(self):
        ''' Tests posting the feed form with an invalid key '''
        form_data = {'key': INVALID_YOUTUBE_KEY, 'source': Config.YOUTUBE}
        form = FeedForm(form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('miscosas/content/not_found.html',
            [t.name for t in response.templates])

    def test_feed_last_fm_right(self):
        ''' Tests posting the feed form with a valid key '''
        form_data = {'key': VALID_LAST_FM_KEY, 'source': Config.LASTFM}
        form = FeedForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertRedirects(response, '/feed/1')
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 15)

    def test_feed_last_fm_wrong(self):
        ''' Tests posting the feed form with an invalid key '''
        form_data = {'key': INVALID_LAST_FM_KEY, 'source': Config.LASTFM}
        form = FeedForm(form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('miscosas/content/not_found.html',
            [t.name for t in response.templates])

    def test_feed_reddit_right(self):
        ''' Tests posting the feed form with a valid key '''
        form_data = {'key': VALID_REDDIT_KEY, 'source': Config.REDDIT}
        form = FeedForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertRedirects(response, '/feed/1')
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 26)

    def test_feed_reddit_wrong(self):
        ''' Tests posting the feed form with an invalid key '''
        form_data = {'key': INVALID_REDDIT_KEY, 'source': Config.REDDIT}
        form = FeedForm(form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('miscosas/content/not_found.html',
            [t.name for t in response.templates])

    def test_feed_flickr_right(self):
        ''' Tests posting the feed form with a valid key '''
        form_data = {'key': VALID_FLICKR_KEY, 'source': Config.FLICKR}
        form = FeedForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertRedirects(response, '/feed/1')
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 20)

    def test_feed_flickr_wrong(self):
        ''' Tests posting the feed form with an invalid key '''
        form_data = {'key': INVALID_FLICKR_KEY, 'source': Config.FLICKR}
        form = FeedForm(form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('miscosas/content/not_found.html',
            [t.name for t in response.templates])

    def test_feed_goodreads_right(self):
        ''' Tests posting the feed form with a valid key '''
        form_data = {'key': VALID_GOODREADS_KEY, 'source': Config.GOODREADS}
        form = FeedForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertRedirects(response, '/feed/1')
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 14)

    def test_feed_goodreads_wrong(self):
        ''' Tests posting the feed form with an invalid key '''
        form_data = {'key': INVALID_GOODREADS_KEY, 'source': Config.GOODREADS}
        form = FeedForm(form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('miscosas/content/not_found.html',
            [t.name for t in response.templates])

    def test_feed_spotify_right(self):
        ''' Tests posting the feed form with a valid key '''
        form_data = {'key': VALID_SPOTIFY_KEY, 'source': Config.SPOTIFY}
        form = FeedForm(data=form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertRedirects(response, '/feed/1')
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 10)

    def test_feed_spotify_wrong(self):
        ''' Tests posting the feed form with an invalid key '''
        form_data = {'key': INVALID_SPOTIFY_KEY, 'source': Config.SPOTIFY}
        form = FeedForm(form_data)
        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)
        self.assertEqual(response.status_code, 404)
        self.assertIn('miscosas/content/not_found.html',
            [t.name for t in response.templates])

class TestPostCommentViews(TestCase):

    sample_form = {
        'title': 'Hola',
        'content': 'This is my comment',
        'action': 'comment'
    }

    def setUp(self):
        ''' Set up some items so that comments can be added '''
        form = {'key': VALID_YOUTUBE_KEY, 'source': Config.YOUTUBE}
        self.client.post('/feeds', form)
        self.user = User.objects.create_user('root', password='toor')
        self.other_user = User.objects.create_user('root1', password='toor')
        self.client.force_login(self.user)

    def test_comment_form_rigth(self):
        ''' Tests posting a new comment '''
        response = self.client.post('/item/1', self.sample_form)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertContains(response, "class='simple-list'", count=1, status_code=200)

    def test_comment_form_no_user(self):
        ''' Tests posting a new comment without being logged in '''
        self.client.logout()
        response = self.client.post('/item/1', self.sample_form)
        self.assertContains(response, "class='no-content'", count=1, status_code=200)
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_invalid_item(self):
        ''' Tests posting a new comment on an invalid item '''
        response = self.client.post('/item/f56', self.sample_form)
        self.assertEqual(response.status_code, 404)
        self.assertIn('miscosas/content/not_found.html',
            [t.name for t in response.templates])

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

    def test_delete_comment(self):
        ''' Tests deleting a comment posted by the user '''
        self.client.post('/item/1', self.sample_form)
        self.assertEquals(Comment.objects.count(), 1)
        self.client.post('/item/1', {'action': 'delete', 'pk': 1})
        self.assertEquals(Comment.objects.count(), 0)

    def test_delete_not_own_comment(self):
        ''' Tests deleting comments made by other user '''
        Comment(
            title="aaa",
            content="aaa",
            user=self.other_user,
            item=Item.objects.get(pk=4)).save()
        self.assertEquals(Comment.objects.count(), 1)
        self.client.post('/item/4', {'action': 'delete', 'pk': 1})
        self.assertEquals(Comment.objects.count(), 1)

    def test_delete_comment_no_user(self):
        ''' Tests deleting a comment while not logged in '''
        self.client.post('/item/1', self.sample_form)
        self.assertEquals(Comment.objects.count(), 1)
        self.client.logout()
        self.client.post('/item/1', {'action': 'delete', 'pk': 1})
        self.assertEquals(Comment.objects.count(), 1)

    def test_delete_comment_wrong_item(self):
        ''' Tests deleting a comment posting on a different item '''
        self.client.post('/item/5', self.sample_form)
        self.assertEquals(Comment.objects.count(), 1)
        self.client.post('/item/1', {'action': 'delete', 'pk': 1})
        self.assertEquals(Comment.objects.count(), 1)


class TestPostVoteForm(TestCase):

    def setUp(self):
        ''' Set up some items so that votes can be added '''
        form = {'key': VALID_YOUTUBE_KEY, 'source': Config.YOUTUBE}
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
        self.assertEqual(self.item.upvote_count, 0)
        self.assertEqual(self.item.downvote_count, 0)
        self.assertEqual(self.user.profile.vote_count, 0)
        self.assertEqual(Vote.objects.count(), 0)

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
            'font_size': Config.LARGE_FONT,
        }

        response = self.client.post('/user/' + self.user.username, form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(username=self.user.username).profile.font_size, Config.LARGE_FONT)

    def test_change_theme(self):
        form = {
            'theme': Config.DARKMODE,
            'font_size': self.user.profile.font_size,
        }

        response = self.client.post('/user/' + self.user.username, form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(username=self.user.username).profile.theme, Config.DARKMODE)

    def test_post_wrong_user(self):
        form = {
            'theme': Config.DARKMODE,
            'font_size': Config.LARGE_FONT,
        }

        response = self.client.post('/user/' + self.other_user.username, form)
        self.assertEqual(response.status_code, 200)
        profile = User.objects.get(username=self.other_user.username).profile
        self.assertEqual(profile.font_size, Config.MEDIUM_FONT)
        self.assertEqual(profile.theme, Config.LIGHTMODE)


class TestPostFeedChoose(TestCase):

    def setUp(self):
        ''' Set up some feeds so that votes can be added '''
        form = {'key': VALID_YOUTUBE_KEY, 'source': Config.YOUTUBE}
        self.client.post('/feeds', form)
        form = {'key': VALID_LAST_FM_KEY, 'source': Config.LASTFM}
        self.client.post('/feeds', form)

    def test_unchoose_feed(self):
        ''' Tests form for unchoosing feed '''
        form = {'action': 'unchoose'}
        self.client.post('/feed/1', form)
        self.assertFalse(Feed.objects.get(pk=1).chosen)
        self.assertTrue(Feed.objects.get(pk=2).chosen)

        response = self.client.get('/')
        self.assertContains(response, "list-brief", 1)

    def test_rechoose_feed(self):
        form = {'action': 'unchoose'}
        self.client.post('/feed/1', form)
        form = {'key': VALID_YOUTUBE_KEY, 'source': Config.YOUTUBE}
        self.client.post('/feeds', form)

        self.assertTrue(Feed.objects.get(pk=1).chosen)
        self.assertTrue(Feed.objects.get(pk=2).chosen)

        response = self.client.get('/')
        self.assertContains(response, "list-brief", 2)
