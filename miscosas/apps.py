import sys
import json

from django.apps import AppConfig

ERROR_MESSAGE = """
[MisCosasConfig] Could not find file with secret keys.
Create a 'secret.json' file with api keys if you want all functionality to be available
"""

class MisCosasConfig(AppConfig):
    name = 'miscosas'

    last_fm_api_key = ""
    try:
        with open('secret.json') as f:
            last_fm_api_key = json.load(f)['lastfm']
    except FileNotFoundError:
        print(ERROR_MESSAGE, file=sys.stderr)