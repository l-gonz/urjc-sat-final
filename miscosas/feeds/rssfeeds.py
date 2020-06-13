from django.contrib.syndication.views import Feed

from miscosas.models import Comment

class RssFeed(Feed):
    title = "Comments"
    link = "/"
    feed_url = "/comments.rss"
    description = "New comments published to the app"

    def items(self):
        return Comment.objects.order_by('-date')[:10]

    def item_title(self, item: Comment):
        return item.title

    def item_description(self, item: Comment):
        return item.content

    def item_link(self, item: Comment):
        return '/item/' + str(item.item.pk)

    def item_author_name(self, item: Comment):
        return item.user.username

    def item_author_link(self, item: Comment):
        return '/user/' + item.user.username

    def item_pubdate(self, item: Comment):
        return item.date

    def item_updateddate(self, item: Comment):
        return item.date
