""" Secret keys for web app

Replace this fields with your own keys
to be able to get data from external APIs
"""

# A secret key for a particular Django installation.
# This is used to provide cryptographic signing,
# and should be set to a unique, unpredictable value.
#
# More info on: https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-SECRET_KEY
PROJECT_KEY = "django-secret-key"

# Get your personal key from https://www.last.fm/join?next=/api/account/create
LAST_FM_API_KEY = "last-fm-api-key"

# Developer key from Goodreads, can be obtained at https://www.goodreads.com/api/keys
GOODREADS_API_KEY = "goodreads-api-key"

# Spotify clientID:clientSecret, can be obtained at https://developer.spotify.com/documentation/general/guides/app-settings/#register-your-app
SPOTIFY_API_KEY = "clientID:secretKey"
