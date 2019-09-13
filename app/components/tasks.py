from app import app
from app.components.backend_led import *
from app.database.database import *
from app.components.backend_watering import START_WATERING_THREAD
from app.components.mqtt import *
from app.components.file_management import SAVE_DATABASE, WRITE_LOGFILE_SYSTEM, GET_LOCATION_COORDINATES
from app.components.process_program import START_PROGRAM_THREAD, STOP_PROGRAM_THREAD, GET_PROGRAM_RUNNING
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL
from app.components.backend_spotify import *

from difflib import SequenceMatcher

import spotipy
import re


""" ################################ """
""" ################################ """
"""         controller tasks         """
""" ################################ """
""" ################################ """


def START_CONTROLLER_TASK(task, controller_name, controller_command):

    controller_command = controller_command[1:-1].replace('"','')

    # ###########
    # start scene
    # ###########

    if "scene" in task:

        task = task.lower()
        task = task.split(" /// ")
        
        group = GET_LED_GROUP_BY_NAME(task[1])
        scene = GET_LED_SCENE_BY_NAME(task[2])

        # group existing ?
        if group != None:

            # scene existing ?
            if scene != None:

                try:
                    brightness = int(task[3])
                except:
                    brightness = 100

                # new led setting ?
                if group.current_setting != scene.name or int(group.current_brightness) != brightness:
                    
                    SET_LED_GROUP_SCENE(group.id, scene.id, brightness)
                    CHECK_LED_GROUP_SETTING_THREAD(group.id, scene.id, scene.name, brightness, 2, 10)

                else:
                    WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name +
                                         " | " + scene.name + " : " + str(brightness))

            else:
                WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " +
                                     controller_command + " | Scene - " + task[2] + " | not founded")

        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " +
                                 controller_command + " | Group - " + task[1] + " | not founded")

    # #################
    # change brightness
    # #################

    if "brightness" in task:
        
        task = task.lower()
        task = task.split(" /// ")
        
        group   = GET_LED_GROUP_BY_NAME(task[1])
        command = task[2]

        # group existing ?
        if group != None:

            # command valid ?
            if command == "turn_up" or command == "turn_down":
                
                scene_name = group.current_setting

                # led_group off ?
                if scene_name != "off":
                    
                    scene = GET_LED_SCENE_BY_NAME(scene_name)

                    # get new brightness_value
                    current_brightness = group.current_brightness

                    if (command == "turn_up") and current_brightness != 100:
                        target_brightness = int(current_brightness) + 20

                        if target_brightness > 100:
                            target_brightness = 100

                        SET_LED_GROUP_BRIGHTNESS_DIMMER(group.id, "turn_up")
                        CHECK_LED_GROUP_SETTING_THREAD(group.id, scene.id, scene_name, target_brightness, 2, 10)

                    elif (command == "turn_down") and current_brightness != 0:

                        target_brightness = int(current_brightness) - 20

                        if target_brightness < 0:
                            target_brightness = 0

                        SET_LED_GROUP_BRIGHTNESS_DIMMER(group.id, "turn_down")
                        CHECK_LED_GROUP_SETTING_THREAD(group.id, scene.id, scene_name, target_brightness, 2, 10)

                    else:
                        WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name +
                                             " | " + scene_name + " : " + str(current_brightness) + " %")

                else:
                    WRITE_LOGFILE_SYSTEM("WARNING", "LED | Group - " +
                                         group.name + " | OFF : 0 %")

            else:
                WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " +
                                     controller_command + " | Command - " + task[2] + " | not valid")

        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " +
                                 controller_command + " | Group - " + task[1] + " | not founded")

    # #######
    # led off
    # #######

    if "led_off" in task:
        
        task = task.lower()
        task = task.split(" /// ")

        if task[1] == "group":

            # get input group names and lower the letters
            try:
                list_groups = task[2].split(",")
            except:
                list_groups = [task[2]]

            for input_group_name in list_groups:
                input_group_name = input_group_name.replace(" ", "")

                group_founded = False

            # get exist group names
            for group in GET_ALL_LED_GROUPS():

                if input_group_name == group.name.lower():
                    group_founded = True

                    # new led setting ?
                    if group.current_setting != "OFF":
                        scene_name = group.current_setting
                        scene = GET_LED_SCENE_BY_NAME(scene_name)

                        SET_LED_GROUP_TURN_OFF(group.id)
                        CHECK_LED_GROUP_SETTING_THREAD(group.id, scene.id, "OFF", 0, 2, 10)

                    else:
                        WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %")

            # group not founded
            if group_founded == False:
                WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " +
                                     controller_command + " | Group - " + input_group_name + " | not founded")

        if task[1] == "all":
            for group in GET_ALL_LED_GROUPS():

                # new led setting ?
                if group.current_setting != "OFF":
                    scene_name = group.current_setting
                    scene      = GET_LED_SCENE_BY_NAME(scene_name)

                    SET_LED_GROUP_TURN_OFF(group.id)
                    CHECK_LED_GROUP_SETTING_THREAD(group.id, scene.id, "OFF", 0, 2, 10)

            else:
                WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %")

    # ######
    # device
    # ######

    if "device" in task:
        task = task.split(" /// ")
        device = GET_MQTT_DEVICE_BY_NAME(task[1].lower())

        # device founded ?
        if device != None:
            
            controller_setting_formated = str(task[2:])
            controller_setting_formated = controller_setting_formated.replace("[", "")
            controller_setting_formated = controller_setting_formated.replace("]", "")
            controller_setting_formated = controller_setting_formated.replace("'", "")
            
            
            # check device exception
            check_result = CHECK_DEVICE_EXCEPTIONS(device.id, controller_setting_formated)
            
           
            if check_result == True:               
              
                # convert string to json-format
                controller_setting = controller_setting_formated.replace(' ', '')
                controller_setting = controller_setting.replace(':', '":"')
                controller_setting = controller_setting.replace(',', '","')
                controller_setting = '{"' + str(controller_setting) + '"}'
                    
                # new device setting ?  
                new_setting = False

                if not "," in controller_setting:
                    if not controller_setting[1:-1] in device.last_values:
                        new_setting = True
                                                                
                # more then one setting value:
                else:   
                    controller_setting_temp = controller_setting[1:-1]
                    list_controller_setting = controller_setting_temp.split(",")
                    
                    for setting in list_controller_setting:
                        
                        if not setting in device.last_values:
                            new_setting = True  


                if new_setting == True:             
                    
                    # mqtt
                    if device.gateway == "mqtt":
                        
                        channel  = "miranda/mqtt/" + device.ieeeAddr + "/set"                  
                        msg      = controller_setting

                        MQTT_PUBLISH(channel, msg)  
                        
                        CHECK_MQTT_SETTING_THREAD(device.ieeeAddr, controller_setting, 5, 20)


                    # zigbee2mqtt
                    if device.gateway == "zigbee2mqtt":
                        
                        channel  = "miranda/zigbee2mqtt/" + device.name + "/set"                  
                        msg      = controller_setting

                        MQTT_PUBLISH(channel, msg)  
                        
                        CHECK_ZIGBEE2MQTT_SETTING_THREAD(device.name, controller_setting, 5, 20)  
                             
                else:

                    if device.gateway == "mqtt":
                        WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + device.name + " | " + controller_setting_formated) 

                    if device.gateway == "zigbee2mqtt":
                        WRITE_LOGFILE_SYSTEM("STATUS", "Zigbee2MQTT | Device - " + device.name + " | " + controller_setting_formated)                   
                                                                

            else:
                WRITE_LOGFILE_SYSTEM("WARNING", "Controller - " + controller_name + " | " + check_result)
                                

        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | Gerät - " + task[1] + " | not founded")


    # ########
    # programs
    # ########

    if "program" in task:
        
        task = task.lower()
        task = task.split(" /// ")
        
        program = GET_PROGRAM_BY_NAME(task[1].lower())

        if program != None:
            program_running = GET_PROGRAM_RUNNING()

            if task[2] == "start" and program_running == None:
                START_PROGRAM_THREAD(program.id)
                
            elif task[2] == "start" and program_running != None:
                WRITE_LOGFILE_SYSTEM("WARNING", "Controller - " + controller_name + " | Command - " + controller_command + " | Other Program running")
                                     
            elif task[2] == "stop":
                STOP_PROGRAM_THREAD()
                
            else:
                WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | Command not valid")

        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | Program not founded")


    # #######
    # spotify
    # #######

    if "spotify" in task:
        
        spotify_token = GET_SPOTIFY_TOKEN()
        
        if spotify_token != "":
            
            task = task.lower()         
            task = task.split(" /// ")
            
            sp       = spotipy.Spotify(auth=spotify_token)
            sp.trace = False
            
            try:
                spotify_volume = sp.current_playback(market=None)['device']['volume_percent']
            except:
                spotify_volume = 50
            

            if task[1] == "play":
                SPOTIFY_CONTROL(spotify_token, "play", spotify_volume)       

            if task[1] == "previous": 
                SPOTIFY_CONTROL(spotify_token, "previous", spotify_volume)   

            if task[1] == "next":
                SPOTIFY_CONTROL(spotify_token, "next", spotify_volume)     

            if task[1] == "stop": 
                SPOTIFY_CONTROL(spotify_token, "stop", spotify_volume)      

            if task[1] == "turn_up":   
                SPOTIFY_CONTROL(spotify_token, "turn_up", spotify_volume)

            if task[1] == "turn_down":   
                SPOTIFY_CONTROL(spotify_token, "turn_down", spotify_volume)                 

            if task[1].lower() == "volume":
                spotify_volume = int(task[2])
                SPOTIFY_CONTROL(spotify_token, "volume", spotify_volume)  
                    

            # start playlist
                    
            if task[1].lower() == "playlist": 
                
                # get spotify_device_id
                device_name          = task[2]                                    
                list_spotify_devices = sp.devices()["devices"]  
                
                for device in list_spotify_devices:
                    if device['name'].lower() == device_name.lower():
                        spotify_device_id = device['id']  
                        continue                                
                
                # get playlist_uri
                playlist_name          = task[3]
                list_spotify_playlists = sp.current_user_playlists(limit=20)["items"]
                
                for playlist in list_spotify_playlists:
                    if playlist['name'].lower() == playlist_name.lower():
                        playlist_uri = playlist['uri']
                        continue
                        
                # get volume
                playlist_volume = int(task[4])
                
                SPOTIFY_START_PLAYLIST(spotify_token, spotify_device_id, playlist_uri, playlist_volume)
        
        
            # start track
                    
            if task[1].lower() == "track": 

                # get spotify_device_id
                device_name          = task[2]                                    
                list_spotify_devices = sp.devices()["devices"]  
                
                for device in list_spotify_devices:
                    if device['name'].lower() == device_name.lower():
                        spotify_device_id = device['id']  
                        continue                                
                
                # get playlist_uri
                track_uri = SPOTIFY_SEARCH_TRACK(spotify_token, task[3], task[4], 1) [0][2]
                      
                # get volume
                track_volume = int(task[5])
                
                SPOTIFY_START_TRACK(spotify_token, spotify_device_id, track_uri, track_volume)


            # start album
                    
            if task[1].lower() == "album": 

                # get spotify_device_id
                device_name          = task[2]                                    
                list_spotify_devices = sp.devices()["devices"]  
                
                for device in list_spotify_devices:
                    if device['name'].lower() == device_name.lower():
                        spotify_device_id = device['id']  
                        continue                                
                
                # get album_uri
                album_uri = SPOTIFY_SEARCH_ALBUM(spotify_token, task[3], task[4], 1) [0][2]
                      
                # get volume
                album_volume = int(task[5])
                
                SPOTIFY_START_ALBUM(spotify_token, spotify_device_id, album_uri, album_volume)

                
        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | No Spotify Token founded")
            

