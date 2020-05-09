"""
URL config for app MisCosas
"""

from django.urls import path

from . import views

urlpatterns = [
    path('feeds', views.feeds),
    path('feed/<str:id>', views.feed),
    path('items', views.items),
    path('item/<str:id>', views.item),
    path('users', views.users),
    path('user/<str:id>', views.user),
    path('about', views.about),
    path('', views.index),
]
