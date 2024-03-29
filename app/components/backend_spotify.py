
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

          > new client.py file is in /miranda/support
          > destination linux_path: /usr/local/lib/python3.7/dist-packages/spotipy
          > sudo cp /home/pi/miranda/support/Spotipy/client.py /usr/local/lib/python3.7/dist-packages/spotipy/client.py

https://stackoverflow.com/questions/47028093/attributeerror-spotify-object-has-no-attribute-current-user-saved-tracks


"""

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.email import SEND_EMAIL

import requests
import json
import spotipy
import socket 
import time
import base64
import threading

from urllib.parse import quote

""" ######################## """
""" spotify authentification """
""" ######################## """

#  Client Keys
CLIENT_ID             = GET_SPOTIFY_CLIENT_ID()
CLIENT_SECRET         = GET_SPOTIFY_CLIENT_SECRET()

# Spotify URLS
SPOTIFY_AUTH_URL      = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL     = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL  = "https://api.spotify.com"
API_VERSION           = "v1"
SPOTIFY_API_URL       = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
REDIRECT_URI          = "http://" + GET_HOST_DEFAULT_NETWORK() + ":" + str(GET_HOST_PORT()) + "/spotify/token"
SCOPE                 = "playlist-read-private user-read-recently-played user-read-currently-playing user-read-playback-state streaming"
STATE                 = ""
SHOW_DIALOG_bool      = True
SHOW_DIALOG_str       = str(SHOW_DIALOG_bool).lower()

#  Client Tokens
SPOTIFY_TOKEN         = ''
SPOTIFY_REFRESH_TOKEN = GET_SPOTIFY_REFRESH_TOKEN()
    
    
def GET_SPOTIFY_AUTHORIZATION():
    
    auth_query_parameters = {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "client_id": CLIENT_ID
    }    
    
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    
    return auth_url


def GENERATE_SPOTIFY_TOKEN(auth_token):
    
    global SPOTIFY_TOKEN    
    global SPOTIFY_REFRESH_TOKEN       
    
    body = {
        "grant_type": 'authorization_code',
        "code" : str(auth_token),
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    post_request = requests.post(SPOTIFY_TOKEN_URL, data=body)

    answer = json.loads(post_request.text)
    
    try:
        SPOTIFY_TOKEN = answer["access_token"]
        WRITE_LOGFILE_SYSTEM("SUCCESS", "Spotify | Login")
        WRITE_LOGFILE_SYSTEM("SUCCESS", "Spotify | Token received")
        
    except:
        WRITE_LOGFILE_SYSTEM("ERROR", "Spotify | Login failed")
        WRITE_LOGFILE_SYSTEM("ERROR", "Spotify | Token not received | " + str(answer))
        SEND_EMAIL("ERROR", "Spotify | Token not received | " + str(answer))

    try:
        SET_SPOTIFY_REFRESH_TOKEN(answer["refresh_token"])
        SPOTIFY_REFRESH_TOKEN = answer["refresh_token"]        
        WRITE_LOGFILE_SYSTEM("SUCCESS", "Spotify | Refresh Token received") 
        
    except:
        WRITE_LOGFILE_SYSTEM("ERROR", "Spotify | Refresh Token not received | " + str(answer))
        SEND_EMAIL("ERROR", "Spotify | Refresh Token not received | " + str(answer))           
 
    REFRESH_SPOTIFY_TOKEN_THREAD(0)


def GET_SPOTIFY_TOKEN():
    global SPOTIFY_TOKEN

    return SPOTIFY_TOKEN


def DELETE_SPOTIFY_TOKEN():
    global SPOTIFY_TOKEN
    global SPOTIFY_REFRESH_TOKEN   

    SPOTIFY_TOKEN         = ""
    SPOTIFY_REFRESH_TOKEN = ""
    SET_SPOTIFY_REFRESH_TOKEN("")


""" #################### """
""" token refresh thread """
""" #################### """


def REFRESH_SPOTIFY_TOKEN_THREAD(first_delay):
    
    try:
        Thread = threading.Thread(target=REFRESH_SPOTIFY_TOKEN, args=(first_delay, ))
        Thread.start()  
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Thread | Refresh Spotify Token | " + str(e)) 
        SEND_EMAIL("ERROR", "Thread | Refresh Spotify Token | " + str(e)) 


def REFRESH_SPOTIFY_TOKEN(first_delay):   
    
    current_timer = first_delay
    
    global SPOTIFY_TOKEN        
    global SPOTIFY_REFRESH_TOKEN
    
    while SPOTIFY_REFRESH_TOKEN != "":
        
        if current_timer == 3000:
        
            body = {
                "grant_type" : "refresh_token",
                "refresh_token" : GET_SPOTIFY_REFRESH_TOKEN()
            }

            auth_str = '{}:{}'.format(CLIENT_ID, CLIENT_SECRET)
            b64_auth_str = base64.b64encode(auth_str.encode()).decode()

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic {}'.format(b64_auth_str)
            }

            post_refresh = requests.post(SPOTIFY_TOKEN_URL, data=body, headers=headers) 
            answer       = json.loads(post_refresh.text)

            try:
                SPOTIFY_TOKEN = answer["access_token"]
                WRITE_LOGFILE_SYSTEM("SUCCESS", "Spotify | Token updated") 
                
            except Exception as e:
                WRITE_LOGFILE_SYSTEM("ERROR", "Spotify | Token not updated | " + str(e)) 
                SEND_EMAIL("ERROR", "Spotify | Token not updated | " + str(e)) 

            try:
                SET_SPOTIFY_REFRESH_TOKEN(answer["refresh_token"])
                SPOTIFY_REFRESH_TOKEN = answer["refresh_token"]        
                WRITE_LOGFILE_SYSTEM("SUCCESS", "Spotify | Refresh Token updated")  
                
            except:
                pass
                
            current_timer = 0
            
                
        else:
            current_timer = current_timer + 1
            time.sleep(1)