""" ################################ """
""" ################################ """
"""           scheduler tasks        """
""" ################################ """
""" ################################ """


def START_SCHEDULER_TASK(task_object):

    # ###########
    # start scene
    # ###########

    try:
        if "scene" in task_object.task:

            task = task_object.task.split(" /// ")
            
            group = GET_LED_GROUP_BY_NAME(task[1])
            scene = GET_LED_SCENE_BY_NAME(task[2])

            # group existing ?
            if group != None:

                # scene existing ?
                if scene != None:

                    try:
                        brightness = int(task[3])
                    except:
                        brightness = 100

                    # new led setting ?
                    if group.current_setting != scene.name or int(group.current_brightness) != brightness:
                        
                        WRITE_LOGFILE_SYSTEM("EVENT", 'Scheduler | Task - ' + task_object.name + ' | started')                      
                        
                        SET_LED_GROUP_SCENE(group.id, scene.id, brightness)
                        CHECK_LED_GROUP_SETTING_THREAD(group.id, scene.id, scene.name, brightness, 2, 10)


                else:
                    WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Scene - " + task[2] + " | not founded")

            else:
                WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Group - " + task[1] + " | not founded")


    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))


    # #######
    # led off
    # #######

    try:
        if "led_off" in task_object.task:
            
            task = task_object.task.split(" /// ")

            if task[1] == "group":

                # get input group names and lower the letters
                try:
                    list_groups = task[2].split(",")
                except:
                    list_groups = [task[2]]

                for input_group_name in list_groups: 
                    input_group_name = input_group_name.replace(" ", "")

                    group_founded = False

                    # get exist group names 
                    for group in GET_ALL_LED_GROUPS():

                        if input_group_name.lower() == group.name.lower():
                            group_founded = True   

                            # new led setting ?
                            if group.current_setting != "OFF":
                                
                                WRITE_LOGFILE_SYSTEM("EVENT", 'Scheduler | Task - ' + task_object.name + ' | started')                              
                                
                                SET_LED_GROUP_TURN_OFF(group.id)
                                CHECK_LED_GROUP_SETTING_THREAD(group.id, 0, "OFF", 0, 5, 20)   


                    if group_founded == False:
                        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Group - " + input_group_name + " | not founded")     


            if task[1] == "all" or task[1] == "ALL":

                for group in GET_ALL_LED_GROUPS():

                    # new led setting ?
                    if group.current_setting != "OFF":
                        scene_name = group.current_setting
                        scene      = GET_LED_SCENE_BY_NAME(scene_name)

                        WRITE_LOGFILE_SYSTEM("EVENT", 'Scheduler | Task - ' + task_object.name + ' | started')

                        SET_LED_GROUP_TURN_OFF(group.id)
                        CHECK_LED_GROUP_SETTING_THREAD(group.id, scene.id, "OFF", 0, 5, 20)    
                           

    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


    # ######
    # device
    # ######

    try:
        if "device" in task_object.task and "mqtt_update" not in task_object.task:
            
            task = task_object.task.split(" /// ")

            device = GET_MQTT_DEVICE_BY_NAME(task[1].lower())

            # device founded ?
            if device != None:
                scheduler_setting_formated = task[2]
                
                # check device exception
                check_result = CHECK_DEVICE_EXCEPTIONS(device.id, scheduler_setting_formated)
                
               
                if check_result == True:                         
                
                    # convert string to json-format
                    scheduler_setting = scheduler_setting_formated.replace(' ', '')
                    scheduler_setting = scheduler_setting.replace(':', '":"')
                    scheduler_setting = scheduler_setting.replace(',', '","')
                    scheduler_setting = '{"' + str(scheduler_setting) + '"}'                

                    # new device setting ?  
                    new_setting = False
                    
                    if not "," in scheduler_setting:
                        if not scheduler_setting[1:-1] in device.last_values:
                            new_setting = True
                                                                    
                    # more then one setting value:
                    else:   
                        scheduler_setting_temp = scheduler_setting[1:-1]
                        list_scheduler_setting = scheduler_setting_temp.split(",")
                        
                        for setting in list_scheduler_setting:
                            
                            if not setting in device.last_values:
                                new_setting = True  

                    
                    if new_setting == True:

                        WRITE_LOGFILE_SYSTEM("EVENT", 'Scheduler | Task - ' + task_object.name + ' | started')                              
                                                        
                        # mqtt
                        if device.gateway == "mqtt":
                            
                            channel  = "miranda/mqtt/" + device.ieeeAddr + "/set"                  
                            msg      = scheduler_setting

                            MQTT_PUBLISH(channel, msg)  
                            
                            CHECK_MQTT_SETTING_THREAD(device.ieeeAddr, scheduler_setting, 5, 20)


                        # zigbee2mqtt
                        if device.gateway == "zigbee2mqtt":
                            
                            channel  = "miranda/zigbee2mqtt/" + device.name + "/set"                  
                            msg      = scheduler_setting

                            MQTT_PUBLISH(channel, msg)  
                            
                            CHECK_ZIGBEE2MQTT_SETTING_THREAD(device.name, scheduler_setting, 5, 20)
                            
                else:
                    WRITE_LOGFILE_SYSTEM("WARNING", "Scheduler | Task - " + task_object.name + " | " + check_result)

            else:
                WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Device - " + task[1] + " | not founded")                  


    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))     


    # ########
    # programs
    # ########

    try:
        if "program" in task_object.task:
            
            task    = task_object.task.split(" /// ")
            program = GET_PROGRAM_BY_NAME(task[1].lower())

            if program != None:
                program_running = GET_PROGRAM_RUNNING() 

                if task[2] == "start" and program_running == None:
                    START_PROGRAM_THREAD(program.id)
                    
                elif task[2] == "start" and program_running != None:
                    WRITE_LOGFILE_SYSTEM("WARNING", "Scheduler | Task - " + task_object.name + " | Other Program running")  
                    
                elif task[2] == "stop":
                    STOP_PROGRAM_THREAD() 
                    
                else:
                    WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Command not valid")

            else:
                WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Program not founded")           


    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


    # ###############
    # watering plants
    # ###############

    try:
        if "watering_plants" in task_object.task:
            task = task_object.task.split(" /// ")
            group_number = task[1]
            START_WATERING_THREAD(group_number)


    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


    # #############
    # save database 
    # #############

    try:  
        if "save_database" in task_object.task:
            SAVE_DATABASE() 


    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))     


    # ###################
    # update mqtt devices
    # ###################

    try:
        if "mqtt_update_devices" in task_object.task:
            UPDATE_MQTT_DEVICES("mqtt")


    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


    # ##################
    # request sensordata
    # ##################

    try:
        if "request_sensordata" in task_object.task:
            task = task_object.task.split(" /// ")
            REQUEST_MQTT_SENSORDATA(task[1])  


    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))              


    # ##################
    #      spotify
    # ##################

    try:
        if "spotify" in task_object.task:
            task = task_object.task.split(" /// ")

            spotify_token = GET_SPOTIFY_TOKEN()

            # check spotify login 
            if spotify_token != "":
                
                sp       = spotipy.Spotify(auth=spotify_token)
                sp.trace = False
                
                
                # basic control
                
                try:
                
                    spotify_device_id = sp.current_playback(market=None)['device']['id']
                    spotify_volume    = sp.current_playback(market=None)['device']['volume_percent']

                    if task[1].lower() == "play":
                        SPOTIFY_CONTROL(spotify_token, "play", spotify_volume)       
            
                    if task[1].lower() == "previous":
                        SPOTIFY_CONTROL(spotify_token, "previous", spotify_volume)   

                    if task[1].lower() == "next":
                        SPOTIFY_CONTROL(spotify_token, "next", spotify_volume)     

                    if task[1].lower() == "stop": 
                        SPOTIFY_CONTROL(spotify_token, "stop", spotify_volume)   

                    if task[1].lower() == "volume":
                        spotify_volume = int(task[2])
                        SPOTIFY_CONTROL(spotify_token, "volume", spotify_volume)       
                        
                except:
                    pass
                    
                    
                # start playlist
                        
                if task[1].lower() == "playlist": 

                    # get spotify_device_id
                    device_name          = task[2]                                    
                    list_spotify_devices = sp.devices()["devices"]  
                    
                    for device in list_spotify_devices:
                        if device['name'].lower() == device_name.lower():
                            spotify_device_id = device['id']  
                            continue                                
                    
                    # get playlist_uri
                    playlist_name          = task[3]
                    list_spotify_playlists = sp.current_user_playlists(limit=20)["items"]
                    
                    for playlist in list_spotify_playlists:
                        if playlist['name'].lower() == playlist_name.lower():
                            playlist_uri = playlist['uri']
                            continue
                          
                    # get volume
                    playlist_volume = int(task[4])
                    
                    SPOTIFY_START_PLAYLIST(spotify_token, spotify_device_id, playlist_uri, playlist_volume)
            
            
                # start track
                        
                if task[1].lower() == "track": 

                    # get spotify_device_id
                    device_name          = task[2]                                    
                    list_spotify_devices = sp.devices()["devices"]  
                    
                    for device in list_spotify_devices:
                        if device['name'].lower() == device_name.lower():
                            spotify_device_id = device['id']  
                            continue                                
                    
                    # get playlist_uri
                    track_uri = SPOTIFY_SEARCH_TRACK(spotify_token, task[3], task[4], 1) [0][2]
                          
                    # get volume
                    track_volume = int(task[5])
                    
                    SPOTIFY_START_TRACK(spotify_token, spotify_device_id, track_uri, track_volume)


                # start album
                        
                if task[1].lower() == "album": 

                    # get spotify_device_id
                    device_name          = task[2]                                    
                    list_spotify_devices = sp.devices()["devices"]  
                    
                    for device in list_spotify_devices:
                        if device['name'].lower() == device_name.lower():
                            spotify_device_id = device['id']  
                            continue                                
                    
                    # get album_uri
                    album_uri = SPOTIFY_SEARCH_ALBUM(spotify_token, task[3], task[4], 1) [0][2]
                          
                    # get volume
                    album_volume = int(task[5])
                    
                    SPOTIFY_START_ALBUM(spotify_token, spotify_device_id, album_uri, album_volume)

        
            else:
                WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | No Spotify Token founded")   


    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))    


    # ####################################
    # remove scheduler task without repeat
    # ####################################

    if task_object.option_repeat != "checked":
        DELETE_SCHEDULER_TASK(task_object.id)



