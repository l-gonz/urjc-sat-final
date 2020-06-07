#!/usr/bin/python3

from xml.sax.handler import ContentHandler
from xml.sax import make_parser

from .feedparser import FeedParser


class YTHandler(ContentHandler):
    """Class to handle events fired by the SAX parser

    Fills in self.videos with data from videos
    in a YT channel XML document.
    """

    CONTENT_ELEMENTS = [
        'yt:videoId',
        'media:title',
        'published',
        'media:description',
    ]

    ATTR_ELEMENTS = {
        'link': 'href',
        'media:thumbnail': 'url'
    }

    def __init__(self):
        """Initialization of variables for the parser
        * inContent: reading target content (leaf strings)
        * content: target content being readed
        * videos: list of videos (<entry> elements) in the channel,
            each video is a dictionary
        * current_video: the information from the current <entry>
        """
        self.inContent = False
        self.content = ""
        self.videos = []
        self.current_video = {}
        self.channel_name = ""

    def startElement(self, name, attrs):
        self.inContent = (name in self.CONTENT_ELEMENTS or
                          name == 'name' or name == 'uri')
        if name in self.ATTR_ELEMENTS:
            self.current_video[name] = attrs.get(self.ATTR_ELEMENTS[name])

    def endElement(self, name):
        if name == 'entry':
            self.videos.append(self.current_video)
            self.current_video = {}
        elif name == 'name' and self.channel_name == "":
            self.channel_name = self.content
        elif name in self.CONTENT_ELEMENTS:
            self.current_video[name] = self.content

        self.content = ""
        self.inContent = False

    def characters(self, chars):
        if self.inContent:
            self.content = self.content + chars


class YTChannel(FeedParser):
    """Class to get videos in a YouTube channel.

    Extracts video info from the XML document for a YT channel.
    """

    def __init__(self, stream):
        self.parser = make_parser()
        self.handler = YTHandler()
        self.parser.setContentHandler(self.handler)
        self.parser.parse(stream)

    def feed_title(self):
        return self.handler.channel_name

    def items_data(self):
        items = []
        for video in self.handler.videos:
            items.append({
                'key': video['yt:videoId'],
                'title': video['media:title'],
                'description': video['media:description'],
                'picture': video['media:thumbnail'],
            })
        return items
