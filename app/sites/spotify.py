from flask import request, redirect, g, url_for, render_template
from flask_login import login_required, current_user
from functools import wraps
from urllib.parse import quote

from app import app
from app.database.database import *
from app.components.backend_spotify import *
from app.components.email import SEND_EMAIL

import requests
import json
import spotipy
import socket 


# access rights
def permission_required(f):
    @wraps(f)
    def wrap(*args, **kwargs): 
        try:
            if current_user.permission_spotify == "checked":
                return f(*args, **kwargs)
            else:
                return redirect(url_for('logout'))
        except Exception as e:
            print(e)
            return redirect(url_for('logout'))
        
    return wrap


forwarding_site_global = ""

list_search_track_results = ""
list_search_album_results = ""


""" ############ """
""" site spotify """
""" ############ """

@app.route('/spotify', methods=['GET', 'POST'])
@login_required
@permission_required
def spotify():   
    
    global list_search_track_results
    global list_search_album_results
    
    error_message_search_track = ""
    error_message_search_album = ""
    error_message_spotify      = ""
    
    track_name   = ""
    track_artist = ""
    album_name   = "" 
    album_artist = ""  
    collapse_search_track = ""   
    collapse_search_album = ""        
    

    spotify_token = GET_SPOTIFY_TOKEN()
    

    # check spotify login 
    if spotify_token != "":
        
        try:
        
            sp       = spotipy.Spotify(auth=spotify_token)
            sp.trace = False
            
            if request.method == "POST": 
                
                spotify_volume = request.form.get("get_spotify_volume")
            
                if "set_spotify_play" in request.form:  
                    SPOTIFY_CONTROL(spotify_token, "play", spotify_volume)       
        
                if "set_spotify_previous" in request.form: 
                    SPOTIFY_CONTROL(spotify_token, "previous", spotify_volume)   

                if "set_spotify_next" in request.form:
                    SPOTIFY_CONTROL(spotify_token, "next", spotify_volume)     

                if "set_spotify_stop" in request.form:  
                    SPOTIFY_CONTROL(spotify_token, "stop", spotify_volume)   

                if "set_spotify_shuffle" in request.form:  
                    SPOTIFY_CONTROL(spotify_token, "shuffle", spotify_volume)   

                if "set_spotify_volume" in request.form: 
                    SPOTIFY_CONTROL(spotify_token, "volume", spotify_volume)          
                            
                if "spotify_start_playlist" in request.form:    
                    spotify_device_id = request.form.get("spotify_start_playlist")
                    playlist_uri      = request.form.get("set_spotify_playlist:" + spotify_device_id)
                    playlist_volume   = request.form.get("set_spotify_playlist_volume:" + spotify_device_id)
                    
                    SPOTIFY_START_PLAYLIST(spotify_token, spotify_device_id, playlist_uri, playlist_volume)


                """ ##### """
                """ track """
                """ ##### """   
           
                if "spotify_search_track" in request.form:
           
                    collapse_search_track = "in"   

                    track_name   = request.form.get("get_spotify_search_track")
                    track_artist = request.form.get("get_spotify_search_track_artist")
                    
                    list_search_track_results = SPOTIFY_SEARCH_TRACK(spotify_token, track_name, track_artist, 5)
                
                    if isinstance(list_search_track_results, str):
                        error_message_search_track = list_search_track_results
                        list_search_track_results  = []  
                        
                
                if "spotify_track_play" in request.form:
                    
                    collapse_search_track = "in"  
                    
                    track_uri         = request.form.get("spotify_track_play")
                    spotify_device_id = request.form.get("get_spotify_track_device:" + track_uri)
                    track_volume      = request.form.get("get_spotify_track_volume:" + track_uri)
                    
                    SPOTIFY_START_TRACK(spotify_token, spotify_device_id, track_uri, track_volume)

                             
           
                """ ##### """
                """ album """
                """ ##### """   
           
                if "spotify_search_album" in request.form:
                    
                    collapse_search_album = "in"  

                    album_name   = request.form.get("get_spotify_search_album")
                    album_artist = request.form.get("get_spotify_search_album_artist")

                    list_search_album_results = SPOTIFY_SEARCH_ALBUM(spotify_token, album_name, album_artist, 5)  
       
                    if isinstance(list_search_album_results, str):
                        error_message_search_album = list_search_album_results 
                        list_search_album_results  = []  
                          
                        
                if "spotify_album_play" in request.form:
                    
                    collapse_search_album = "in" 
                    
                    album_uri         = request.form.get("spotify_album_play")
                    spotify_device_id = request.form.get("get_spotify_album_device:" + album_uri)
                    album_volume      = request.form.get("get_spotify_album_volume:" + album_uri)
                    
                    SPOTIFY_START_ALBUM(spotify_token, spotify_device_id, album_uri, album_volume)
     
            
            """ ############ """
            """ account data """
            """ ############ """   
                     
            spotify_user           = sp.current_user()["display_name"]   
            spotify_devices        = sp.devices()["devices"]        
            spotify_playlists      = sp.current_user_playlists(limit=20)["items"]                                 
            tupel_current_playback = GET_SPOTIFY_CURRENT_PLAYBACK(spotify_token) 
            
            
            print("#############################")
            print(spotify_devices)
            

            # get volume
            try:
                spotify_current_playback_volume = sp.current_playback(market=None)['device']['volume_percent']
                volume = spotify_current_playback_volume    
                
            except:
                volume = 50
    
    
        # login problems
        except Exception as e:
            WRITE_LOGFILE_SYSTEM("ERROR", "Spotify | " + str(e)) 
            SEND_EMAIL("ERROR", "Spotify | " + str(e)) 
            
            tupel_current_playback = ""
            spotify_user = ""
            spotify_playlists = ""
            spotify_devices = ""
            volume = 50         
    
    
    # not logged in
    else:     
        tupel_current_playback = ""
        spotify_user           = ""
        spotify_playlists      = ""
        spotify_devices        = ""
        volume                 = 50         
        
        
    return render_template('spotify.html',
                            error_message_search_track=error_message_search_track,
                            error_message_search_album=error_message_search_album,
                            error_message_spotify=error_message_spotify,
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
                            collapse_search_track=collapse_search_track,   
                            collapse_search_album=collapse_search_album,                                                                                                                                                                                   
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,
                            permission_heating=current_user.permission_heating,                           
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system,                     
                            )
  
  
  
