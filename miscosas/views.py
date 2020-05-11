"""
Django views for app MisCosas
"""

from django.shortcuts import render, redirect, HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth import login, authenticate

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


def feeds(request: WSGIRequest):
    if request.method == 'POST':
        try:
            key = request.POST['key']
            # TODO Send feed origin in form
            if FEEDS_DATA['YouTube'].load(key):
                return redirect(f'feed/{Feed.objects.get(key=key).pk}')
            else:
                return not_found(request)
        except KeyError:
            pass

    feeds = Feed.objects.all()
    form = FeedForm()
    context = {
        'title': 'Feeds | Mis cosas',
        'feed_list': feeds,
        'form': form,
    }
    return render(request, 'miscosas/content/feeds.html', context)


def feed(request: WSGIRequest, id: str):
    try:
        pk = int(id)
        feed = Feed.objects.get(pk=pk)
    except (Feed.DoesNotExist, ValueError):
        return not_found(request)

    context = {
        'title': f'{feed.title} | Mis cosas',
        'feed': feed,
        'item_list': feed.item_set.all(),
    }

    return render(request, 'miscosas/content/feed_page.html', context)


def item(request: WSGIRequest, id: str):
    try:
        pk = int(id)
        item = Item.objects.get(pk=pk)
    except (Item.DoesNotExist, ValueError):
        return not_found(request)

    context = {
        'title': f'{item.title} | {item.feed.title} | Mis cosas',
        'item': item,
        'link': FEEDS_DATA[item.feed.origin].get_item_url(item.key),
    }
    return render(request, 'miscosas/content/item_page.html', context)


def users(request: WSGIRequest):
    return render(request, 'miscosas/content/users.html')


def user(request: WSGIRequest, id: str):
    return render(request, 'miscosas/content/user_page.html')


def about(request: WSGIRequest):
    return render(request, 'miscosas/content/about.html')


def not_found(request):
    return render(
        request,
        'miscosas/content/not_found.html',
        {'title': 'Page not found | Mis cosas'},
        status=404)
