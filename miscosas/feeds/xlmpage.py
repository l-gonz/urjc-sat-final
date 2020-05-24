from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from collections.abc import Iterable

from django.http.response import HttpResponse, Http404
from django.core.handlers.wsgi import WSGIRequest

from miscosas.models import Feed, Item, Comment, User
from .feedhandler import FEEDS_DATA

def render_document(request: WSGIRequest, context: dict, format: str) -> HttpResponse:
    if format == 'xml':
        return render_xml(request, context)
    elif format == 'json':
        return render_json(request, context)
    else:
        return Http404("Error")

def render_xml(request: WSGIRequest, context: dict):
    xml = Element('page')
    SubElement(xml, 'link', href=request.build_absolute_uri(request.path))
    for name in context:
        if name == 'title':
            SubElement(xml, name).text = context[name]
        elif isinstance(context[name], Iterable):
            if any(isinstance(i, Feed) for i in context[name]):
                feeds = SubElement(xml, 'feeds', name=name)
                feeds.extend([feed_xml(request, feed, False) for feed in context[name]])
            elif any(isinstance(i, Item) for i in context[name]):
                items = SubElement(xml, 'items', {'name': name})
                items.extend([item_xml(request, item, False) for item in context[name]])
            elif any(isinstance(i, User) for i in context[name]):
                xml.extend([user_xml(request, user, False) for user in context[name]])
        elif isinstance(context[name], Feed):
            xml.append(feed_xml(request, context[name], True))
        elif isinstance(context[name], Item):
            xml.append(item_xml(request, context[name], True))
        elif isinstance(context[name], User):
            xml.append(user_xml(request, context[name], True))
    return HttpResponse(prettify(xml), content_type='text/xml')

def render_json(request: WSGIRequest, context: dict):
    json = ''
    return HttpResponse(json, content_type='text/json')

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def feed_xml(request: WSGIRequest, feed: Feed, detailed: bool):
    element = Element('feed')
    SubElement(element, 'title').text = feed.title
    SubElement(element, 'source').text = feed.source
    if detailed:
        SubElement(element, 'link', href=FEEDS_DATA[feed.source].get_feed_url(feed.key))
        SubElement(element, 'chosen').text = str(feed.chosen)
    else:
        SubElement(element, 'link', href=request.build_absolute_uri('/feed/' + str(feed.pk)))
    return element

def item_xml(request: WSGIRequest, item: Item, detailed: bool):
    element = Element('item')
    SubElement(element, 'title').text = item.title
    if detailed:
        SubElement(element, 'link', href=FEEDS_DATA[item.feed.source].get_feed_url(item.key))
        SubElement(element, 'description').text = item.description
        SubElement(element, 'image', src=item.picture)
        element.extend([comment_xml(comment) for comment in item.comments.all().order_by('-date')[:20]])
    else:
        SubElement(element, 'link', href=request.build_absolute_uri('/item/' + str(item.pk)))
    SubElement(element, 'upvotes').text = str(item.upvote_count)
    SubElement(element, 'downvotes').text = str(item.downvote_count)
    element.append(feed_xml(request, item.feed, False))
    return element

def comment_xml(comment: Comment):
    element = Element('comment')
    SubElement(element, 'title').text = comment.title
    SubElement(element, 'content').text = comment.content
    SubElement(element, 'date').text = str(comment.date)
    return element

def user_xml(request: WSGIRequest, user: User, detailed: bool):
    element = Element('user')
    SubElement(element, 'name').text = user.username
    if not detailed:
        SubElement(element, 'link', href=request.build_absolute_uri('/user/' + user.username))
    return element
