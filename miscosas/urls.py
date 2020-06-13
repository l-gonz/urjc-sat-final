"""
URL config for app MisCosas
"""

from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import AuthForm
from .feeds.rssfeeds import RssFeed

#TODO Name views
#TODO Probar en lab
#TODO Rehacer db

urlpatterns = [
    # Auth
    path('login/', auth_views.LoginView.as_view(authentication_form=AuthForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    # App
    path('feeds', views.feeds_page, name='feeds'),
    path('feed/<str:feed_id>', views.feed_page, name='feed'),
    path('item/<str:item_id>', views.item_page, name='item'),
    path('users', views.users_page, name='users'),
    path('user/<str:username>', views.user_page, name='user'),
    path('about', views.about_page, name='about'),
    path('comments.rss', RssFeed(), name='rss'),
    path('', views.index, name='index'),
]