""" ################################ """
""" ################################ """
"""        speechcontrol tasks       """
""" ################################ """
""" ################################ """


def START_SPEECHCONTROL_TASK(answer):

    print(answer)

    # exception
    if ("could not understand audio" in answer) or ("Could not request results" in answer):
        WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Detection | " + answer)

    else:
        WRITE_LOGFILE_SYSTEM("EVENT", "Speechcontrol | Detection | " + answer)

        SPEECHCONTROL_LED_TASK(answer)
        SPEECHCONTROL_DEVICE_TASK(answer)
        SPEECHCONTROL_PROGRAM_TASK(answer)
        SPEECHCONTROL_SPOTIFY_TASK(answer)
        

# ############
# Check answer
# ############


def CHECK_SPEECHCONTROL_ANSWER(answer, keywords):
    
    if keywords != "":
    
        answer_words = answer.split()

        if "," in keywords:
            list_keywords = keywords.split(",")
        else:
            list_keywords = [keywords]


        for keyword in list_keywords:
            keyword_lengh = len(re.findall(r'\w+', keyword))

            # keyword group
            if keyword_lengh > 1:
                keyword_group = keyword.split()

                for keyword in keyword_group:
                    keyword = keyword.strip()

                    keyword_founded = False

                    for word in answer_words:
                        word = word.strip()

                        # keyword founded ?
                        if SequenceMatcher(None, keyword.lower(), word.lower()).ratio() > 0.75:
                            keyword_founded = True

                    if keyword_founded == False:
                        return False
                    
                return True

            # only one keyword
            else:
                for word in answer_words:
                    
                    # keyword founded ?
                    if SequenceMatcher(None, keyword.lower(), word.lower()).ratio() > 0.75:
                        return True


        return False
    
    else:
        return False 


