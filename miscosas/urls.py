"""
URL config for app MisCosas
"""

from django.urls import path

from . import views

urlpatterns = [
    path('feeds', views.feeds_page),
    path('feed/<str:id>', views.feed_page),
    path('item/<str:id>', views.item_page),
    path('users', views.users_page),
    path('user/<str:id>', views.user_page),
    path('about', views.about_page),
    path('', views.index),
]
