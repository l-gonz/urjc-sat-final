class FeedData():

    def __init__(self, name, feedUrl, itemUrl, dataUrl, iconSrc):
        self.name = name
        self.feedUrl = feedUrl
        self.itemUrl = itemUrl
        self.dataUrl = dataUrl
        self.iconSrc = iconSrc

    def get_feed_url(self, id):
        return str.format(self.feedUrl, id=id)

    def get_item_url(self, id):
        return str.format(self.itemUrl, id=id)

    def get_data_url(self, id):
        return str.format(self.dataUrl, id=id)


youtube_feed = FeedData(
    "YouTube",
    "https://www.youtube.com/channel/{id}",
    "https://www.youtube.com/watch?v={id}",
    "http://www.youtube.com/feeds/videos.xml?channel_id={id}",
    "miscosas/youtube_social_icon_white.png")