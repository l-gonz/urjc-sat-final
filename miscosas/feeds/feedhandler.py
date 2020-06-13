from urllib.request import urlopen, Request
from urllib.parse import quote

from project.secretkeys import LAST_FM_API_KEY, GOODREADS_API_KEY, SPOTIFY_API_KEY
from miscosas.apps import MisCosasConfig as Config
from .ytchannel import YTChannel
from .lastfmartist import LastFmArtist
from .subreddit import Subreddit
from .flickrtag import FlickrTag
from .goodreadsauthor import GoodreadsAuthor, get_author_id
from .spotifyartist import SpotifyArtist, get_artist_id


class FeedData:
    """Stores information from a feed source."""

    def __init__(self,
                 feed_url,
                 item_url,
                 data_url,
                 source,
                 feed_parser,
                 icon,
                 api_key="",
                 pre_load=None):
        """
        Initializes the required data to access the feed.

        Parameters:
        ----------------
        feed_url : str
            External link for a feed, will format {feed}
        item_url : str
            External link for an item, will format {feed} and {item}
        data_url : str
            Feed source API url to get the document to parse,
            will format {feed} and {api_key}
        source : str
            The identifier for the source of the data
        feed_parser : FeedParser
            An implementation of FeedParser to get the feed
            data from the the document
        icon : str
            A link to the feed source icon
        api_key : str
            An optional API key if the source API requires it
        pre_load: func
            An optional function that is executed before the
            document with the data is requested and parsed
        """

        self._feed_url = feed_url
        self._item_url = item_url
        self._data_url = data_url
        self._source = source
        self._parser = feed_parser
        self.icon = icon
        self._api_key = api_key
        self._pre_load = pre_load

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
        """Load the info from a new or existing feed.

        Returns a tuple (feed, exception)"""

        headers = {}
        if self._pre_load:
            headers, feed_key = self._pre_load(feed_key, self._api_key)

        url = self.get_data_url(feed_key)
        request = Request(url, headers=headers)
        response = urlopen(request)

        return self._parse(response, feed_key)

    def _parse(self, response, feed_key):
        """Parses an HTTPResponse into a Feed with Items."""
        from miscosas.models import Feed, Item

        parser = self._parser(response)

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

        return feed


YOUTUBE_FEED = FeedData(
    "https://www.youtube.com/channel/{feed}",
    "https://www.youtube.com/watch?v={item}",
    "http://www.youtube.com/feeds/videos.xml?channel_id={feed}",
    Config.YOUTUBE,
    YTChannel,
    "https://s.ytimg.com/yts/img/favicon_144-vfliLAfaB.png")

LAST_FM_FEED = FeedData(
    "https://www.last.fm/music/{feed}",
    "https://www.last.fm/music/{feed}/{item}",
    "http://ws.audioscrobbler.com/2.0/?method=artist.gettopalbums&artist={feed}&limit=15&api_key={api_key}",
    Config.LASTFM,
    LastFmArtist,
    "https://www.last.fm/static/images/logo_static.adb61955725c.png",
    LAST_FM_API_KEY)

REDDIT_FEED = FeedData(
    "https://www.reddit.com/r/{feed}",
    "https://www.reddit.com/r/{feed}/comments/{item}",
    "https://www.reddit.com/r/{feed}.rss",
    Config.REDDIT,
    Subreddit,
    "http://t1.gstatic.com/images?q=tbn:ANd9GcThsotATP9ktYH_-oqNK6lYSI2USCxC-9nhbqScnKqvWFyxmL64")

FLICKR_FEED = FeedData(
    "https://www.flickr.com/search/?tags={feed}",
    "https://www.flickr.com/photos/{item}/",
    "https://www.flickr.com/services/feeds/photos_public.gne?tags={feed}",
    Config.FLICKR,
    FlickrTag,
    "https://cdn.kustomerhostedcontent.com/media/5aecd7338a0607779d1ec9cc/966e09a41a33f89fe18f2ab227336f09.png")

GOODREADS_FEED = FeedData(
    "https://www.goodreads.com/author/show/{feed}",
    "https://www.goodreads.com/book/show/{item}",
    "https://www.goodreads.com/author/list.xml?id={feed}&key={api_key}",
    Config.GOODREADS,
    GoodreadsAuthor,
    "http://d.gr-assets.com/misc/1454549143-1454549143_goodreads_misc.png",
    GOODREADS_API_KEY,
    get_author_id)

SPOTIFY_FEED = FeedData(
    "https://open.spotify.com/artist/{feed}",
    "https://open.spotify.com/track/{item}",
    "https://api.spotify.com/v1/artists/{feed}/top-tracks?country=ES",
    Config.SPOTIFY,
    SpotifyArtist,
    "https://pluspng.com/img-png/spotify-logo-png-open-2000.png",
    SPOTIFY_API_KEY,
    get_artist_id)

FEEDS_DATA = {
    Config.YOUTUBE: YOUTUBE_FEED,
    Config.LASTFM: LAST_FM_FEED,
    Config.REDDIT: REDDIT_FEED,
    Config.FLICKR: FLICKR_FEED,
    Config.GOODREADS: GOODREADS_FEED,
    Config.SPOTIFY: SPOTIFY_FEED,
}
