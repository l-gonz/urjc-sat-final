"""
Forms for app MisCosas
"""

from django import forms

from .feeds.feedhandler import FEEDS_DATA

CHOICES = [(key, key) for key in FEEDS_DATA]

class FeedForm(forms.Form):
    origin = forms.CharField(widget=forms.Select(choices=CHOICES))
    key = forms.CharField()


class CommentForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)
