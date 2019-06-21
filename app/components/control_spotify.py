from app import app
from app.database.database import *

import requests
import json
import spotipy
import socket 


def GET_SPOTIFY_CURRENT_PLAYBACK(authorization_header):

	sp       = spotipy.Spotify(auth=authorization_header)
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
