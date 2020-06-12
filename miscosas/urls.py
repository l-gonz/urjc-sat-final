"""
URL config for app MisCosas
"""

from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import AuthForm
from .feeds.rssfeeds import RssFeed

#TODO Name views
#TODO Raise exception on load() en vez de (_,_)
#TODO Feeds en Profile
#TODO Probar en lab
#TODO Rehacer db
#TODO Traducir

urlpatterns = [
    # Auth
    path('login/', auth_views.LoginView.as_view(authentication_form=AuthForm)),
    path('logout/', auth_views.LogoutView.as_view()),
    path('signup', views.signup),
    # App
    path('feeds', views.feeds_page),
    path('feed/<str:feed_id>', views.feed_page),
    path('item/<str:item_id>', views.item_page),
    path('users', views.users_page),
    path('user/<str:username>', views.user_page),
    path('about', views.about_page),
    path('comments.rss', RssFeed()),
    path('', views.index),
]
