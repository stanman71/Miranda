
"""

https://github.com/drshrey/spotify-flask-auth-example

https://github.com/plamere/spotipy/issues/194
https://spotipy.readthedocs.io/en/latest/

https://developer.spotify.com/dashboard/
https://developer.spotify.com/documentation/general/guides/scopes/
https://developer.spotify.com/documentation/web-api/reference/search/search/
https://developer.spotify.com/documentation/web-api/reference/player/start-a-users-playback/


BUGFIX SPOTIPY:

Error:    AttributeError: 'Spotify' object has no attribute 'devices'
Solution: Replace the old client.py file 

          > new client.py file is in /SmartControl/support
          > destination linux_path: /usr/local/lib/python3.5/dist-packages/spotipy

https://stackoverflow.com/questions/47028093/attributeerror-spotify-object-has-no-attribute-current-user-saved-tracks


"""


from flask import request, redirect, g, url_for, render_template
from flask_login import login_required, current_user
from functools import wraps
from urllib.parse import quote

from app import app
from app.database.database import *
from app.components.file_management import GET_CONFIG_HOST_IP_ADDRESS, GET_SPOTIFY_CLIENT_ID, GET_SPOTIFY_CLIENT_SECRET
from app.components.control_spotify import *
from app.components.shared_resources import GET_SPOTIFY_AUTHORIZATION_HEADER, SET_SPOTIFY_AUTHORIZATION_HEADER

import requests
import json
import spotipy
import socket 


# access rights
def permission_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.permission_spotify == "checked":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('logout'))
    return wrap


""" ######################## """
""" spotify authentification """
""" ######################## """

# Client Keys
CLIENT_ID         = GET_SPOTIFY_CLIENT_ID()
CLIENT_SECRET     = GET_SPOTIFY_CLIENT_SECRET()

# Spotify URLS
SPOTIFY_AUTH_URL  = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL   = "https://api.spotify.com/v1"

# Server-side Parameters
REDIRECT_URI      = "http://" + GET_CONFIG_HOST_IP_ADDRESS() + "/dashboard/spotify/token"
SCOPE             = "playlist-read-private user-read-recently-played user-read-currently-playing user-read-playback-state streaming"
STATE             = ""
SHOW_DIALOG_bool  = True
SHOW_DIALOG_str   = str(SHOW_DIALOG_bool).lower()


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}


target_site = ""


""" ############ """
""" site spotify """
""" ############ """

