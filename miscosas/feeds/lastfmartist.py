#!/usr/bin/python3

from xml.sax.handler import ContentHandler
from xml.sax import make_parser


class LastFmHandler(ContentHandler):
    """Class to handle events fired by the SAX parser

    Fills in self.albums with data from albums
    in a Last.fm artist XML document.
    """

    ALBUM_TAGS = [
        'name',
        'image'
    ]

    def __init__(self):
        """Initialization of variables for the parser
        * in_content: reading target content (leaf strings)
        * content: target content being read
        * albums: list of albums in the artist,
            each album is a dictionary (name, image)
        * current_album: the information from the current entry
        """
        self.in_content = False
        self.in_artist = False
        self.content = ""
        self.albums = []
        self.current_album = {}
        self.name = ""

    def startElement(self, name, attrs):
        self.in_content = (name == 'name' or
                          (name == 'image' and attrs['size'] == 'extralarge'))
        if name == 'artist':
            self.in_artist = True

    def endElement(self, name):
        if self.in_content and name in self.ALBUM_TAGS:
            if self.in_artist:
                self.name = self.content
            else:
                self.current_album[name] = self.content
        if name == 'album':
            self.albums.append(self.current_album)
            self.current_album = {}
        if name == 'artist':
            self.in_artist = False

        self.content = ""
        self.in_content = False

    def characters(self, chars):
        if self.in_content:
            self.content = self.content + chars


class LastFmArtist():
    """Class to get videos in a YouTube channel.

    Extracts video info from the XML document for a YT channel.
    The list of videos found can be retrieved later by calling videos()
    """

    def __init__(self, stream):
        self.parser = make_parser()
        self.handler = LastFmHandler()
        self.parser.setContentHandler(self.handler)
        self.parser.parse(stream)

    def feed_title(self):
        return self.handler.name

    def items_data(self):
        items = []
        for album in self.handler.albums:
            items.append({
                'key': album['name'],
                'title': album['name'],
                'picture': album['image'],
            })
        return items
