import urllib

from miscosas.models import Feed, Item
from miscosas.apps import MisCosasConfig
from .ytchannel import YTChannel
from .lastfmartist import LastFmArtist


class FeedData():
    ''' Stores information from a feed origin. '''

    def __init__(self, name, feed_url, item_url, data_url, icon_src, load_function):
        ''' Name and urls for accessing the feed.

        Urls need a {key} field for formatting. '''

        self.name = name
        self.feed_url = feed_url
        self.item_url = item_url
        self.data_url = data_url
        self.icon_src = icon_src
        self.load = load_function

    def get_feed_url(self, feed_key):
        ''' Returns the url of the feed with the given key '''
        return str.format(self.feed_url, feed=feed_key)

    def get_item_url(self, feed_key, item_key):
        ''' Returns the url of the item with the given key '''
        return str.format(self.item_url, feed=feed_key, item=item_key)

    def get_data_url(self, feed_key):
        ''' Returns the url of the XML or JSON file
        with the data from the feed with the given key '''
        return str.format(self.data_url, feed=feed_key)

    def load_feed(self, feed_key):
        ''' Load the info from a new or existing feed '''
        self.load(feed_key)


def load_youtube_feed(feed_key: str):
    ''' Adds a new feed from YouTube to the database,
    downloading the data and making items from it'''

    url = YOUTUBE_FEED.data_url.format(feed=feed_key)
    try:
        xml_stream = urllib.request.urlopen(url)
    except urllib.error.HTTPError:
        return False

    channel = YTChannel(xml_stream)
    feed, _ = Feed.objects.get_or_create(
        key=feed_key,
        origin=YOUTUBE_FEED.name,
        defaults={
            'title': channel.name(),
        })

    for video in channel.videos():
        Item.objects.update_or_create(
            key=video['yt:videoId'],
            defaults={
                'key': video['yt:videoId'],
                'title': video['media:title'],
                'feed': feed,
                'description': video['media:description'],
                'picture': video['media:thumbnail'],
            })

    return True

def load_last_fm_feed(feed_key: str):
    ''' Adds a new feed from Last.fm to the database,
    downloading the data and making items from it'''

    url = LAST_FM_FEED.data_url.format(feed=feed_key, api_key=MisCosasConfig.last_fm_api_key)
    try:
        xml_stream = urllib.request.urlopen(url)
    except urllib.error.HTTPError:
        return False

    artist = LastFmArtist(xml_stream)
    feed, _ = Feed.objects.get_or_create(
        key=feed_key,
        origin=LAST_FM_FEED.name,
        defaults={
            'title': feed_key,
        })

    for album in artist.albums():
        Item.objects.update_or_create(
            key=album['name'],
            defaults={
                'key': album['name'],
                'title': album['name'],
                'feed': feed,
                'picture': album['image'],
            })

    return True


YOUTUBE_FEED = FeedData(
    "YouTube",
    "https://www.youtube.com/channel/{feed}",
    "https://www.youtube.com/watch?v={item}",
    "http://www.youtube.com/feeds/videos.xml?channel_id={feed}",
    "miscosas/youtube_social_icon_white.png",
    load_youtube_feed)

LAST_FM_FEED = FeedData(
    "last.fm",
    "https://www.last.fm/music/{feed}",
    "https://www.last.fm/music/{feed}/{item}",
    "http://ws.audioscrobbler.com/2.0/?method=artist.gettopalbums&artist={feed}&limit=15&api_key={api_key}",
    "https://www.last.fm/static/images/logo_static.adb61955725c.png",
    load_last_fm_feed)

FEEDS_DATA = {
    YOUTUBE_FEED.name: YOUTUBE_FEED,
}
