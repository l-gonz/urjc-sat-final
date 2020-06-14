"""
Forms for app MisCosas
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UsernameField
from django.utils.translation import gettext_lazy as _

from .models import Profile, Feed, Comment


class FeedForm(forms.ModelForm):
    """Form to add new feeds to the database."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adds bootstrap form class to all the fields
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs['class'] = 'form-control'

        self.fields['key'].widget.attrs['maxlength'] = 64

    class Meta:
        model = Feed
        fields = ['source', 'key']


class CommentForm(forms.ModelForm):
    """Form to add new comments to the database.

    Makes sure fields have bootstrap form class and
    the length limit they should."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['title'].widget.attrs['maxlength'] = 64

    class Meta:
        model = Comment
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs=
            {
                'class': 'form-control',
                'rows': 4,
                'maxlength': 256,
            })
        }


class ProfileForm(forms.ModelForm):
    """Form to change the profile settings."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap form classes
        self.fields['_picture'].widget.attrs['class'] = 'form-control-file'
        self.fields['theme'].widget.attrs['class'] = 'form-control'
        self.fields['font_size'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Profile
        fields = ['_picture', 'theme', 'font_size']
        labels = {
            "_picture": _("Profile picture")
        }


class RegistrationForm(UserCreationForm):
    """Override of django default form for user creation."""
    username = UsernameField(max_length=32)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Bootstrap form classes
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs['class'] = 'form-control'


class AuthForm(AuthenticationForm):
    """Override of django default form for authenticating."""
    def __init__(self, *args, **kwargs):
        super(AuthForm, self).__init__(*args, **kwargs)
        # Bootstrap form classes
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs['class'] = 'form-control'
