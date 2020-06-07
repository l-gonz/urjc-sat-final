import sys
from urllib.request import urlopen
from urllib.parse import quote
from urllib.error import URLError, HTTPError

from project.secretkeys import LAST_FM_API_KEY
from miscosas.apps import MisCosasConfig as Config
from .feedparser import ParsingError
from .ytchannel import YTChannel
from .lastfmartist import LastFmArtist
from .subreddit import Subreddit
from .flickrtag import FlickrTag


class FeedData:
    ''' Stores information from a feed source. '''

    def __init__(self,
                 feed_url,
                 item_url,
                 data_url,
                 source,
                 feed_parser,
                 api_key=""):
        ''' Urls for accessing the feed.

        Urls need {feed} or {item} fields for formatting. '''

        self._feed_url = feed_url
        self._item_url = item_url
        self._data_url = data_url
        self._source = source
        self._parser = feed_parser
        self._api_key = api_key

    def get_feed_url(self, feed_key):
        ''' Returns the url of the feed with the given key '''
        return str.format(self._feed_url, feed=quote(feed_key))

    def get_item_url(self, feed_key, item_key):
        ''' Returns the url of the item with the given key '''
        return str.format(self._item_url, feed=quote(feed_key), item=quote(item_key))

    def get_data_url(self, feed_key):
        ''' Returns the url of the XML or JSON file
        with the data from the feed with the given key '''
        return str.format(self._data_url, feed=quote(feed_key), api_key=self._api_key)

    def load(self, feed_key):
        ''' Load the info from a new or existing feed '''
        from miscosas.models import Feed, Item

        url = self.get_data_url(feed_key)
        try:
            xml_stream = urlopen(url)
        except (URLError, HTTPError) as e:
            return False

        # Wrong reddit names redirect to a search rss
        if self._source == Config.REDDIT and xml_stream.geturl() != url:
            return False

        try:
            parser = self._parser(xml_stream)
        except ParsingError as e:
            print("ParsingError: " + str(e), end='\n', file=sys.stderr)
            return False

        feed, _ = Feed.objects.update_or_create(
            key=feed_key,
            source=self._source,
            defaults={
                'title': parser.feed_title(),
                'chosen': True,
            })

        for item in parser.items_data():
            Item.objects.update_or_create(
                key=item['key'],
                defaults={
                    **item,
                    'feed': feed,
                })

        return True


YOUTUBE_FEED = FeedData(
    "https://www.youtube.com/channel/{feed}",
    "https://www.youtube.com/watch?v={item}",
    "http://www.youtube.com/feeds/videos.xml?channel_id={feed}",
    Config.YOUTUBE,
    YTChannel)

LAST_FM_FEED = FeedData(
    "https://www.last.fm/music/{feed}",
    "https://www.last.fm/music/{feed}/{item}",
    "http://ws.audioscrobbler.com/2.0/?method=artist.gettopalbums&artist={feed}&limit=15&api_key={api_key}",
    Config.LASTFM,
    LastFmArtist,
    LAST_FM_API_KEY)

REDDIT_FEED = FeedData(
    "https://www.reddit.com/r/{feed}",
    "https://www.reddit.com/r/{feed}/comments/{item}",
    "https://www.reddit.com/r/{feed}.rss",
    Config.REDDIT,
    Subreddit)

FLICKR_FEED = FeedData(
    "https://www.flickr.com/search/?tags={feed}",
    "https://www.flickr.com/photos/{item}/",
    "https://www.flickr.com/services/feeds/photos_public.gne?tags={feed}",
    Config.FLICKR,
    FlickrTag)

FEEDS_DATA = {
    Config.YOUTUBE: YOUTUBE_FEED,
    Config.LASTFM: LAST_FM_FEED,
    Config.REDDIT: REDDIT_FEED,
    Config.FLICKR: FLICKR_FEED,
}
