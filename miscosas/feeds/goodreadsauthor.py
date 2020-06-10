#!/usr/bin/python3

from time import sleep
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from xml.etree import ElementTree
from urllib.request import urlopen
from urllib.parse import quote

from .feedparser import FeedParser, ParsingError


class GoodreadsHandler(ContentHandler):
    """Class to handle events fired by the SAX parser

    Fills in self.books with data from book items
    in a goodreads author book list.
    """

    ENTRY_TAGS = [
        'id',
        'title',
        'image_url',
        'description',
        'ratings_count',
    ]

    TITLE_TAG = 'name'

    ENTRY_TAG = 'book'
    ENTRY_CHILD_TAGS = [
        'authors',
        'work',
    ]

    def __init__(self):
        """Initialization of variables for the parser
        * in_content: reading target content (leaf strings)
        * content: target content being read
        * books: list of books from the author,
            each book is a dictionary (id, title, image_url, description)
        * current_entry: the information from the current book
        """
        self.in_content = False
        self.in_entry = False
        self.in_authors = False
        self.content = ""
        self.books = []
        self.current_entry = {}
        self.name = ""

    def startElement(self, name, attrs):
        self.in_content = (
            (self.in_entry and not self.in_authors and name in self.ENTRY_TAGS) or
            (not self.in_entry and name in self.TITLE_TAG)
        )
        if name == self.ENTRY_TAG:
            self.in_entry = True
        if name in self.ENTRY_CHILD_TAGS:
            self.in_authors = True

    def endElement(self, name):
        if self.in_entry and not self.in_authors and name in self.ENTRY_TAGS:
            self.current_entry[name] = self.content
        elif not self.in_entry and name in self.TITLE_TAG:
            self.name = self.content
        elif name == self.ENTRY_TAG:
            self.books.append(self.current_entry)
            self.current_entry = {}
            self.in_entry = False
        elif name in self.ENTRY_CHILD_TAGS:
            self.in_authors = False

        self.content = ""
        self.in_content = False

    def characters(self, chars):
        if self.in_content:
            self.content = self.content + chars


class GoodreadsAuthor(FeedParser):
    """Class to get books from a author in Goodreads.

    Uses Goodreads API to get a list of books from author name
    or author id
    """

    def __init__(self, stream):
        # Get books list from xml
        self.parser = make_parser()
        self.handler = GoodreadsHandler()
        self.parser.setContentHandler(self.handler)
        self.parser.parse(stream)

        # Remove books with less than 1000 reviews
        # as they are probably language variations
        try:
            self.books = [book for book in self.handler.books if int(book['ratings_count']) >= 1000]
        except KeyError:
            raise ParsingError("Missing expected tag")
        except ValueError:
            raise ParsingError("Could not parse ratings count")


        # Make sure all expected fields are filled
        if not self.handler.name:
            raise ParsingError("Feed has no title")
        if not self.books:
            raise ParsingError("Feed has no items")
        if any(not self.is_item_complete(item) for item in self.books):
            raise ParsingError("Some item is missing fields")

    def feed_title(self):
        return self.handler.name

    def items_data(self):
        items = []
        for book in self.books:
            items.append({
                'key': book['id'],
                'title': book['title'],
                'description': book['description'],
                'picture': book['image_url'],
            })
        return items

    def is_item_complete(self, item):
        ''' Checks if an individual item has all expected fields '''
        return (item.get('id') and
                item.get('title') and
                'description' in item and
                'image_url' in item)


def get_author_id(author_name: str, api_key: str):
    """Translates an author name into a Goodreads author id."""
    # Key is already an author id, not a name
    if author_name.isdigit():
        return {}, author_name

    url = "https://www.goodreads.com/api/author_url/{feed}?key={api_key}"
    url = str.format(url, feed=quote(author_name), api_key=api_key)
    stream = urlopen(url)

    tree = ElementTree.parse(stream)
    node = tree.find('author')
    if node:
        author_id = node.attrib['id']
    else:
        raise ParsingError("Key not found")

    # Goodreads API has a one request per second limit
    # Forcing sleep during 1 second to not risk losing
    # the developer key
    sleep(1)
    return {}, author_id