""" ############### """
""" spotify control """
""" ############### """


def SPOTIFY_CONTROL(spotify_token, command, spotify_volume):

    sp       = spotipy.Spotify(auth=spotify_token)
    sp.trace = False     

    try:

        spotify_device_id = sp.current_playback(market=None)['device']['id']

        if command == "play":    
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

        if command == "previous":    
            sp.volume(int(spotify_volume), device_id=spotify_device_id)   
            sp.previous_track(device_id=spotify_device_id)     

        if command == "next":     
            sp.volume(int(spotify_volume), device_id=spotify_device_id)  
            sp.next_track(device_id=spotify_device_id) 
            
        if command == "stop":     
            sp.pause_playback(device_id=spotify_device_id)  

        if command == "shuffle":     
            sp.shuffle(True, device_id=spotify_device_id) 

        if command == "volume":        
            sp.volume(int(spotify_volume), device_id=spotify_device_id)      

        if command == "turn_up":   
            volume = spotify_volume + 10
            
            if volume > 100:
                volume = 100
               
            sp.volume(int(volume), device_id=spotify_device_id)  
                
        if command == "turn_down":   
            volume = spotify_volume - 10
            
            if volume < 0:
                volume = 0
               
            sp.volume(int(volume), device_id=spotify_device_id)     
        
            
    except Exception as e:
        if str(e) == "'NoneType' object is not subscriptable":
            pass
            #WRITE_LOGFILE_SYSTEM("ERROR", "Spotify | No active Device founded")                     
        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Spotify | " + str(e)) 


def SPOTIFY_START_PLAYLIST(spotify_token, spotify_device_id, playlist_uri, playlist_volume):

    sp       = spotipy.Spotify(auth=spotify_token)
    sp.trace = False    
    
    sp.start_playback(device_id=spotify_device_id, context_uri=playlist_uri, uris=None, offset = None, position_ms = None)     
    sp.volume(int(playlist_volume), device_id=spotify_device_id)  
    sp.shuffle(True, device_id=spotify_device_id)
    sp.next_track(device_id=spotify_device_id) 
    

def SPOTIFY_START_TRACK(spotify_token, spotify_device_id, track_uri, track_volume):

    sp       = spotipy.Spotify(auth=spotify_token)
    sp.trace = False    

    sp.volume(int(track_volume), device_id=spotify_device_id)   
    sp.start_playback(device_id=spotify_device_id, context_uri=None, uris=[track_uri], offset={"position": 0})    
    

def SPOTIFY_START_ALBUM(spotify_token, spotify_device_id, album_uri, album_volume):

    sp       = spotipy.Spotify(auth=spotify_token)
    sp.trace = False    

    sp.volume(int(album_volume), device_id=spotify_device_id) 
    sp.start_playback(device_id=spotify_device_id, context_uri=album_uri, uris=None, offset={"position": 0})      



""" #################### """
""" get current playback """
""" #################### """

