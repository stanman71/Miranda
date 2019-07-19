
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(client_id='11a33d121d194cfebbc08d1ee6dbd0f6', client_secret='af1b5460be774d8db58313bbf1a056b8')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlists = sp.user_playlists('stanman71')

while playlists:
    for i, playlist in enumerate(playlists['items']):
        print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None
        
        
print(sp.me())

"""


import spotipy
import spotipy.util as util
 

token = util.prompt_for_user_token(
        username="stanman71",
        scope="user-read-playback-state streaming",
        client_id="11a33d121d194cfebbc08d1ee6dbd0f6",
        client_secret="af1b5460be774d8db58313bbf1a056b8",
        redirect_uri="http://192.168.1.40:5000/dashboard/spotify/token")

spotify = spotipy.Spotify(auth=token)
current_track = spotify.current_user_playing_track()

print(current_track)


