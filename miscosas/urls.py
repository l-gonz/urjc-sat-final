"""
URL config for app MisCosas
"""

from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # Auth
    path('login/', auth_views.LoginView.as_view()),
    path('logout/', auth_views.LogoutView.as_view()),
    # App
    path('feeds', views.feeds_page),
    path('feed/<str:feed_id>', views.feed_page),
    path('item/<str:item_id>', views.item_page),
    path('users', views.users_page),
    path('user/<str:username>', views.user_page),
    path('about', views.about_page),
    path('', views.index),
]
