#!/usr/bin/python3

from xml.sax.handler import ContentHandler
from xml.sax import make_parser

from .feedparser import FeedParser, ParsingError


class FlickrHandler(ContentHandler):
    """Class to handle events fired by the SAX parser

    Fills in self.photos with data from photo items
    with a tag in Flickr.
    """

    ENTRY_TAGS = [
        'content',
        'title',
    ]

    ENTRY_ARGS = {
        'link': 'href',
    }

    FEED_TAGS = [
        'title'
    ]

    ENTRY_TAG = 'entry'

    def __init__(self):
        """Initialization of variables for the parser
        * in_content: reading target content (leaf strings)
        * content: target content being read
        * photos: list of photos in the subreddit,
            each photo is a dictionary (title, content, link)
        * current_entry: the information from the current photo
        """
        self.in_content = False
        self.in_entry = False
        self.content = ""
        self.photos = []
        self.current_entry = {}
        self.name = ""

    def startElement(self, name, attrs):
        self.in_content = (
            (self.in_entry and name in self.ENTRY_TAGS) or
            (self.in_entry and name in self.ENTRY_ARGS) or
            (not self.in_entry and name in self.FEED_TAGS))
        if name == self.ENTRY_TAG:
            self.in_entry = True
        if self.in_entry and name in self.ENTRY_ARGS:
            if attrs['rel'] == 'alternate':
                self.current_entry[name] = attrs[self.ENTRY_ARGS[name]]

    def endElement(self, name):
        if self.in_entry and name in self.ENTRY_TAGS:
            self.current_entry[name] = self.content
        elif not self.in_entry and name in self.FEED_TAGS:
            self.name = self.content
        elif name == self.ENTRY_TAG:
            self.photos.append(self.current_entry)
            self.current_entry = {}
            self.in_entry = False

        self.content = ""
        self.in_content = False

    def characters(self, chars):
        if self.in_content:
            self.content = self.content + chars


class FlickrTag(FeedParser):
    """Class to get photos from a tag in Flickr.

    Extracts item info from the XML document for a Flickr tag rss feed.
    """

    def __init__(self, stream):
        self.parser = make_parser()
        self.handler = FlickrHandler()
        self.parser.setContentHandler(self.handler)
        self.parser.parse(stream)

        # Make sure all expected fields are filled
        if not self.handler.name:
            raise ParsingError("Feed has no title")
        if not self.handler.photos:
            raise ParsingError("Feed has no items")
        if any(not self.is_item_complete(item) for item in self.handler.photos):
            raise ParsingError("Some item is missing fields")

    def feed_title(self):
        return self.handler.name

    def items_data(self):
        items = []
        for photo in self.handler.photos:
            items.append({
                'key': photo['link']
                    .replace("https://www.flickr.com/photos/", "")[:-1],
                'title': photo['title'],
                'description': photo['content'],
            })
        return items

    def is_item_complete(self, item):
        ''' Checks if an individual item has all expected fields '''
        return (item.get('link') and
                item.get('title') and
                item.get('content'))