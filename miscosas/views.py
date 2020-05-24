"""
Django views for app MisCosas
"""

from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.core.exceptions import ValidationError
from django.db.models import Q, F
from django.db.models.functions import Length

from .models import Feed, Item, Comment, User, Vote
from .forms import FeedForm, CommentForm, ProfileForm
from .feeds.feedhandler import FEEDS_DATA
from .feeds.xlmpage import render_document


def index(request: WSGIRequest):
    # Selects the items that have been voted the most
    # from all the items that have been voted
    items = list(Item.objects.filter(votes__isnull=False).distinct())
    items.sort(key=lambda i: i.upvote_count, reverse=True)
    items.sort(key=lambda i: i.upvote_count - i.downvote_count, reverse=True)

    latest_votes = []
    if request.user.is_authenticated:
        latest_votes = [v.item for v in Vote.objects.filter(user=request.user).order_by('-date')]

    context = {
        'title': 'Mis cosas',
        'popular_items': items[:10],
        'chosen_feeds': Feed.objects.filter(chosen=True),
        'user_latest_votes': latest_votes[:5],
        'form': FeedForm(),
    }

    return render_or_document(request, 'miscosas/content/index.html', context)


def feeds_page(request: WSGIRequest):
    if request.method == 'POST':
        form = FeedForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['key']
            source = form.cleaned_data['source']
            if FEEDS_DATA[source].load(key):
                return redirect(f'feed/{Feed.objects.get(key=key).pk}')
            else:
                return not_found_page(request)

    context = {
        'title': 'Feeds | Mis cosas',
        'all_feeds': Feed.objects.all(),
        'form': FeedForm(),
    }
    return render_or_document(request, 'miscosas/content/feeds.html', context)


def feed_page(request: WSGIRequest, feed_id: str):
    try:
        pk = int(feed_id)
        feed = Feed.objects.get(pk=pk)
    except (Feed.DoesNotExist, ValueError):
        return not_found_page(request)

    if request.method == 'POST':
        try:
            if request.POST['action'] == 'unchoose':
                feed.chosen = False
                feed.save()
        except (KeyError, ValidationError):
            # Ignore wrong post attempts
            pass

    context = {
        'title': f'{feed.title} | Mis cosas',
        'feed': feed,
        'item_list': feed.items.all(),
        'link': FEEDS_DATA[feed.source].get_feed_url(feed.key),
    }

    return render_or_document(request, 'miscosas/content/feed_page.html', context)


def item_page(request: WSGIRequest, item_id: str):
    try:
        pk = int(item_id)
        item = Item.objects.get(pk=pk)
    except (Item.DoesNotExist, ValueError):
        return not_found_page(request)

    if request.method == 'POST' and request.user.is_authenticated:
        try:
            if request.POST['action'] == 'comment':
                form = CommentForm(request.POST)
                if form.is_valid():
                    comment = Comment(
                        title=request.POST['title'],
                        content=request.POST['content'],
                        item=item,
                        user=request.user)
                    comment.full_clean()
                    comment.save()
            elif request.POST['action'] == 'upvote' or request.POST['action'] == 'downvote':
                positive = request.POST['action'] == 'upvote'
                Vote.objects.filter(item=item, user=request.user, positive=(not positive)).delete()
                try:
                    Vote.objects.get(item=item, user=request.user)
                except Vote.DoesNotExist:
                    Vote(positive=positive, user=request.user, item=item).save()
            path = request.POST['path']
            return redirect(path)
        except (KeyError, ValidationError):
            # Ignore wrong post attempts
            pass

    context = {
        'title': f'{item.title} | {item.feed.title} | Mis cosas',
        'item': item,
        'link': FEEDS_DATA[item.feed.source].get_item_url(item.feed.key, item.key),
        'comment_list': item.comments.all(),
        'form': CommentForm(),
    }
    return render_or_document(request, 'miscosas/content/item_page.html', context)


def users_page(request: WSGIRequest):
    context = {
        'title': 'Users | Mis cosas',
        'user_list': User.objects.all().select_related('profile'),
    }
    return render_or_document(request, 'miscosas/content/users.html', context)


def user_page(request: WSGIRequest, username: str):
    try:
        owner = User.objects.get(username=username)
    except (User.DoesNotExist, ValueError):
        return not_found_page(request)

    user_match = request.user.is_authenticated and owner.username == request.user.username

    if request.method == 'POST' and user_match:
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()

    #TODO Show error if profile.picture image does not exist

    context = {
        'title': f'{owner.username} | Mis cosas',
        'owner': owner,
        'upvoted_item_list': Item.objects.filter(votes__user=owner, votes__positive=True),
        'downvoted_item_list': Item.objects.filter(votes__user=owner, votes__positive=False),
        'commented_item_list': Item.objects.filter(comments__user=owner).distinct(),
        'form': ProfileForm(instance=owner.profile),
        'user_match': user_match,
    }
    return render_or_document(request, 'miscosas/content/user_page.html', context)


def about_page(request: WSGIRequest):
    context = {'title': 'About | Mis cosas'}
    return render(request, 'miscosas/content/about.html', context)


def not_found_page(request):
    return render(
        request,
        'miscosas/content/not_found.html',
        {'title': 'Page not found | Mis cosas'},
        status=404)


def render_or_document(request, template, context):
    ''' Renders the response in the requested format '''
    if request.GET.get('format'):
        return render_document(request, context, request.GET['format'])
    return render(request, template, context)
