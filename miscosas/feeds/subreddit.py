#!/usr/bin/python3

import re
from xml.sax.handler import ContentHandler
from xml.sax import make_parser

from .feedparser import FeedParser, ParsingError


class RedditHandler(ContentHandler):
    """Class to handle events fired by the SAX parser

    Fills in self.news with data from news items
    in a subreddit RSS feed.
    """

    ENTRY_TAGS = [
        'content',
        'id',
        'title',
    ]

    FEED_TAGS = [
        'title'
    ]

    ENTRY_TAG = 'entry'

    def __init__(self):
        """Initialization of variables for the parser
        * in_content: reading target content (leaf strings)
        * content: target content being read
        * news: list of news in the subreddit,
            each news is a dictionary (title, id, content)
        * current_entry: the information from the current news
        """
        self.in_content = False
        self.in_entry = False
        self.content = ""
        self.news = []
        self.current_entry = {}
        self.name = ""

    def startElement(self, name, attrs):
        self.in_content = (
            (self.in_entry and name in self.ENTRY_TAGS) or
            (not self.in_entry and name in self.FEED_TAGS))
        if name == self.ENTRY_TAG:
            self.in_entry = True

    def endElement(self, name):
        if self.in_entry and name in self.ENTRY_TAGS:
            self.current_entry[name] = self.content
        elif not self.in_entry and name in self.FEED_TAGS:
            self.name = self.content
        elif name == self.ENTRY_TAG:
            self.news.append(self.current_entry)
            self.current_entry = {}
            self.in_entry = False

        self.content = ""
        self.in_content = False

    def characters(self, chars):
        if self.in_content:
            self.content = self.content + chars


class Subreddit(FeedParser):
    """Class to get news from a subreddit.

    Extracts item info from the XML document for a reddit rss feed.
    """

    def __init__(self, stream):
        self.parser = make_parser()
        self.handler = RedditHandler()
        self.parser.setContentHandler(self.handler)
        self.parser.parse(stream)

        # Make sure all expected fields are filled
        if not self.handler.name:
            raise ParsingError("Feed has no title")
        if not self.handler.news:
            raise ParsingError("Feed has no items")
        if any(not self.is_item_complete(item) for item in self.handler.news):
            raise ParsingError("Some item is missing fields")

    def feed_title(self):
        name = self.handler.name
        if name.startswith('/r/'):
            return name.split('/')[2]
        else:
            return name

    def items_data(self):
        items = []
        for news in self.handler.news:
            items.append({
                'key': news['id'].split('_')[1],
                'title': news['title'],
                'description': self.format_content(news['content']),
            })
        return items

    def is_item_complete(self, item):
        ''' Checks if an individual item has all expected fields '''
        return (item.get('id') and
                item.get('title') and
                item.get('content'))

    def format_content(self, content: str):
        ''' Removes [link] and [comments] links from the end '''
        pos = content.find('&#32; submitted by &#32')
        for _ in [1, 2]:
            span_start = content.find("<span>", pos)
            span_end = content.find("</span>", span_start)
            content = content[:span_start] + content[span_end:]
        return content