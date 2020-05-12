import urllib

from miscosas.models import Feed, Item
from .ytchannel import YTChannel


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

    def get_feed_url(self, key):
        ''' Returns the url of the feed with the given key '''
        return str.format(self.feed_url, key=key)

    def get_item_url(self, key):
        ''' Returns the url of the item with the given key '''
        return str.format(self.item_url, key=key)

    def get_data_url(self, key):
        ''' Returns the url of the XML or JSON file
        with the data from the feed with the given key '''
        return str.format(self.data_url, key=key)

    def load_feed(self, key):
        ''' Load the infor from a new or existing feed '''
        self.load(key)


def load_youtube_feed(key: str):
    ''' Adds a new feed from YouTube to the database,
    downloading the data and making items from it'''

    url = YOUTUBE_FEED.data_url.format(key=key)
    try:
        xml_stream = urllib.request.urlopen(url)
    except urllib.error.HTTPError:
        return False

    channel = YTChannel(xml_stream)
    feed, _ = Feed.objects.get_or_create(
        key=key,
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


YOUTUBE_FEED = FeedData(
    "YouTube",
    "https://www.youtube.com/channel/{key}",
    "https://www.youtube.com/watch?v={key}",
    "http://www.youtube.com/feeds/videos.xml?channel_id={key}",
    "miscosas/youtube_social_icon_white.png",
    load_youtube_feed)

FEEDS_DATA = {
    YOUTUBE_FEED.name: YOUTUBE_FEED,
}
