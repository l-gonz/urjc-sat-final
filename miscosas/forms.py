"""
Forms for app MisCosas
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField

from .models import Profile
from .feeds.feedhandler import FEEDS_DATA

CHOICES = [(key, key) for key in FEEDS_DATA]

class FeedForm(forms.Form):
    source = forms.CharField(widget=forms.Select(choices=CHOICES, attrs={'class':'form-control'}))
    key = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'class':'form-control'}))


class CommentForm(forms.Form):
    title = forms.CharField(max_length=64, widget=forms.TextInput(attrs={'class':'form-control'}))
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class':'form-control',
            'rows':4}),
        max_length=256)


class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['_picture'].widget.attrs['class'] = 'form-control-file'
        self.fields['theme'].widget.attrs['class'] = 'form-control'
        self.fields['font_size'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Profile
        fields = ['_picture', 'theme', 'font_size']
        labels = {
            "_picture": "Profile picture"
        }


class RegistrationForm(UserCreationForm):
    ''' Override of django default form for user creation '''
    username = UsernameField(max_length=32)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs['class'] = 'form-control'


class AuthForm(AuthenticationForm):
    ''' Override of django default form for authenticating '''
    def __init__(self, *args, **kwargs):
        super(AuthForm, self).__init__(*args, **kwargs)

        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs['class'] = 'form-control'