def GET_SPOTIFY_CURRENT_PLAYBACK(spotify_token):

    sp       = spotipy.Spotify(auth=spotify_token)
    sp.trace = False        

    spotify_current_playback = sp.current_playback(market=None)


    try:
        # get device name
        spotify_current_playback_device_name = spotify_current_playback['device']['name']
        
    except:
        spotify_current_playback_device_name = ""
 
 
    try:
        # get device type
        spotify_current_playback_device_type = spotify_current_playback['device']['type']
        
    except:
        spotify_current_playback_device_type = ""     


    try:
        # get playback state
        spotify_current_playback_state = spotify_current_playback['is_playing'] 
        
    except:
        spotify_current_playback_state = ""
 
 
    try:
        # get playback volume
        spotify_current_playback_volume = spotify_current_playback['device']['volume_percent']
        
    except:
        spotify_current_playback_volume = ""      
 
 
    try:
        # get playback track
        spotify_current_playback_track = spotify_current_playback['item']['name']   
        
    except:
        spotify_current_playback_track = ""           
 
 
    try:
        # get playback track artists
        spotify_current_playback_artists = []
        
        for i in range(len(spotify_current_playback["item"]["artists"])):
            spotify_current_playback_artists.append(spotify_current_playback["item"]["artists"][i]["name"])  
            
    except:
        spotify_current_playback_artists = []     


    try:
        # get progress in minutes:seconds
        spotify_current_playback_progress = spotify_current_playback['progress_ms'] / 1000
        
        def convertSeconds(seconds):
            h = seconds//(60*60)
            m = int((seconds-h*60*60)//60)
            s = int(seconds-(h*60*60)-(m*60))
            
            if len(str(s)) == 1:
                s = str(0) + str(s) 
            
            return [m, s]
            
        spotify_current_playback_progress = (str(convertSeconds(spotify_current_playback_progress)[0]) + ":" + 
                                             str(convertSeconds(spotify_current_playback_progress)[1]))
    
    except:
        spotify_current_playback_progress = ""
    
    
    try:
        # get playlist name
        spotify_current_playback_playlist_name = sp.user_playlist(sp.current_user()["display_name"], spotify_current_playback["context"]["uri"], fields=None)
        spotify_current_playback_playlist_name = spotify_current_playback_playlist_name['name']
        
    except:
        spotify_current_playback_playlist_name = ""
        
            
    try:
        # get playback shuffle state
        spotify_current_playback_shuffle_state = spotify_current_playback['shuffle_state']   
        
    except:
        spotify_current_playback_shuffle_state = ""  
        
    
    tupel_current_playback = (spotify_current_playback_device_name,
                              spotify_current_playback_device_type,
                              spotify_current_playback_state,
                              spotify_current_playback_volume,
                              spotify_current_playback_track,
                              spotify_current_playback_artists,
                              spotify_current_playback_progress,
                              spotify_current_playback_playlist_name,
                              spotify_current_playback_shuffle_state)
                
                            
    return tupel_current_playback


""" ############ """
""" search track """
""" ############ """

def SPOTIFY_SEARCH_TRACK(spotify_token, track_name, track_artist, number_results):

    sp       = spotipy.Spotify(auth=spotify_token)
    sp.trace = False        
    
    list_search_track_results = []

    try:
        
        if track_name != "":
                  
            if track_artist != '':

                results = sp.search(q='artist:' + track_artist + ' track:' + track_name, limit = number_results, type='track')

                if results['tracks']['items'] != []:

                    for i in range(len(results['tracks']['items'])):
                        list_search_track_results.append((results['tracks']['items'][i]['name'],
                                                          results['tracks']['items'][i]['artists'][0]['name'],
                                                          results['tracks']['items'][i]['uri']))
                                                          
                    return list_search_track_results
                    

            else:

                results = sp.search(q=' track:' + track_name, limit = number_results, type='track')

                if results['tracks']['items'] != []:

                    for i in range(len(results['tracks']['items'])):
                        list_search_track_results.append((results['tracks']['items'][i]['name'],
                                                          results['tracks']['items'][i]['artists'][0]['name'],
                                                          results['tracks']['items'][i]['uri']))
                                                          
                    return list_search_track_results
                    
                    
        else:
            return ("Keinen Track Namen angegeben")
                              
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Spotify | " + str(e)) 
        return ("ERROR: " + str(e))  
                        

""" ############ """
""" search album """
""" ############ """

def SPOTIFY_SEARCH_ALBUM(spotify_token, album_name, album_artist, number_results):

    sp       = spotipy.Spotify(auth=spotify_token)
    sp.trace = False        
    
    list_search_album_results = []

    try:

        if album_name != "":

            if album_artist != '':

                results = sp.search(q='artist:' + album_artist + ' album:' + album_name, limit = number_results, type='album')

                if results['albums']['items'] != []:

                    for i in range(len(results['albums']['items'])):
                        list_search_album_results.append((results['albums']['items'][i]['name'],
                                                          results['albums']['items'][i]['artists'][0]['name'],
                                                          results['albums']['items'][i]['uri']))
                    
                    return list_search_album_results                                      
                

            else:

                results = sp.search(q=' album:' + album_name, limit = number_results, type='album')

                if results['albums']['items'] != []:

                    for i in range(len(results['albums']['items'])):
                        list_search_album_results.append((results['albums']['items'][i]['name'],
                                                          results['albums']['items'][i]['artists'][0]['name'],
                                                          results['albums']['items'][i]['uri']))
                                                          
                    return list_search_album_results
                    
                         
        else:
            return ("Keinen Album Namen angegeben")

                              
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Spotify | " + str(e)) 
        return ("ERROR: " + str(e))  

