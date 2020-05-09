"""
Django views for app MisCosas
"""

from django.shortcuts import render, redirect, HttpResponse
from django.core.handlers.wsgi import WSGIRequest

from .models import Feed, Item
from .forms import FeedForm
from .feedhandler import get_youtube_feed


def index(request: WSGIRequest):
    feeds = Feed.objects.all()
    items = Item.objects.all()
    form = FeedForm()
    context = {
        'title': 'Mis cosas',
        'feed_list': feeds,
        'item_list': items,
        'form': form,
    }
    return render(request, 'miscosas/content/index.html', context)


def feeds(request: WSGIRequest):
    if request.method == 'POST':
        try:
            key = request.POST['key']
            if get_youtube_feed(key):
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

    items = Item.objects.filter(feed=feed)
    context = {
        'title': f'{feed.title} | Mis cosas',
        'item_list': items,
    }

    return render(request, 'miscosas/content/feed_page.html', context)


def items(request: WSGIRequest):
    return HttpResponse("Página de items")


def item(request: WSGIRequest, id: str):
    return HttpResponse("Página de item")


def users(request: WSGIRequest):
    return HttpResponse("Página de usuarios")


def user(request: WSGIRequest, id: str):
    return HttpResponse("Página de usuario")


def about(request: WSGIRequest):
    return HttpResponse("Página de información")


def not_found(request):
    return render(request, 'miscosas/content/not_found.html', status=404)
