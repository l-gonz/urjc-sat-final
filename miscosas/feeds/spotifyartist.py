#!/usr/bin/python3

import base64
import json
from urllib.request import Request, urlopen
from urllib.parse import quote

from .feedparser import FeedParser, ParsingError


class SpotifyHandler:

    def __init__(self, stream):
        tracks_json = json.load(stream)
        tracks_raw = tracks_json['tracks']

        self.tracks = self.parse_tracks(tracks_raw)
        self.name = self.parse_name(tracks_raw)

    def parse_tracks(self, tracks_json: list):
        tracks = []
        for track in tracks_json:
            track_parsed = {
                'id': track['id'],
                'name': track['name'],
            }
            track_parsed['description'] = self.parse_description(track)
            track_parsed['image'] = track['album']['images'][0]['url']
            tracks.append(track_parsed)

        return tracks

    def parse_name(self, tracks: list):
        return tracks[0]['artists'][0]['name']

    def parse_description(self, track: dict):
        try:
            album = track['album']
            link = album['external_urls'].get('spotify')
            preview = track.get('preview_url')
            return (f"<p>Song from album <a href='{link}'>{album.get('name')}</a><p>" +
                    f"<audio controls><source src='{preview}' type='audio/mp3'></audio>")
        except KeyError:
            return ""


class SpotifyArtist(FeedParser):
    """Class to get tracks from an artist in Spotify.

    Uses Spotify API to get a list of tracks from a JSON response
    """

    def __init__(self, stream):
        try:
            self.handler = SpotifyHandler(stream)
        except (KeyError, IndexError):
            raise ParsingError("Could not parse data")

        # Make sure all expected fields are filled
        if not self.handler.name:
            raise ParsingError("Feed has no title")
        if not self.handler.tracks:
            raise ParsingError("Feed has no items")
        if any(not self.is_item_complete(item) for item in self.handler.tracks):
            raise ParsingError("Some item is missing fields")

    def feed_title(self):
        return self.handler.name

    def items_data(self):
        items = []
        for track in self.handler.tracks:
            items.append({
                'key': track['id'],
                'title': track['name'],
                'description': track['description'],
                'picture': track['image'],
            })
        return items

    def is_item_complete(self, item):
        ''' Checks if an individual item has all expected fields '''
        return (item.get('id') and
                item.get('name') and
                'description' in item and
                'image' in item)


def get_artist_id(artist_name: str, api_key: str):
    """Translates an artist name into a Spotify artist id."""
    # Get token
    token_url = "https://accounts.spotify.com/api/token"
    authorization = base64.standard_b64encode(api_key.encode('utf-8')).decode('utf-8')
    headers = {'Authorization' : 'Basic ' + authorization}
    data = "grant_type=client_credentials".encode('utf-8')
    request = Request(token_url, data, headers, method='POST')
    response = urlopen(request)
    response_dict = json.load(response)
    token = response_dict.get('access_token')

    # Search artist name to get id
    search_url = f"https://api.spotify.com/v1/search?q={quote(artist_name)}&type=artist&limit=1"
    headers = {'Authorization' : 'Bearer ' + token}
    request = Request(search_url, headers=headers, method='GET')
    response = urlopen(request)

    # Get artist id from response
    response_dict = json.load(response)
    items = response_dict['artists']['items']

    # No artist was found, try using it the key as artist id instead
    if len(items) == 0:
        return headers, artist_name

    artist_id = items[0].get('id')
    return headers, artist_id