@app.route('/dashboard/spotify', methods=['GET', 'POST'])
@login_required
@permission_required
def dashboard_spotify():
    error_message_search_track = ""
    error_message_search_album = ""
    list_search_track_results  = []
    list_search_album_results  = []
    track_name = ""
    track_artist = ""
    album_name = ""
    album_artist = ""   
    collapse_dashboard_search_track = ""   
    collapse_dashboard_search_album = ""        
    
    authorization_header = GET_SPOTIFY_AUTHORIZATION_HEADER()
    

    # check spotify login 
    try:
        
        sp       = spotipy.Spotify(auth=authorization_header)
        sp.trace = False
        
        if request.method == "POST": 
            
            
            """ ####################### """
            """ spotify general control """
            """ ####################### """
        
            try:
        
                spotify_device_id = sp.current_playback(market=None)['device']['id']
                spotify_volume    = request.form.get("get_spotify_volume")
                    
                if "set_spotify_start" in request.form:    
                    sp.volume(int(spotify_volume), device_id=spotify_device_id)  
                    
                    try:
                        context_uri = sp.current_playback(market=None)["context"]["uri"]
                    except:
                        context_uri = None
                        
                    try:
                        track_uri   = sp.current_playback(market=None)['item']['uri']
                    except:
                        track_uri   = None
                        
                    try:
                        position    = sp.current_playback(market=None)['progress_ms']
                    except:
                        position    = None
                    
                    if context_uri != None:
                        sp.start_playback(device_id=spotify_device_id, context_uri=context_uri, uris=None, offset = None, position_ms = None)  
                        
                    elif track_uri != None:
                        sp.start_playback(device_id=spotify_device_id, context_uri=None, uris=[track_uri], offset = None, position_ms = position)    
                        
                    else:
                        sp.start_playback(device_id=spotify_device_id, context_uri=None, uris=None, offset = None, position_ms = None)

                if "set_spotify_previous" in request.form:    
                    sp.volume(int(spotify_volume), device_id=spotify_device_id)   
                    sp.previous_track(device_id=spotify_device_id)     

                if "set_spotify_next" in request.form:     
                    sp.volume(int(spotify_volume), device_id=spotify_device_id)  
                    sp.next_track(device_id=spotify_device_id) 
                    
                if "set_spotify_stop" in request.form:     
                    sp.pause_playback(device_id=spotify_device_id)  

                if "set_spotify_shuffle" in request.form:     
                    sp.shuffle(True, device_id=spotify_device_id) 

                if "set_spotify_volume" in request.form:        
                    sp.volume(int(spotify_volume), device_id=spotify_device_id)      
                    
            except:
                pass
                        
                        
            """ ############## """
            """ start playlist """
            """ ############## """                        
                        
            if "spotify_start_playlist" in request.form:    
                spotify_device_id = request.form.get("spotify_start_playlist")
                playlist_uri      = request.form.get("set_spotify_playlist:" + spotify_device_id)
                playlist_volume   = request.form.get("set_spotify_playlist_volume:" + spotify_device_id)
                
                sp.volume(int(playlist_volume), device_id=spotify_device_id)  
                sp.start_playback(device_id=spotify_device_id, context_uri=playlist_uri, uris=None, offset = None, position_ms = None)      
                                        
           
            """ ############ """
            """ search track """
            """ ############ """   
       
            if "spotify_search_track" in request.form or "spotify_track_play" in request.form or "spotify_track_pause" in request.form:
       
                collapse_dashboard_search_track = "in"   

                try:
                    track_name = request.form.get("get_spotify_search_track")

                    if track_name != "":
                              
                        track_artist = request.form.get("get_spotify_search_track_artist")

                        if track_artist != '':

                            results = sp.search(q='artist:' + track_artist + ' track:' + track_name, limit=5, type='track')

                            if results['tracks']['items'] != []:

                                for i in range(len(results['tracks']['items'])):
                                    list_search_track_results.append((results['tracks']['items'][i]['name'],
                                                                      results['tracks']['items'][i]['artists'][0]['name'],
                                                                      results['tracks']['items'][i]['uri']))

                        else:

                            results = sp.search(q=' track:' + track_name, limit=5, type='track')

                            if results['tracks']['items'] != []:

                                for i in range(len(results['tracks']['items'])):
                                    list_search_track_results.append((results['tracks']['items'][i]['name'],
                                                                      results['tracks']['items'][i]['artists'][0]['name'],
                                                                      results['tracks']['items'][i]['uri']))
                                
                                
                    else:
                        error_message_search_track = "Keinen Track Namen angegeben"
                                          
                except Exception as e:
                    error_message_search_track = "ERROR: " + str(e)   
                    
                    
                try:
                    
                    if "spotify_track_play" in request.form:
                        
                        track_uri         = request.form.get("spotify_track_play")
                        spotify_device_id = request.form.get("get_spotify_track_device:" + track_uri)
                        volume            = request.form.get("get_spotify_track_volume:" + track_uri)

                        sp.volume(int(volume), device_id=spotify_device_id)  
                        sp.start_playback(device_id=spotify_device_id, context_uri=None, uris=[track_uri], offset={"position": 0})                               
                        
                except Exception as e:
                    error_message_search_track = "ERROR: " + str(e)  
                         
       
            """ ############ """
            """ search album """
            """ ############ """   
       

            if "spotify_search_album" in request.form or "spotify_album_play" in request.form or "spotify_album_pause" in request.form:
                
                collapse_dashboard_search_album = "in"  
                
                try:
                    album_name = request.form.get("get_spotify_search_album")

                    if album_name != "":
                              
                        album_artist = request.form.get("get_spotify_search_album_artist")

                        if album_artist != '':

                            results = sp.search(q='artist:' + album_artist + ' album:' + album_name, limit=5, type='album')

                            if results['albums']['items'] != []:

                                for i in range(len(results['albums']['items'])):
                                    list_search_album_results.append((results['albums']['items'][i]['name'],
                                                                      results['albums']['items'][i]['artists'][0]['name'],
                                                                      results['albums']['items'][i]['uri']))

                        else:

                            results = sp.search(q=' album:' + album_name, limit=5, type='album')

                            if results['albums']['items'] != []:

                                for i in range(len(results['albums']['items'])):
                                    list_search_album_results.append((results['albums']['items'][i]['name'],
                                                                      results['albums']['items'][i]['artists'][0]['name'],
                                                                      results['albums']['items'][i]['uri']))
                                
                                     
                    else:
                        error_message_search_album = "Keinen Album Namen angegeben"

                                          
                except Exception as e:
                    error_message_search_album = "ERROR: " + str(e)   
                    
                  
                try:
                    
                    if "spotify_album_play" in request.form:
                        
                        album_uri         = request.form.get("spotify_album_play")
                        spotify_device_id = request.form.get("get_spotify_album_device:" + album_uri)
                        volume            = request.form.get("get_spotify_album_volume:" + album_uri)

                        sp.volume(int(volume), device_id=spotify_device_id)  
                        sp.start_playback(device_id=spotify_device_id, context_uri=album_uri, uris=None, offset={"position": 0})                               
                        
                except Exception as e:
                    error_message_search_album = "ERROR: " + str(e)         
       
            
        """ ############ """
        """ account data """
        """ ############ """   
                       
        spotify_user           = sp.current_user()["display_name"]   
        spotify_devices        = sp.devices()["devices"]        
        spotify_playlists      = sp.current_user_playlists(limit=20)["items"]                                 
        tupel_current_playback = GET_SPOTIFY_CURRENT_PLAYBACK(authorization_header)                            
        
        # set volume
        try:
            spotify_current_playback_volume = sp.current_playback(market=None)['device']['volume_percent']
            volume = spotify_current_playback_volume    
            
        except:
            volume = 50
    

    except Exception as e:
        print(e)
        tupel_current_playback = ""
        spotify_user = "Nicht eingeloggt"
        spotify_playlists = ""
        spotify_devices = ""
        volume = 50         

    
    return render_template('dashboard_spotify.html',
                            error_message_search_track=error_message_search_track,
                            error_message_search_album=error_message_search_album,
                            spotify_user=spotify_user,  
                            tupel_current_playback=tupel_current_playback,
                            spotify_playlists=spotify_playlists,
                            spotify_devices=spotify_devices, 
                            list_search_track_results=list_search_track_results, 
                            list_search_album_results=list_search_album_results,     
                            track_name=track_name,
                            track_artist=track_artist,     
                            album_name=album_name,
                            album_artist=album_artist,   
                            volume=volume, 
                            collapse_dashboard_search_track=collapse_dashboard_search_track,   
                            collapse_dashboard_search_album=collapse_dashboard_search_album,                                                                                                                                                                                   
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system,                     
                            )
                            
                                                  
