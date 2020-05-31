from django.contrib import admin
from .models import Feed, Item, Vote, Comment, Profile

# Register your models here.
admin.site.register(Feed)
admin.site.register(Item)
admin.site.register(Vote)
admin.site.register(Comment)
admin.site.register(Profile)