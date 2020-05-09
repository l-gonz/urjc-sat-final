from django.test import TestCase

from .forms import *
from .models import *

# Create your tests here.
class TestEmptyDb(TestCase):

    def test_main_page(self):
        response = self.client.get('/')
        self.assertContains(response, "class='no-content'", count=2, status_code=200)
        self.assertContains(response, "<form", count=1, status_code=200)

    def test_feed_form(self):
        form_data = {'key': 'uyv3458slf'}
        form = FeedForm(data=form_data)

        self.assertTrue(form.is_valid())

        response = self.client.post('/feeds', form.cleaned_data)

        self.assertEqual(response.status_code, 200)