# #########
# LED Tasks
# #########

def SPEECHCONTROL_LED_TASK(answer):

    table_numbers = {'fünf'           : 5,
                     'zehn'           : 10, 
                     'fünfzehn'       : 15,
                     'zwanzig'        : 20,
                     'fünfundzwanzig' : 25,
                     'dreizig'        : 30,
                     'dreissig'       : 30,                     
                     'fünfunddreizig' : 35,
                     'fünfunddreissig': 35,                     
                     'vierzig'        : 40,
                     'fünfundvierzig' : 45,
                     'fünfzig'        : 50,
                     'fünfundfünfzig' : 55,
                     'sechzig'        : 60,
                     'fünfundsechzig' : 65, 
                     'siebzig'        : 70,
                     'fünfundsiebzig' : 75,
                     'achtzig'        : 80,
                     'fünfundachtzig' : 85,
                     'neunzig'        : 90,
                     'fünfundneunzig' : 95,
                     'hundert'        : 100                            
                     }

    answer_words = answer.split()
    ratio_value  = int(GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_sensitivity) / 100

    
    # ###########
    # start scene 
    # ###########

    keywords = GET_SPEECHCONTROL_LED_TASK_BY_ID(1).keywords

    if CHECK_SPEECHCONTROL_ANSWER(answer, keywords) == True:

        try:
            groups = GET_ALL_LED_GROUPS()
            scenes = GET_ALL_LED_SCENES() 

            group_id   = None
            scene_id   = None
            brightness = 100

            # search group
            for group in groups:
                for word in answer_words:

                    if SequenceMatcher(None, group.name.lower(), word.lower()).ratio() > ratio_value:
                        group_id = group.id
                        continue

            # search scene
            for scene in scenes:
                for word in answer_words:
                    
                    if SequenceMatcher(None, scene.name.lower(), word.lower()).ratio() > ratio_value:
                        scene_id = scene.id
                        continue

            # search brightness value
            for element in answer.split():
                element = element.replace("%","")

                # check brightness as 'number' value
                if element.isdigit() and (1 <= int(element) <= 100):
                    brightness = int(element)
                    continue

                # check brightness as 'word' value
                try:
                    brightness = int(table_numbers[element])
                    continue
                except:
                    pass  


            # group founded ?
            if group_id != None: 

                # scene founded ?
                if scene_id != None:   
                    group = GET_LED_GROUP_BY_ID(group_id)
                    scene = GET_LED_SCENE_BY_ID(scene_id) 

                    # new led setting ?
                    if group.current_setting != scene.name or int(group.current_brightness) != brightness:
                        SET_LED_GROUP_SCENE(group.id, scene.id, brightness)
                        CHECK_LED_GROUP_SETTING_THREAD(group.id, scene.id, scene.name, brightness, 3, 15)     
                        time.sleep(1)
                        return                               

                    else:
                        WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | " + scene.name + " : " + str(brightness) + " %")     
                        return

                else:
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | Scene not founded")
                    return

            else:
                WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | Group not founded")
                return


        except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | " + str(e))  
            return


    # ##############
    # set brightness
    # ##############

    keywords = GET_SPEECHCONTROL_LED_TASK_BY_ID(2).keywords

    if CHECK_SPEECHCONTROL_ANSWER(answer, keywords) == True:
                
        try:        
            groups = GET_ALL_LED_GROUPS()

            group_id   = None
            brightness = None

            # search group
            for group in groups:
                for word in answer_words:

                    if SequenceMatcher(None, group.name.lower(), word.lower()).ratio() > ratio_value:
                        group_id = group.id
                        continue

            # search brightness value
            for element in answer.split():
                element = element.replace("%","")

                # check brightness as 'number' value
                if element.isdigit() and (1 <= int(element) <= 100):
                    brightness = int(element)
                    continue

                # check brightness as 'word' value
                try:
                    brightness = int(table_numbers[element])
                    continue
                except:
                    pass                    
            
            # group founded ?
            if group_id != None: 

                # brightness value founded ?
                if brightness != None:  
                    group = GET_LED_GROUP_BY_ID(group_id)

                    # led_group off ?
                    if group.current_setting != "OFF":
                        scene_name = group.current_setting
                        scene      = GET_LED_SCENE_BY_NAME(scene_name)                            

                        # new led brightness setting ?
                        if group.current_brightness != brightness:
                            
                            SET_LED_GROUP_BRIGHTNESS(group.id, brightness)
                            CHECK_LED_GROUP_SETTING_THREAD(group.id, scene.id, scene_name, brightness, 3, 15)  
                            time.sleep(1)
                            return                                       

                        else:
                            WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | " + scene_name + " : " + str(brightness) + " %") 
                            return  

                    else:
                        WRITE_LOGFILE_SYSTEM("WARNING", "LED | Group - " + group.name + " | OFF : 0 %") 
                        return                                     

                else:
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | Brightness value not founded")
                    return
                    
            else:
                WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | Group not founded")
                return

        except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | " + str(e))    
            return


    # ##################
    # turn off led group
    # ##################

    keywords = GET_SPEECHCONTROL_LED_TASK_BY_ID(3).keywords

    if CHECK_SPEECHCONTROL_ANSWER(answer, keywords) == True:

        try:
            groups = GET_ALL_LED_GROUPS()
            
            founded_groups = []

            # search group
            for group in groups:
                for word in answer_words:

                    if SequenceMatcher(None, group.name.lower(), word.lower()).ratio() > ratio_value:
                        founded_groups.append(group)        


            # group founded
            if founded_groups != []:

                for group in founded_groups:
                    scene_name = group.current_setting
                    scene      = GET_LED_SCENE_BY_NAME(scene_name)

                    # new led setting ?
                    if group.current_setting != "OFF":
                        SET_LED_GROUP_TURN_OFF(group.id)
                        CHECK_LED_GROUP_SETTING_THREAD(group.id, scene.id, "OFF", 0, 3, 15)  
                        time.sleep(1)
                        return                                       

                    else:
                        WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %")  
                        return                       

            else:
                WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | No Group founded")
                return                        


        except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | " + str(e))    
            return


    # #################
    # turn off all leds
    # #################

    keywords = GET_SPEECHCONTROL_LED_TASK_BY_ID(4).keywords

    if CHECK_SPEECHCONTROL_ANSWER(answer, keywords) == True:
        
        try:
            # check all led groups
            for group in GET_ALL_LED_GROUPS():
                scene_name = group.current_setting
                scene      = GET_LED_SCENE_BY_NAME(scene_name)

                # new led setting ?
                if group.current_setting != "OFF":
                    SET_LED_GROUP_TURN_OFF(group.id)
                    CHECK_LED_GROUP_SETTING_THREAD(group.id, scene.id, "OFF", 0, 3, 15)   
                    time.sleep(1)
                    return                              

                else:
                    WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %") 
                    return

        except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | " + str(e))    
            return


