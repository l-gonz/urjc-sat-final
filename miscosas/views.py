"""
Django views for app MisCosas
"""

from django.shortcuts import render, redirect, HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth import login, authenticate
from django.core.exceptions import ValidationError

from .models import *
from .forms import *
from .feedhandler import FEEDS_DATA


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
        try:
            key = request.POST['key']
            # TODO Send feed origin in form
            if FEEDS_DATA['YouTube'].load(key):
                return redirect(f'feed/{Feed.objects.get(key=key).pk}')
            else:
                return not_found_page(request)
        except KeyError:
            # Ignore wrong post attempts
            pass

    feeds = Feed.objects.all()
    form = FeedForm()
    context = {
        'title': 'Feeds | Mis cosas',
        'feed_list': feeds,
        'form': form,
    }
    return render(request, 'miscosas/content/feeds.html', context)


def feed_page(request: WSGIRequest, id: str):
    try:
        pk = int(id)
        feed = Feed.objects.get(pk=pk)
    except (Feed.DoesNotExist, ValueError):
        return not_found_page(request)

    context = {
        'title': f'{feed.title} | Mis cosas',
        'feed': feed,
        'item_list': feed.item_set.all(),
    }

    return render(request, 'miscosas/content/feed_page.html', context)


def item_page(request: WSGIRequest, id: str):
    try:
        pk = int(id)
        item = Item.objects.get(pk=pk)
    except (Item.DoesNotExist, ValueError):
        return not_found_page(request)

    if request.method == 'POST' and request.user.is_authenticated:
        try:
            if request.POST['action'] == 'comment':
                comment = Comment(
                    title=request.POST['title'],
                    content=request.POST['content'],
                    item=item,
                    user=request.user)
                comment.full_clean()
                comment.save()
            elif request.POST['action'] == 'vote':
                # read votes post form here
                pass
        except (KeyError, ValidationError):
            # Ignore wrong post attempts
            pass

    context = {
        'title': f'{item.title} | {item.feed.title} | Mis cosas',
        'item': item,
        'link': FEEDS_DATA[item.feed.origin].get_item_url(item.key),
        'comment_list': item.comment_set.all(),
        'form': CommentForm(),
    }
    return render(request, 'miscosas/content/item_page.html', context)


def users_page(request: WSGIRequest):
    return render(request, 'miscosas/content/users.html')


def user_page(request: WSGIRequest, id: str):
    return render(request, 'miscosas/content/user_page.html')


def about_page(request: WSGIRequest):
    return render(request, 'miscosas/content/about.html')


def not_found_page(request):
    return render(
        request,
        'miscosas/content/not_found.html',
        {'title': 'Page not found | Mis cosas'},
        status=404)
