from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MisCosasConfig(AppConfig):
    name = 'miscosas'

    YOUTUBE = 'yt'
    LASTFM = 'lfm'
    REDDIT = 'rd'
    FLICKR = 'fl'
    GOODREADS = 'gr'

    LIGHTMODE = 'lm'
    DARKMODE = 'dm'

    SMALL_FONT = 'sm'
    MEDIUM_FONT = 'md'
    LARGE_FONT = 'lg'

    SOURCES = {
        YOUTUBE: 'YouTube',
        LASTFM: 'last.fm',
        REDDIT: 'Reddit',
        FLICKR: 'Flickr',
        GOODREADS: 'Goodreads',
    }

    THEMES = [
        (LIGHTMODE, _('Light mode')),
        (DARKMODE, _('Dark mode')),
    ]

    FONT_SIZES = [
        (SMALL_FONT, _('Small')),
        (MEDIUM_FONT, _('Medium')),
        (LARGE_FONT, _('Large')),
    ]
