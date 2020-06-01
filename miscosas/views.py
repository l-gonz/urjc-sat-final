"""
Django views for app MisCosas
"""

from django.shortcuts import render, redirect, HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet

from .models import Feed, Item, Comment, User, Vote
from .forms import FeedForm, CommentForm, ProfileForm
from .feeds.feedhandler import FEEDS_DATA
from .feeds.serializepage import render_document


ENTRIES_PER_PAGE = 10


def index(request: WSGIRequest):
    # Selects the items that have been voted the most
    # from all the items that have been voted
    items = list(Item.objects.filter(votes__isnull=False))
    items = [item for item in items if item.upvote_count > 0]
    items.sort(key=lambda i: i.upvote_count, reverse=True)
    items.sort(key=lambda i: i.upvote_count - i.downvote_count, reverse=True)

    latest_votes = []
    if request.user.is_authenticated:
        latest_votes = [v.item for v in Vote.objects.filter(user=request.user).order_by('-date')]

    context = {
        'popular_items': items[:ENTRIES_PER_PAGE],
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

    feeds = Feed.objects.all()
    pages = pagination(request, feeds)

    context = {
        'all_feeds': pages['set'],
        'form': FeedForm(),
        'pages': pages['pages'],
        'current_page': pages['current_page'],
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

    pages = pagination(request, feed.items.all())

    context = {
        'feed': feed,
        'item_list': pages['set'],
        'link': FEEDS_DATA[feed.source].get_feed_url(feed.key),
        'pages': pages['pages'],
        'current_page': pages['current_page'],
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
                try:
                    vote = Vote.objects.get(item=item, user=request.user)
                    old_state = vote.positive;
                    vote.delete()
                    if old_state != positive:
                        Vote(positive=positive, user=request.user, item=item).save()
                except Vote.DoesNotExist:
                    Vote(positive=positive, user=request.user, item=item).save()
            path = request.POST['path']
            return redirect(path)
        except (KeyError, ValidationError):
            # Ignore wrong post attempts
            pass

    comments = item.comments.all().order_by('-date')
    pages = pagination(request, comments)

    context = {
        'item': item,
        'link': FEEDS_DATA[item.feed.source].get_item_url(item.feed.key, item.key),
        'comment_list': pages['set'],
        'form': CommentForm(),
        'pages': pages['pages'],
        'current_page': pages['current_page'],
    }
    return render_or_document(request, 'miscosas/content/item_page.html', context)


def users_page(request: WSGIRequest):
    users = User.objects.all().select_related('profile')
    pages = pagination(request, users)

    context = {
        'user_list': pages['set'],
        'pages': pages['pages'],
        'current_page': pages['current_page'],
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

    context = {
        'owner': owner,
        'upvoted_item_list': Item.objects.filter(votes__user=owner, votes__positive=True),
        'downvoted_item_list': Item.objects.filter(votes__user=owner, votes__positive=False),
        'commented_item_list': Item.objects.filter(comments__user=owner).distinct(),
        'form': ProfileForm(instance=owner.profile),
        'user_match': user_match,
    }
    return render_or_document(request, 'miscosas/content/user_page.html', context)


def about_page(request: WSGIRequest):
    return render(request, 'miscosas/content/about.html')


def not_found_page(request: WSGIRequest):
    return render(request, 'miscosas/content/not_found.html', status=404)


def render_or_document(request: WSGIRequest, template: str, context: dict):
    ''' Renders the response in the requested format '''
    context['documents'] = True
    if request.GET.get('format'):
        return render_document(request, context, request.GET['format'])
    return render(request, template, context)


def pagination(request: WSGIRequest, set: QuerySet):
    ''' Divides the entries in a query set in pages

    Returns a dictionary with data for the context '''
    pages = range(1, set.count() // ENTRIES_PER_PAGE + 2)
    if len(set) % 10 == 0 and len(pages) > 1:
        pages = pages[:-1]
    try:
        current_page = int(request.GET.get('page', 1))
    except ValueError:
        current_page = 1
    item_i = ENTRIES_PER_PAGE * (current_page - 1)
    item_f = item_i + ENTRIES_PER_PAGE

    return {
        'set': set[item_i:item_f],
        'pages': pages,
        'current_page': current_page,
    }