# ############
# Device Tasks
# ############                   

def SPEECHCONTROL_DEVICE_TASK(answer):

    answer_words = answer.split()
    ratio_value  = int(GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_sensitivity) / 100

    for task in GET_ALL_SPEECHCONTROL_DEVICE_TASKS():

        if CHECK_SPEECHCONTROL_ANSWER(answer, task.keywords) == True:
        
            try:
                device = GET_MQTT_DEVICE_BY_IEEEADDR(task.mqtt_device_ieeeAddr)

                # device founded ?
                if device != None:
                    speechcontrol_setting_formated = task.setting
                    
                    # check device exception
                    check_result = CHECK_DEVICE_EXCEPTIONS(device.id, speechcontrol_setting_formated)
                    
                   
                    if check_result == True:    
                    
                        # convert string to json-format
                        speechcontrol_setting = speechcontrol_setting_formated.replace(' ', '')
                        speechcontrol_setting = speechcontrol_setting.replace(':', '":"')
                        speechcontrol_setting = speechcontrol_setting.replace(',', '","')
                        speechcontrol_setting = '{"' + str(speechcontrol_setting) + '"}'        

                        # new device setting ?  
                        new_setting = False
                        
                        if not "," in speechcontrol_setting:
                            if not speechcontrol_setting[1:-1] in device.last_values:
                                new_setting = True
                                                                        
                        # more then one setting value:
                        else:   
                            speechcontrol_setting_temp = speechcontrol_setting[1:-1]
                            list_speechcontrol_setting = speechcontrol_setting_temp.split(",")
                            
                            for setting in list_speechcontrol_setting:
                                
                                if not setting in device.last_values:
                                    new_setting = True  


                        if new_setting == True:

                            # mqtt
                            if device.gateway == "mqtt":
                                
                                channel  = "miranda/mqtt/" + device.ieeeAddr + "/set"                  
                                msg      = speechcontrol_setting

                                MQTT_PUBLISH(channel, msg)  
                                CHECK_MQTT_SETTING_THREAD(device.ieeeAddr, speechcontrol_setting, 5, 20)
                                return
                                
                                
                            # zigbee2mqtt
                            if device.gateway == "zigbee2mqtt":
                                
                                channel  = "miranda/zigbee2mqtt/" + device.name + "/set"                  
                                msg      = speechcontrol_setting

                                MQTT_PUBLISH(channel, msg)  
                                CHECK_ZIGBEE2MQTT_SETTING_THREAD(device.name, speechcontrol_setting, 5, 20)   
                                return

                        else:
                            
                            if device.gateway == "mqtt":
                                WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + device.name + " | " + speechcontrol_setting_formated) 
                                return

                            if device.gateway == "zigbee2mqtt":
                                WRITE_LOGFILE_SYSTEM("STATUS", "Zigbee2MQTT | Device - " + device.name + " | " + speechcontrol_setting_formated) 
                                return                                       


                    else:
                        WRITE_LOGFILE_SYSTEM("WARNING", "Speechcontrol | Device Task | " + answer + " | " + check_result)                     

                else:
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Device Task | " + answer + " | Device not founded")
                    return                             


            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Device Task | " + answer + " | " + str(e))      
                return                    



# #############
# Program Tasks
# #############                   

def SPEECHCONTROL_PROGRAM_TASK(answer):

    answer_words = answer.split()
    ratio_value  = int(GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_sensitivity) / 100
    
    for task in GET_ALL_SPEECHCONTROL_PROGRAM_TASKS():

        if CHECK_SPEECHCONTROL_ANSWER(answer, task.keywords) == True:
                    
            try:
                program = GET_PROGRAM_BY_ID(task.program_id)

                # program founded ?
                if program != None:
                    command = task.command.lower()
                    command = command.replace(" ", "")

                    program_running = GET_PROGRAM_RUNNING() 

                    if command == "start" and program_running == None:
                        START_PROGRAM_THREAD(program.id)
                        return
                        
                    elif command == "start" and program_running != None:
                        WRITE_LOGFILE_SYSTEM("WARNING", "Speechcontrol | Program Task | " + answer + " | Other Program running")    
                        return  
                                    
                    elif command == "stop":
                        STOP_PROGRAM_THREAD() 
                        return
                        
                    else:
                        WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Program Task | " + answer + " | Command not valid")
                        return

                else:
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Program Task | " + answer + " | Program not founded")    
                    return       

            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Program Task | " + answer + " | " + str(e))   
                return 


def SPEECHCONTROL_SPOTIFY_TASK(answer):
    
    table_numbers = {'fünf'           : 5,
                     'zehn'           : 10, 
                     'fünfzehn'       : 15,
                     'zwanzig'        : 20,
                     'fünfundzwanzig' : 25,
                     'dreizig'        : 30,
                     'dreissig'       : 30,                     
                     'fünfunddreizig' : 35,
                     'fünfunddreissig': 35,     
                     'vierzig'        : 40,
                     'fünfundvierzig' : 45,
                     'fünfzig'        : 50,
                     'fünfundfünfzig' : 55,
                     'sechzig'        : 60,
                     'fünfundsechzig' : 65, 
                     'siebzig'        : 70,
                     'fünfundsiebzig' : 75,
                     'achtzig'        : 80,
                     'fünfundachtzig' : 85,
                     'neunzig'        : 90,
                     'fünfundneunzig' : 95,
                     'hundert'        : 100                            
                     }
                        

    answer_words = answer.split()
    ratio_value  = int(GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_sensitivity) / 100

    
    # ##############
    # start playlist 
    # ##############

    keywords = GET_SPEECHCONTROL_SPOTIFY_TASK_BY_ID(1).keywords

    if CHECK_SPEECHCONTROL_ANSWER(answer, keywords) == True:    
        spotify_token = GET_SPOTIFY_TOKEN()
                
        if spotify_token != "": 

            sp             = spotipy.Spotify(auth=spotify_token)
            sp.trace       = False              

            try:
                list_spotify_devices   = sp.devices()["devices"] 
                list_spotify_playlists = sp.current_user_playlists(limit=20)["items"]

                spotify_device_id    = None
                spotify_playlist_uri = None
                playlist_volume      = 50

                # search spotify device
                for device in list_spotify_devices:
                    for word in answer_words:

                        if SequenceMatcher(None, device["name"].lower(), word.lower()).ratio() > ratio_value:
                            spotify_device_id = device["id"]
                            continue

                # search playlist
                for playlist in list_spotify_playlists:
                    for word in answer_words:
                        
                        if SequenceMatcher(None, playlist["name"].lower(), word.lower()).ratio() > ratio_value:
                            spotify_playlist_uri = playlist["uri"]
                            continue

                # search volume value
                for element in answer.split():
                    element = element.replace("%","")

                    # check brightness as 'number' value
                    if element.isdigit() and (1 <= int(element) <= 100):
                        volume = int(element)
                        continue

                    # check volume as 'word' value
                    try:
                        playlist_volume = int(table_numbers[element])
                        continue
                    except:
                        pass  
    

                # device founded ?
                if spotify_device_id != None: 

                    # playlist founded ?
                    if spotify_playlist_uri != None:   
                                                        
                        SPOTIFY_START_PLAYLIST(spotify_token, spotify_device_id, spotify_playlist_uri, playlist_volume)
                        
                    else:
                        WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | Playlist not founded")
                        return

                else:
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | Device not founded") 
                    return   
                        
                        
            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | " + str(e))   
                return                       


        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | No Spotify Token founded")   
            return   



    # ####
    # play  
    # ####

    keywords = GET_SPEECHCONTROL_SPOTIFY_TASK_BY_ID(2).keywords

    if CHECK_SPEECHCONTROL_ANSWER(answer, keywords) == True:    
        spotify_token = GET_SPOTIFY_TOKEN()
        
        if spotify_token != "": 

            sp             = spotipy.Spotify(auth=spotify_token)
            sp.trace       = False      
            spotify_volume = sp.current_playback(market=None)['device']['volume_percent']       

            try:

                SPOTIFY_CONTROL(spotify_token, "play", spotify_volume)
                        
                                                    
            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | " + str(e))   
                return                       


        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | No Spotify Token founded")   
            return   
                    
                    
    # ########
    # previous  
    # ########

    keywords = GET_SPEECHCONTROL_SPOTIFY_TASK_BY_ID(3).keywords

    if CHECK_SPEECHCONTROL_ANSWER(answer, keywords) == True:    
        spotify_token = GET_SPOTIFY_TOKEN()
        
        if spotify_token != "": 

            sp             = spotipy.Spotify(auth=spotify_token)
            sp.trace       = False      
            spotify_volume = sp.current_playback(market=None)['device']['volume_percent']       

            try:

                SPOTIFY_CONTROL(spotify_token, "previous", spotify_volume)
                        
                                                    
            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | " + str(e))   
                return                       


        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | No Spotify Token founded")   
            return   
            
                    
    # ####
    # next  
    # ####

    keywords = GET_SPEECHCONTROL_SPOTIFY_TASK_BY_ID(4).keywords

    if CHECK_SPEECHCONTROL_ANSWER(answer, keywords) == True:    
        spotify_token = GET_SPOTIFY_TOKEN()
        
        if spotify_token != "": 

            sp             = spotipy.Spotify(auth=spotify_token)
            sp.trace       = False      
            spotify_volume = sp.current_playback(market=None)['device']['volume_percent']       

            try:

                SPOTIFY_CONTROL(spotify_token, "next", spotify_volume)
                        
                                                    
            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | " + str(e))   
                return                       


        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | No Spotify Token founded")   
            return   
            
                    
    # ####
    # stop  
    # ####

    keywords = GET_SPEECHCONTROL_SPOTIFY_TASK_BY_ID(5).keywords

    if CHECK_SPEECHCONTROL_ANSWER(answer, keywords) == True:
        spotify_token = GET_SPOTIFY_TOKEN()
        
        if spotify_token != "": 

            sp             = spotipy.Spotify(auth=spotify_token)
            sp.trace       = False      
            spotify_volume = sp.current_playback(market=None)['device']['volume_percent']       

            try:

                SPOTIFY_CONTROL(spotify_token, "stop", spotify_volume)
                        
                                                    
            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | " + str(e))   
                return                       


        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | No Spotify Token founded")   
            return                                          



    # ######
    # volume  
    # ######

    keywords = GET_SPEECHCONTROL_SPOTIFY_TASK_BY_ID(6).keywords

    if CHECK_SPEECHCONTROL_ANSWER(answer, keywords) == True:
        spotify_token = GET_SPOTIFY_TOKEN()
        
        if spotify_token != "": 

            sp             = spotipy.Spotify(auth=spotify_token)
            sp.trace       = False      
            spotify_volume = sp.current_playback(market=None)['device']['volume_percent']       

            try:
                
                volume = 0
                
                # search volume value
                for element in answer.split():
                    element = element.replace("%","")

                    # check brightness as 'number' value
                    if element.isdigit() and (1 <= int(element) <= 100):
                        volume = int(element)
                        continue

                    # check volume as 'word' value
                    try:
                        volume = int(table_numbers[element])
                        continue
                    except:
                        pass    
                        
                if spotify_volume != volume:                        
                    SPOTIFY_CONTROL(spotify_token, "volume", volume)
                        
                                                    
            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | " + str(e))   
                return                       


        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Spotify Task | " + answer + " | No Spotify Token founded")   
            return   


