import urllib

from project.secretkeys import LAST_FM_API_KEY
from miscosas.models import Feed, Item
from .ytchannel import YTChannel
from .lastfmartist import LastFmArtist


class FeedData():
    ''' Stores information from a feed source. '''

    def __init__(self, feed_url, item_url, data_url, icon_src, load_function):
        ''' Urls for accessing the feed.

        Urls need {feed} or {item} fields for formatting. '''

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

    def get_data_url(self, feed_key, api_key=""):
        ''' Returns the url of the XML or JSON file
        with the data from the feed with the given key '''
        return str.format(self.data_url, feed=feed_key, api_key=api_key)

    def load_feed(self, feed_key):
        ''' Load the info from a new or existing feed '''
        self.load(feed_key)


def load_youtube_feed(feed_key: str):
    ''' Adds a new feed from YouTube to the database,
    downloading the data and making items from it'''

    url = YOUTUBE_FEED.get_data_url(feed_key)
    try:
        xml_stream = urllib.request.urlopen(url)
    except urllib.error.HTTPError:
        return False

    channel = YTChannel(xml_stream)
    feed, _ = Feed.objects.update_or_create(
        key=feed_key,
        source=Feed.YOUTUBE,
        defaults={
            'title': channel.name(),
            'chosen': True,
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

    url = LAST_FM_FEED.get_data_url(urllib.parse.quote(feed_key), LAST_FM_API_KEY)
    try:
        xml_stream = urllib.request.urlopen(url)
    except urllib.error.HTTPError:
        return False

    artist = LastFmArtist(xml_stream)
    feed, _ = Feed.objects.update_or_create(
        key=feed_key,
        source=Feed.LASTFM,
        defaults={
            'title': artist.name(),
            'chosen': True
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
    "https://www.youtube.com/channel/{feed}",
    "https://www.youtube.com/watch?v={item}",
    "http://www.youtube.com/feeds/videos.xml?channel_id={feed}",
    "miscosas/youtube_social_icon_white.png",
    load_youtube_feed)

LAST_FM_FEED = FeedData(
    "https://www.last.fm/music/{feed}",
    "https://www.last.fm/music/{feed}/{item}",
    "http://ws.audioscrobbler.com/2.0/?method=artist.gettopalbums&artist={feed}&limit=15&api_key={api_key}",
    "https://www.last.fm/static/images/logo_static.adb61955725c.png",
    load_last_fm_feed)

FEEDS_DATA = {
    Feed.YOUTUBE: YOUTUBE_FEED,
    Feed.LASTFM: LAST_FM_FEED,
}
