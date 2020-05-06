"""
Forms for app MisCosas
"""

from django import forms

from .models import Feed, Comment

class FeedForm(forms.Form):
    key = forms.CharField()

class CommentForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField()