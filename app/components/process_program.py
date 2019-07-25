import threading
import heapq
import time
import spotipy

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.shared_resources import process_management_queue
from app.components.mqtt import MQTT_CHECK_SETTING_THREAD, ZIGBEE2MQTT_CHECK_SETTING_THREAD
from app.components.backend_spotify import *


program_running = None
stop_program    = False
repeat_program  = False


def START_PROGRAM_THREAD(program_id):
    global program_running

    Thread = threading.Thread(target=PROGRAM_THREAD, args=(program_id, ))
    Thread.start()    
    
    program_name = GET_PROGRAM_BY_ID(program_id).name
    WRITE_LOGFILE_SYSTEM("EVENT", "Program - " + program_name + " | started") 
    program_running = program_name
    
    
def STOP_PROGRAM_THREAD():
    global stop_program, program_running, repeat_program
    stop_program    = True
    program_running = None
    repeat_program  = False
    
   
def REPEAT_PROGRAM_THREAD():
    global repeat_program
    repeat_program = True

    
def GET_REPEAT_PROGRAM():
    global repeat_program
    return repeat_program       

    
def GET_PROGRAM_RUNNING():
    global program_running
    return program_running   
   

def PROGRAM_THREAD(program_id):
    global stop_program, repeat_program, program_running

    try:
        content      = GET_PROGRAM_BY_ID(program_id).content
        program_name = GET_PROGRAM_BY_ID(program_id).name
        
        lines_total  = len(content.splitlines())
        repeat       = True

        while repeat == True:

            line_number = 1

            for line in content.splitlines():
                
                # stop program
                if stop_program == True:
                    stop_program = False
                    
                    WRITE_LOGFILE_SYSTEM("EVENT", "Program - " + program_name + " | stopped")
                    break
       
       
                else:
                    
                    # update program info
                    if repeat_program == True:
                        program_running = program_name + " ( " + str(line_number) + " | " + str(lines_total) + " | repeat )"
                    else:
                        program_running = program_name + " ( " + str(line_number) + " | " + str(lines_total) + " )"
                    
                    
                    # #######
                    #  break
                    # #######           
                            
                    if "pause" in line:
                            
                        line_content = line.split(" /// ")
                        time.sleep(int(line_content[1]))          
                        
                        
                    # ########
                    #  device
                    # ########
                             
                    if "device" in line:
                            
                        line_content = line.split(" /// ")
                        
                        try:
                              
                            device_name = line_content[1]    
                            device      = ""
                            device      = GET_MQTT_DEVICE_BY_NAME(device_name)         
                            
                            program_setting_formated = line_content[2]

                            # convert string to json-format
                            program_setting = program_setting_formated.replace(" ", "")
                            program_setting = program_setting.replace(':', '":"')
                            program_setting = program_setting.replace(',', '","')
                            program_setting = '{"' + str(program_setting) + '"}'                        
                                                         
                            # new device setting ?	
                            new_setting = False

                            if not "," in program_setting:
                                if not program_setting[1:-1] in device.last_values:
                                    new_setting = True

                            # more then one setting value:
                            else:	
                                program_setting_temp = program_setting[1:-1]
                                list_program_setting = program_setting_temp.split(",")

                                for setting in list_program_setting:

                                    if not setting in device.last_values:
                                        new_setting = True	

                            if new_setting == True:	

                                # mqtt
                                if device.gateway == "mqtt":

                                    channel  = "SmartHome/mqtt/" + device.ieeeAddr + "/set"                  
                                    msg      = program_setting

                                    heapq.heappush(process_management_queue, (30,  ("program", "device", channel, msg))) 

                                    MQTT_CHECK_SETTING_THREAD(device.ieeeAddr, program_setting, 5, 20)


                                # zigbee2mqtt
                                if device.gateway == "zigbee2mqtt":

                                    channel  = "SmartHome/zigbee2mqtt/" + device.name + "/set"                  
                                    msg      = program_setting

                                    heapq.heappush(process_management_queue, (30,  ("program", "device", channel, msg)))

                                    ZIGBEE2MQTT_CHECK_SETTING_THREAD(device.name, program_setting, 5, 20)      
                                
                                    
                            else:

                                if device.gateway == "mqtt":
                                    WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + device.name + " | " + program_setting_formated) 

                                if device.gateway == "zigbee2mqtt":
                                    WRITE_LOGFILE_SYSTEM("STATUS", "Zigbee2MQTT | Device - " + device.name + " | " + program_setting_formated)  		                           

                               
                        except:
                            WRITE_LOGFILE_SYSTEM("ERROR", "Program - " + program_name + " | Device - " +  device_name + " | not founded")
                   
   
                    # #####
                    #  led
                    # #####
                             
                    if "led" in line:
                            
                        line_content = line.split(" /// ")
                        
                        try:
                            led_name = line_content[1]    
                            led_type = GET_MQTT_DEVICE_BY_NAME(led_name).device_type
                            
                            
                            # setting led_rgb or led_white                      
                            if (led_type == "led_rgb" or led_type == "led_white") and line_content[2] != "off" and line_content[2] != "OFF": 
                                
                                led_color_setting = line_content[2]
                                led_brightness    = line_content[3]                      
                                heapq.heappush(process_management_queue, (30,  ("program", led_type, led_name, led_color_setting, led_brightness)))
                         
                         
                            # setting led_simple                           
                            elif led_type == "led_simple" and line_content[2] != "off" and line_content[2] != "OFF":       
                                        
                                led_brightness = line_content[2]                         
                                heapq.heappush(process_management_queue, (30,  ("program", led_type, led_name, led_brightness)))                        
                             
                               
                            # setting led turn_off   
                            else:  
                                    
                                heapq.heappush(process_management_queue, (30,  ("program", "turn_off", led_name)))                              
                          
                            
                        except:
                            WRITE_LOGFILE_SYSTEM("ERROR", "Program - " + program_name + " | LED - " + led_name + " | not founded")
                            

                    # #########
                    #  spotify
                    # #########
                             
                    if "spotify" in line:
                            
                        line_content = line.split(" /// ")

                        if GET_SPOTIFY_TOKEN() == "" and GET_SPOTIFY_REFRESH_TOKEN_TEMP() != "":
                            REFRESH_SPOTIFY_TOKEN()

                        spotify_token = GET_SPOTIFY_TOKEN()

                        # check spotify login 
                        if spotify_token != "":
                            
                            try:
                                
                                sp       = spotipy.Spotify(auth=spotify_token)
                                sp.trace = False
                                
                                
                                # basic control
                                
                                try:
                                
                                    spotify_device_id = sp.current_playback(market=None)['device']['id']
                                    spotify_volume    = sp.current_playback(market=None)['device']['volume_percent']

                                    if line_content[1].lower() == "play":
                                        SPOTIFY_CONTROL(spotify_token, "play", spotify_volume)       
                            
                                    if line_content[1].lower() == "previous":
                                        SPOTIFY_CONTROL(spotify_token, "previous", spotify_volume)   

                                    if line_content[1].lower() == "next":
                                        SPOTIFY_CONTROL(spotify_token, "next", spotify_volume)     

                                    if line_content[1].lower() == "stop": 
                                        SPOTIFY_CONTROL(spotify_token, "stop", spotify_volume)   

                                    if line_content[1].lower() == "volume":
                                        spotify_volume = int(line_content[2])
                                        SPOTIFY_CONTROL(spotify_token, "volume", spotify_volume)       
                                        
                                except:
                                    pass
                                    
                                    
                                # start playlist
                                        
                                if line_content[1].lower() == "playlist": 

                                    # get spotify_device_id
                                    device_name          = line_content[2]                                    
                                    list_spotify_devices = sp.devices()["devices"]  
                                    
                                    for device in list_spotify_devices:
                                        if device['name'].lower() == device_name.lower():
                                            spotify_device_id = device['id']  
                                            continue                                
                                    
                                    # get playlist_uri
                                    playlist_name          = line_content[3]
                                    list_spotify_playlists = sp.current_user_playlists(limit=20)["items"]
                                    
                                    for playlist in list_spotify_playlists:
                                        if playlist['name'].lower() == playlist_name.lower():
                                            playlist_uri = playlist['uri']
                                            continue
                                          
                                    # get volume
                                    playlist_volume = int(line_content[4])
                                    
                                    SPOTIFY_START_PLAYLIST(spotify_token, spotify_device_id, playlist_uri, playlist_volume)
                            
                            
                                # start track
                                        
                                if line_content[1].lower() == "track": 

                                    # get spotify_device_id
                                    device_name          = line_content[2]                                    
                                    list_spotify_devices = sp.devices()["devices"]  
                                    
                                    for device in list_spotify_devices:
                                        if device['name'].lower() == device_name.lower():
                                            spotify_device_id = device['id']  
                                            continue                                
                                    
                                    # get playlist_uri
                                    track_uri = SPOTIFY_SEARCH_TRACK(spotify_token, line_content[3], line_content[4], 1) [0][2]
                                          
                                    # get volume
                                    track_volume = int(line_content[5])
                                    
                                    SPOTIFY_START_TRACK(spotify_token, spotify_device_id, track_uri, track_volume)


                                # start album
                                        
                                if line_content[1].lower() == "album": 

                                    # get spotify_device_id
                                    device_name          = line_content[2]                                    
                                    list_spotify_devices = sp.devices()["devices"]  
                                    
                                    for device in list_spotify_devices:
                                        if device['name'].lower() == device_name.lower():
                                            spotify_device_id = device['id']  
                                            continue                                
                                    
                                    # get album_uri
                                    album_uri = SPOTIFY_SEARCH_ALBUM(spotify_token, line_content[3], line_content[4], 1) [0][2]
                                          
                                    # get volume
                                    album_volume = int(line_content[5])
                                    
                                    SPOTIFY_START_ALBUM(spotify_token, spotify_device_id, album_uri, album_volume)


                            except Exception as e:
                                WRITE_LOGFILE_SYSTEM("ERROR", "Programm - " + GET_PROGRAM_BY_ID(program_id).name + " | " + str(e))
                                print(str(e))  
        
                                        
                        else:
                            WRITE_LOGFILE_SYSTEM("ERROR", "Programm - " + GET_PROGRAM_BY_ID(program_id).name + " | No Spotify Token founded")   

                        
                    line_number = line_number + 1
                    time.sleep(1)
                    
                 
            # repeat program ?
            if repeat_program == True:        
                repeat = True
            else:
                repeat = False
                
        
        program_running = None    
        time.sleep(5)
        WRITE_LOGFILE_SYSTEM("SUCCESS", "Program - " + program_name + " | finished")
                

    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Programm - " + GET_PROGRAM_BY_ID(program_id).name + " | " + str(e))
        return str(e)
    
