"""
Forms for app MisCosas
"""

from django import forms

from .feeds.feedhandler import FEEDS_DATA

choices = [(key, key) for key in FEEDS_DATA]

class FeedForm(forms.Form):
    origin = forms.CharField(widget=forms.Select(choices=choices))
    key = forms.CharField()


class CommentForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)