@app.route("/dashboard/spotify/login/url/<string:target_site_url>")
@login_required
@permission_required
def spotify_login(target_site_url):
    
    global target_site 
    
    target_site = target_site_url
    
    # start authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)

    return redirect(auth_url)
    

@app.route("/dashboard/spotify/token")
@login_required
@permission_required
def spotify_token():

    global target_site    
    
    target_site_url = target_site
    
    # requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # tokens are returned to application
    response_data = json.loads(post_request.text)
    access_token  = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type    = response_data["token_type"]
    expires_in    = response_data["expires_in"]

    # use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    SET_SPOTIFY_AUTHORIZATION_HEADER(authorization_header)


    if target_site_url == "dashboard":
        return redirect(url_for('dashboard'))
        
    if target_site_url == "spotify":
        return redirect(url_for('dashboard_spotify'))      
    

@app.route("/dashboard/spotify/logout/url/<string:target_site_url>")
@login_required
@permission_required
def spotify_logout(target_site_url):
    global authorization_header

    # delete token
    authorization_header = ""    
    
    SET_SPOTIFY_AUTHORIZATION_HEADER(authorization_header)
        
    
    if target_site_url == "dashboard":
        return redirect(url_for('dashboard'))
        
    if target_site_url == "spotify":
        return redirect(url_for('dashboard_spotify'))        
        