@app.route("/spotify/login/url_target/<string:forwarding_site>")
@login_required
@permission_required
def spotify_login(forwarding_site):
    global forwarding_site_global
    
    forwarding_site_global = forwarding_site
    
    auth_url = GET_SPOTIFY_AUTHORIZATION()
    
    return redirect(auth_url)  
 
 
@app.route("/spotify/token")
@login_required
@permission_required
def spotify_token():
    global forwarding_site_global    
    
    GENERATE_SPOTIFY_TOKEN(request.args['code'])
    
    if forwarding_site_global == "dashboard":
        return redirect("http://" + GET_HOST_DEFAULT_NETWORK() + ":" + str(GET_HOST_PORT()) + "/dashboard#spotify")
        
    if forwarding_site_global == "spotify":
        return redirect(url_for('spotify'))
      

@app.route("/spotify/logout/url_target/<string:forwarding_site>")
@login_required
@permission_required
def spotify_logout(forwarding_site):

    DELETE_SPOTIFY_TOKEN()
    WRITE_LOGFILE_SYSTEM("SUCCESS", "Spotify | Logout") 
        
    if forwarding_site == "dashboard":
        return redirect("http://" + GET_HOST_DEFAULT_NETWORK() + ":" + str(GET_HOST_PORT()) + "/dashboard#spotify")
        
    if forwarding_site == "spotify":
        return redirect(url_for('spotify'))      
        
