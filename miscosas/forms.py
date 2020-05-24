"""
Forms for app MisCosas
"""

from django import forms

from .models import Profile
from .feeds.feedhandler import FEEDS_DATA

CHOICES = [(key, key) for key in FEEDS_DATA]

class FeedForm(forms.Form):
    source = forms.CharField(widget=forms.Select(choices=CHOICES))
    key = forms.CharField()


class CommentForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['_picture', 'theme', 'font_size']
        labels = {
            "_picture": "Profile picture"
        }
