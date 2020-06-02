"""
Forms for app MisCosas
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField

from .models import Profile, User
from .feeds.feedhandler import FEEDS_DATA

CHOICES = [(key, key) for key in FEEDS_DATA]

class FeedForm(forms.Form):
    source = forms.CharField(widget=forms.Select(choices=CHOICES))
    key = forms.CharField()


class CommentForm(forms.Form):
    title = forms.CharField(max_length=64)
    content = forms.CharField(widget=forms.Textarea, max_length=256)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['_picture', 'theme', 'font_size']
        labels = {
            "_picture": "Profile picture"
        }


class RegistrationForm(UserCreationForm):
    username = UsernameField(max_length=32)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
