import json

from django.apps import AppConfig

LAST_FM_API_KEY = ""


class MisCosasConfig(AppConfig):
    name = 'miscosas'

    with open('secret.json') as f:
        LAST_FM_API_KEY = json.load(f)['lastfm']
