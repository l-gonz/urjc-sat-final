"""
Django views for app MisCosas
"""

from django.shortcuts import render, redirect
from django.core.handlers.wsgi import WSGIRequest
from django.core.exceptions import ValidationError

from .models import Feed, Item, Comment, User
from .forms import FeedForm, CommentForm, ProfileForm
from .feeds.feedhandler import FEEDS_DATA


def index(request: WSGIRequest):
    context = {
        'title': 'Mis cosas',
        'feed_list': Feed.objects.all(),
        'item_list': Item.objects.all(),
        'form': FeedForm(),
    }
    return render(request, 'miscosas/content/index.html', context)


def feeds_page(request: WSGIRequest):
    if request.method == 'POST':
        form = FeedForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data['key']
            origin = form.cleaned_data['origin']
            if FEEDS_DATA[origin].load(key):
                return redirect(f'feed/{Feed.objects.get(key=key).pk}')
            else:
                return not_found_page(request)

    feeds = Feed.objects.all()
    form = FeedForm()
    context = {
        'title': 'Feeds | Mis cosas',
        'feed_list': feeds,
        'form': form,
    }
    return render(request, 'miscosas/content/feeds.html', context)


def feed_page(request: WSGIRequest, feed_id: str):
    try:
        pk = int(feed_id)
        feed = Feed.objects.get(pk=pk)
    except (Feed.DoesNotExist, ValueError):
        return not_found_page(request)

    context = {
        'title': f'{feed.title} | Mis cosas',
        'feed': feed,
        'item_list': feed.item_set.all(),
        'link': FEEDS_DATA[feed.origin].get_feed_url(feed.key),
    }

    return render(request, 'miscosas/content/feed_page.html', context)


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
            elif request.POST['action'] == 'upvote':
                item.downvotes.remove(request.user)
                item.upvotes.add(request.user)
            elif request.POST['action'] == 'downvote':
                item.upvotes.remove(request.user)
                item.downvotes.add(request.user)
        except (KeyError, ValidationError):
            # Ignore wrong post attempts
            pass

    context = {
        'title': f'{item.title} | {item.feed.title} | Mis cosas',
        'item': item,
        'link': FEEDS_DATA[item.feed.origin].get_item_url(item.feed.key, item.key),
        'comment_list': item.comments.all(),
        'form': CommentForm(),
    }
    return render(request, 'miscosas/content/item_page.html', context)


def users_page(request: WSGIRequest):
    context = {
        'title': 'Users | Mis cosas',
        'user_list': User.objects.all().select_related('profile'),
    }
    return render(request, 'miscosas/content/users.html', context)


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
        'upvoted_item_list': owner.upvotes.all(),
        'downvoted_item_list': owner.downvotes.all(),
        'commented_item_list': Item.objects.filter(comments__user=owner).distinct(),
        'form': ProfileForm(instance=owner.profile),
        'user_match': user_match,
    }
    return render(request, 'miscosas/content/user_page.html', context)


def about_page(request: WSGIRequest):
    return render(request, 'miscosas/content/about.html')


def not_found_page(request):
    return render(
        request,
        'miscosas/content/not_found.html',
        {'title': 'Page not found | Mis cosas'},
        status=404)
