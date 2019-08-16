from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm 
from flask_mobility.decorators import mobile_template

from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from functools import wraps

from app import app
from app.components.file_management import GET_LOGFILE_SYSTEM, GET_CONFIG_VERSION
from app.database.database import *
from app.components.checks import CHECK_DASHBOARD_EXCEPTION_SETTINGS
from app.components.shared_resources import process_management_queue
from app.components.backend_led import LED_GROUP_CHECK_SETTING_PROCESS
from app.components.mqtt import MQTT_CHECK_SETTING_PROCESS, ZIGBEE2MQTT_CHECK_SETTING_PROCESS
from app.components.process_program import *
from app.components.backend_spotify import *

from ping3 import ping

import heapq
import json


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


# access rights
def permission_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.permission_dashboard == "checked":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('logout'))
    return wrap


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@mobile_template('{mobile/}dashboard.html')
@permission_required
def dashboard(template):
    error_message_led = []
    error_message_devices = ""
    error_message_watering_control = ""
    error_message_log = ""
    error_message_start_program = ""
    error_message_spotify = ""
    
    checkbox_repeat_program = ""
    
    selected_type_event    = "selected"
    selected_type_status   = "selected"
    selected_type_database = "selected"    
    selected_type_success  = "selected"   
    selected_type_warning  = "selected"                                                      
    selected_type_error    = "selected"
    
    collapse_dashboard_led      = ""
    collapse_dashboard_devices  = ""         
    collapse_dashboard_watering = ""
    collapse_dashboard_programs = "" 
    collapse_dashboard_spotify  = ""
    collapse_dashboard_log      = ""        
    
        
    # exception sensor name changed ?
    UPDATE_DASHBOARD_EXCEPTION_SENSOR_NAMES()
   
    """ ########### """
    """ led control """
    """ ########### """   
    
    if request.method == "POST":
        
        if request.form.get("change_led_settings") != None:
            
            collapse_dashboard_led = "in"
            
            # set collapse settings
            if request.form.get("checkbox_collapse_led"): 
                collapse_dashboard_led_setting = "checked"
            else:
                collapse_dashboard_led_setting = ""
   
            SET_USER_DASHBOARD_COLLAPSE_SETTING(current_user.id, "led", collapse_dashboard_led_setting)


            for i in range (1,21):

                # set led group
                if request.form.get("set_group_" + str(i)) != None:  

                    group        = GET_LED_GROUP_BY_ID(i)
                    setting      = request.form.get("set_group_" + str(i)) 
                    setting_type = setting.split("_")[0]
                    brightness   = request.form.get("set_brightness_" + str(i))   
                    

                    # start scene
                    if setting_type == "scene":
                        scene_id   = int(setting.split("_")[1])
                        scene_name = GET_LED_SCENE_BY_ID(scene_id).name
                        
                        # new led setting ?
                        if group.current_setting != scene_name:

                            heapq.heappush(process_management_queue, (1,  ("dashboard", "led_scene", i, scene_id, int(brightness))))
                             
                            error_message_led = LED_GROUP_CHECK_SETTING_PROCESS(i, scene_id, scene_name, int(brightness), 2, 10)          
                            continue     
                         
                        else:
                            WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | " + scene_name + " : " + str(brightness) + " %")                             
                        
                        
                    # change brightness only
                    if GET_LED_GROUP_BY_ID(i).current_setting != "OFF" and setting != "turn_off":                 
                        
                        scene_name = GET_LED_GROUP_BY_ID(i).current_setting
                        
                        # led_group off ?
                        if scene_name != "OFF":
                        
                            # new led setting ?
                            if int(brightness) != group.current_brightness and scene_name != "OFF":
                                
                                heapq.heappush(process_management_queue, (1,  ("dashboard", "led_brightness", i, int(brightness))))
                    
                                scene             = GET_LED_SCENE_BY_NAME(scene_name)
                                error_message_led = LED_GROUP_CHECK_SETTING_PROCESS(i, scene.id, scene_name, int(brightness), 2, 10) 
                                continue   
                                
                            else:
                                WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | " + scene_name + " : " + str(brightness) + " %")                              
                                                                
                        else:
                            WRITE_LOGFILE_SYSTEM("WARNING", "LED | Group - " + group.name + " | OFF : 0 %")                              
                            error_message_led = (group.name + " >>> Gruppe ist nicht eingeschaltet")                 
    
    
                    # turn led group off
                    if setting == "turn_off":  
                        
                        scene_name = GET_LED_GROUP_BY_ID(i).current_setting
                        
                        # new led setting ?
                        if scene_name != "OFF":

                            heapq.heappush(process_management_queue, (1,  ("dashboard", "led_off_group", i))) 
                            error_message_led = LED_GROUP_CHECK_SETTING_PROCESS(i, 0, "OFF", 0, 2, 10)                                  
                            continue  
                            
                        else:
                            WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %")                        
     
                                
    """ ############## """
    """ device control """
    """ ############## """       
    
    
    if request.method == "POST":
    
        if request.form.get("change_device_settings") != None:
            
            collapse_dashboard_devices = "in"
     
            # set collapse settings
            if request.form.get("checkbox_collapse_devices"): 
                collapse_dashboard_devices_setting = "checked"
            else:
                collapse_dashboard_devices_setting = ""
   
            SET_USER_DASHBOARD_COLLAPSE_SETTING(current_user.id, "devices", collapse_dashboard_devices_setting)
     
            
            for i in range (1,21):
                
                try:
                        
                    device = GET_MQTT_DEVICE_BY_ID(i)
                    
                    if device in GET_ALL_MQTT_DEVICES("device"):
                        
                        
                        # ####################
                        #   Exception Options
                        # ####################

                        dashboard_exception_option = request.form.get("set_dashboard_exception_option_" + str(i))
                        dashboard_exception_option = dashboard_exception_option.replace(" ","")

                        
                        if request.MOBILE == False:

                            dashboard_exception_setting = request.form.get("set_dashboard_exception_setting_" + str(i))
                                                   
                            if dashboard_exception_setting == "" or dashboard_exception_setting == None:
                                dashboard_exception_setting = "None"  
              
                            # ######
                            # Sensor
                            # ######

                            if GET_MQTT_DEVICE_BY_NAME(dashboard_exception_option) or dashboard_exception_option.isdigit(): 

                                if dashboard_exception_option.isdigit():        
                                    dashboard_exception_sensor_ieeeAddr     = GET_MQTT_DEVICE_BY_ID(dashboard_exception_option).ieeeAddr
                                    dashboard_exception_sensor_input_values = GET_MQTT_DEVICE_BY_ID(dashboard_exception_option).input_values       
                                    dashboard_exception_option              = GET_MQTT_DEVICE_BY_ID(dashboard_exception_option).name
                                    
                                else:
                                    dashboard_exception_sensor_ieeeAddr     = GET_MQTT_DEVICE_BY_NAME(dashboard_exception_option).ieeeAddr
                                    dashboard_exception_sensor_input_values = GET_MQTT_DEVICE_BY_NAME(dashboard_exception_option).input_values                                  
                            
                                # set dashboard exception value 1
                                if device.dashboard_exception_option == "IP-Address":
                                    dashboard_exception_value_1 = "None" 
                            
                                else:
                                    dashboard_exception_value_1 = request.form.get("set_dashboard_exception_value_1_" + str(i))

                                    if dashboard_exception_value_1 != None:                  
                                        dashboard_exception_value_1 = dashboard_exception_value_1.replace(" ", "")

                                        # replace array_position to sensor name 
                                        if dashboard_exception_value_1.isdigit():
                                            
                                            # first two array elements are no sensors
                                            if dashboard_exception_value_1 == "0" or dashboard_exception_value_1 == "1":
                                                dashboard_exception_value_1 = "None"
                                                
                                            else:           
                                                sensor_list                 = GET_MQTT_DEVICE_BY_IEEEADDR(dashboard_exception_sensor_ieeeAddr).input_values
                                                sensor_list                 = sensor_list.split(",")
                                                dashboard_exception_value_1 = sensor_list[int(dashboard_exception_value_1)-2]
                                                
                                    else:
                                       dashboard_exception_value_1 = "None" 


                                # set dashboard exception value 2
                                dashboard_exception_value_2 = request.form.get("set_dashboard_exception_value_2_" + str(i))
                                
                                if dashboard_exception_value_2 == "" or dashboard_exception_value_2 == None:
                                    dashboard_exception_value_2 = "None"       
                                
                                
                                # set dashboard exception value 3
                                dashboard_exception_value_3 = request.form.get("set_dashboard_exception_value_3_" + str(i))
                                
                                if dashboard_exception_value_3 == "" or dashboard_exception_value_3 == None:
                                    dashboard_exception_value_3 = "None"       


                            # ##########
                            # IP Address
                            # ##########

                            elif dashboard_exception_option == "IP-Address":
                                
                                # set dashboard exception value 1
                                dashboard_exception_value_1 = request.form.get("set_dashboard_exception_value_1_" + str(i))
                               
                                if dashboard_exception_value_1 == "" or dashboard_exception_value_1 == None:
                                    dashboard_exception_value_1 = "None" 
                                      
                                dashboard_exception_sensor_ieeeAddr     = "None"
                                dashboard_exception_sensor_input_values = "None"
                                dashboard_exception_value_2             = "None"                        
                                dashboard_exception_value_3             = "None"   
                   
                                                                  
                            else:
                                
                                dashboard_exception_option              = "None" 
                                dashboard_exception_value_1             = "None" 
                                dashboard_exception_value_2             = "None"  
                                dashboard_exception_value_3             = "None"  
                                dashboard_exception_sensor_ieeeAddr     = "None"
                                dashboard_exception_sensor_input_values = "None"                                                            

                            SET_MQTT_DEVICE_DASHBOARD_EXCEPTION(device.ieeeAddr, dashboard_exception_option, dashboard_exception_setting,
                                                                dashboard_exception_sensor_ieeeAddr, dashboard_exception_sensor_input_values,
                                                                dashboard_exception_value_1, dashboard_exception_value_2, dashboard_exception_value_3)
                        
                        
                        else:
                            
                            if dashboard_exception_option == "None":
                            
                                dashboard_exception_setting             = "None" 
                                dashboard_exception_value_1             = "None" 
                                dashboard_exception_value_2             = "None"  
                                dashboard_exception_value_3             = "None"  
                                dashboard_exception_sensor_ieeeAddr     = "None"
                                dashboard_exception_sensor_input_values = "None"                                                            

                                SET_MQTT_DEVICE_DASHBOARD_EXCEPTION(device.ieeeAddr, dashboard_exception_option, dashboard_exception_setting,
                                                                    dashboard_exception_sensor_ieeeAddr, dashboard_exception_sensor_input_values,
                                                                    dashboard_exception_value_1, dashboard_exception_value_2, dashboard_exception_value_3)                        
                
                except Exception as e:
                    if "NoneType" not in str(e):
                        print(e)                        
               
                            
                # ###############
                #  setting_value
                # ###############
                      
                try:  
                      
                    dashboard_setting = request.form.get("set_dashboard_setting_" + str(i))  

                    if dashboard_setting != "None" and dashboard_setting != None:
                                
                        change_state = True
                        
                        # convert json-format to string
                        dashboard_setting_formated = dashboard_setting.replace('"', '')
                        dashboard_setting_formated = dashboard_setting_formated.replace('{', '')
                        dashboard_setting_formated = dashboard_setting_formated.replace('}', '')                                                    
                        
                        # ####################
                        # exception ip_address 
                        # ####################
                        
                        if device.dashboard_exception_option == "IP-Address" and device.dashboard_exception_setting == dashboard_setting_formated:

                            if ping(dashboard_exception_value_1, timeout=1) != None:    
                                error_message_devices = device.name + " >>> Gerät ist noch eingeschaltet"
                                change_state = False

                        # ################
                        # exception sensor
                        # ################
                        
                        if device.dashboard_exception_sensor_ieeeAddr != "None" and device.dashboard_exception_setting == dashboard_setting_formated:
                            
                            sensor_ieeeAddr = device.dashboard_exception_sensor_ieeeAddr
                            sensor_key      = device.dashboard_exception_value_1
                            
                            operator = device.dashboard_exception_value_2
                            value    = device.dashboard_exception_value_3

                            try:
                                 value = str(value).lower()
                            except:
                                 pass
                                     
                            
                            # get sensordata 
                            data         = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device.dashboard_exception_sensor_ieeeAddr).last_values)
                            sensor_value = data[sensor_key]
                            
                            try:
                                 sensor_value = str(sensor_value).lower()
                            except:
                                 pass
                            
                                  
                            # compare conditions
                            if operator == "=" and value.isdigit():
                                if int(sensor_value) == int(value):
                                    change_state = False    
                                else:
                                    change_state = True
                                    
                            if operator == "=" and not value.isdigit():
                                if str(sensor_value) == str(value):
                                    change_state = False
                                else:
                                    change_state = True
                                    
                            if operator == "<" and value.isdigit():
                                if int(sensor_value) < int(value):
                                    change_state = False
                                else:
                                    change_state = True
                                    
                            if operator == ">" and value.isdigit():
                                if int(sensor_value) > int(value):
                                    change_state = False 
                                else:
                                    change_state = True
                                         
                            error_message_devices = device.name + " >>> Sensor erteilt keine Freigabe"
                                                          
                            
                        # ##############    
                        # state changing
                        # ##############

                        if change_state == True: 
                            
                            # new device setting ?  
                            new_setting       = False
                            dashboard_setting = dashboard_setting.replace(' ', '')
                            
                            if not "," in dashboard_setting:
                                if not dashboard_setting[1:-1] in device.last_values:
                                    new_setting = True
                                                                            
                            # more then one setting value:
                            else:   
                                dashboard_setting_temp = dashboard_setting[1:-1]
                                list_dashboard_setting = dashboard_setting_temp.split(",")
                                
                                for setting in list_dashboard_setting:
                                    
                                    if not setting in device.last_values:
                                        new_setting = True   
                            
                            if new_setting == True:

                                # mqtt
                                if device.gateway == "mqtt":
                                    
                                    channel  = "SmartHome/mqtt/" + device.ieeeAddr + "/set"                  
                                    msg      = dashboard_setting

                                    heapq.heappush(process_management_queue, (1, ("dashboard", "device", channel, msg)))   
                       
                                    error_message_devices = MQTT_CHECK_SETTING_PROCESS(device.ieeeAddr, dashboard_setting, 1, 5)                                     
                                  

                                # zigbee2mqtt
                                if device.gateway == "zigbee2mqtt":
                                    
                                    channel  = "SmartHome/zigbee2mqtt/" + device.name + "/set"                  
                                    msg      = dashboard_setting

                                    heapq.heappush(process_management_queue, (1, ("dashboard", "device", channel, msg)))   
                       
                                    error_message_devices = ZIGBEE2MQTT_CHECK_SETTING_PROCESS(device.name, dashboard_setting, 1, 5)      
                              
                                    
                            else:

                                if device.gateway == "mqtt":
                                    WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + device.name + " | " + dashboard_setting_formated) 

                                if device.gateway == "zigbee2mqtt":
                                    WRITE_LOGFILE_SYSTEM("STATUS", "Zigbee2MQTT | Device - " + device.name + " | " + dashboard_setting_formated)    
                                    
                 
                except Exception as e:
                    if "NoneType" not in str(e):
                        print(e)
           
           
    """ ################ """
    """ watering control """
    """ ################ """       
    
    if request.method == "POST":
    
        if request.form.get("change_watering_control_settings") != None:
            
            collapse_dashboard_watering = "in"
            
            # set collapse settings
            if request.form.get("checkbox_collapse_watering"): 
                collapse_dashboard_watering_setting = "checked"
            else:
                collapse_dashboard_watering_setting = ""
   
            SET_USER_DASHBOARD_COLLAPSE_SETTING(current_user.id, "watering", collapse_dashboard_watering_setting)
                 

            for i in range (1,21):
                
                try:      
                    plant = GET_PLANT_BY_ID(i)
                    
                    watering_control_setting = request.form.get("set_watering_control_setting_" + str(i))                         
                                                  
                    if watering_control_setting != "None" and watering_control_setting != None:
                        
                        # convert json-format to string
                        watering_control_setting_formated = watering_control_setting.replace('"', '')
                        watering_control_setting_formated = watering_control_setting_formated.replace('{', '')
                        watering_control_setting_formated = watering_control_setting_formated.replace('}', '')   
                        
                        # new watering setting ?    
                        new_setting              = False
                        watering_control_setting = watering_control_setting.replace(' ', '')
                        
                        if not "," in watering_control_setting:
                            if not watering_control_setting[1:-1] in plant.mqtt_device.last_values:
                                new_setting = True
                                                                        
                        # more then one setting value:
                        else:   
                            watering_control_setting_temp = watering_control_setting[1:-1]
                            list_watering_control_setting = watering_control_setting_temp.split(",")
                            
                            for setting in list_watering_control_setting:
                                
                                if not setting in plant.mqtt_device.last_values:
                                    new_setting = True   
                        
                        if new_setting == True:                             
       
                            channel  = "SmartHome/" + plant.mqtt_device.gateway + "/" + plant.mqtt_device.ieeeAddr + "/set"                        
                            msg      = watering_control_setting

                            heapq.heappush(process_management_queue, (1, ("dashboard", "device", channel, msg)))   
                       
                            error_message_watering_control = MQTT_CHECK_SETTING_PROCESS(plant.mqtt_device.ieeeAddr, watering_control_setting, 1, 5)                                     

                        else:
                                
                            WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + plant.mqtt_device.name + " | " + watering_control_setting_formated) 


                except Exception as e:
                    if "NoneType" not in str(e):
                        print(e)           
       
                       
    """ ############### """
    """ program control """
    """ ############### """              
           
    program_running = GET_PROGRAM_RUNNING() 
           
    # start program
    if request.form.get("start_program") != None:
        
        collapse_dashboard_programs = "in" 
        
        program_id = request.form.get("get_program_id")
        
        if program_id != "None" and program_running == None:
            START_PROGRAM_THREAD(program_id) 
            
            # repeat program ?
            if GET_PROGRAM_RUNNING() != None:
                if request.form.get("repeat_program"):
                    REPEAT_PROGRAM_THREAD()            
            
        elif program_id != "None" and program_running != None:
            error_message_start_program = "Anderes Programm läuft bereits >>> " + program_running 
            
        else:
            error_message_start_program = "Kein Programm ausgewählt"

    # stop program    
    if request.form.get("stop_program") != None:
        
        collapse_dashboard_programs = "in" 
        
        STOP_PROGRAM_THREAD()   

    program_running         = GET_PROGRAM_RUNNING()   
    dropdown_list_programs  = GET_ALL_PROGRAMS() 
    
    if GET_REPEAT_PROGRAM():
        checkbox_repeat_program = "checked"


    """ ############### """
    """ spotify control """
    """ ############### """   
        
    spotify_token = GET_SPOTIFY_TOKEN()
    
    if spotify_token != "":
        
        try:
            
            collapse_dashboard_spotify = "in" 

            sp       = spotipy.Spotify(auth=spotify_token)
            sp.trace = False
            
            if request.method == "POST": 
                
                
                """ ####################### """
                """ spotify general control """
                """ ####################### """
            
                try:
            
                    spotify_device_id = sp.current_playback(market=None)['device']['id']
                    spotify_volume    = request.form.get("get_spotify_volume")
                        
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
                    
                except:
                    pass
                 
                    
                """ ################# """
                """ spotify playlists """
                """ ################# """                        
                            
                            
                if "spotify_start_playlist" in request.form:    
                    spotify_device_id = request.form.get("spotify_start_playlist")
                    playlist_uri      = request.form.get("set_spotify_playlist:" + spotify_device_id)
                    playlist_volume = request.form.get("set_spotify_playlist_volume:" + spotify_device_id)
                    
                    if playlist_volume == None:
                        playlist_volume = 50

                    SPOTIFY_START_PLAYLIST(spotify_token, spotify_device_id, playlist_uri, playlist_volume)     


            """ ############ """
            """ account data """
            """ ############ """   
                      
            spotify_user           = sp.current_user()["display_name"]   
            spotify_devices        = sp.devices()["devices"]        
            spotify_playlists      = sp.current_user_playlists(limit=20)["items"]                                 
            tupel_current_playback = GET_SPOTIFY_CURRENT_PLAYBACK(spotify_token) 
            
            
            # set volume
            try:
                spotify_current_playback_volume = sp.current_playback(market=None)['device']['volume_percent']
                volume = spotify_current_playback_volume    
                
            except:
                volume = 50
           
               
        # login problems                
        except Exception as e:
            WRITE_LOGFILE_SYSTEM("ERROR", "Spotify | " + str(e)) 
            
            tupel_current_playback = ""
            spotify_user = ""
            spotify_playlists = ""
            spotify_devices = ""
            volume = 50                
    

    else:
        
        tupel_current_playback = ""
        spotify_user = ""
        spotify_playlists = ""
        spotify_devices = ""
        volume = 50    
       
       
    """ ############### """
    """  log selection  """
    """ ############### """  
    
    # create log types list
    selected_log_types = ["EVENT", "STATUS", "DATABASE", "SUCCESS", "WARNING", "ERROR"]     
   
    # change log selection 
    if request.form.get("select_log_types") != None:   
        
        collapse_dashboard_log = "in" 
        
        selected_type_event    = ""
        selected_type_status   = ""
        selected_type_database = ""        
        selected_type_success  = ""   
        selected_type_warning  = ""                                                     
        selected_type_error    = ""      
        
        selected_log_types = [] 
   
        list_selection = request.form.getlist('get_log_settings[]')
        
        for element in list_selection:
            
            if element == "EVENT":
                selected_type_event = "selected"
                selected_log_types.append("EVENT")
            if element == "STATUS":
                selected_type_status = "selected"
                selected_log_types.append("STATUS")    
            if element == "DATABASE":
                selected_type_database = "selected"
                selected_log_types.append("DATABASE")                               
            if element == "SUCCESS":
                selected_type_success = "selected"
                selected_log_types.append("SUCCESS")                
            if element == "WARNING":
                selected_type_warning = "selected"
                selected_log_types.append("WARNING")                
            if element == "ERROR":
                selected_type_error = "selected"
                selected_log_types.append("ERROR")     


    # get log entries
    if GET_LOGFILE_SYSTEM(selected_log_types, 15) is not None:
        data_log_system = GET_LOGFILE_SYSTEM(selected_log_types, 15)
        
    else:
        data_log_system = ""
        error_message_log = "Keine Einträge gefunden"    
    
    
    """ ############### """
    """ general control """
    """ ############### """       
    

    data_led = GET_ALL_ACTIVE_LED_GROUPS()
    dropdown_list_led_scenes = GET_ALL_LED_SCENES()

    list_mqtt_devices = GET_ALL_MQTT_DEVICES("sensor")
    
    dropdown_list_exception_options = ["IP-Address"] 
    dropdown_list_operators         = ["=", ">", "<"]
    
    data_device           = GET_ALL_MQTT_DEVICES("device")
    data_watering_control = GET_ALL_PLANTS()   
    data_sensor           = GET_ALL_MQTT_DEVICES("sensor")
    
    # remove watering_control sensors from list
    list_data_sensor = []
    
    for sensor in data_sensor:
        if sensor.device_type != "watering_control":
            list_data_sensor.append(sensor)
            
    data_sensor = list_data_sensor

    error_message_device_exceptions = CHECK_DASHBOARD_EXCEPTION_SETTINGS(GET_ALL_MQTT_DEVICES("device"))

    version = GET_CONFIG_VERSION()       

    # get sensor list
    try:
        mqtt_device_1_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(1).input_values
        mqtt_device_1_input_values = mqtt_device_1_input_values.replace(" ", "")
    except:
        mqtt_device_1_input_values = ""
    try:
        mqtt_device_2_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(2).input_values
        mqtt_device_2_input_values = mqtt_device_2_input_values.replace(" ", "")
    except:
        mqtt_device_2_input_values = ""
    try:        
        mqtt_device_3_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(3).input_values
        mqtt_device_3_input_values = mqtt_device_3_input_values.replace(" ", "")
    except:
        mqtt_device_3_input_values = ""
    try:        
        mqtt_device_4_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(4).input_values
        mqtt_device_4_input_values = mqtt_device_4_input_values.replace(" ", "")
    except:
        mqtt_device_4_input_values = ""
    try:        
        mqtt_device_5_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(5).input_values
        mqtt_device_5_input_values = mqtt_device_5_input_values.replace(" ", "")
    except:
        mqtt_device_5_input_values = ""
    try:        
        mqtt_device_6_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(6).input_values
        mqtt_device_6_input_values = mqtt_device_6_input_values.replace(" ", "")
    except:
        mqtt_device_6_input_values = ""
    try:        
        mqtt_device_7_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(7).input_values
        mqtt_device_7_input_values = mqtt_device_7_input_values.replace(" ", "")
    except:
        mqtt_device_7_input_values = ""
    try:        
        mqtt_device_8_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(8).input_values
        mqtt_device_8_input_values = mqtt_device_8_input_values.replace(" ", "")
    except:
        mqtt_device_8_input_values = ""
    try:        
        mqtt_device_9_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(9).input_values
        mqtt_device_9_input_values = mqtt_device_9_input_values.replace(" ", "")
    except:
        mqtt_device_9_input_values = ""
    try:        
        mqtt_device_10_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(10).input_values
        mqtt_device_10_input_values = mqtt_device_10_input_values.replace(" ", "")
    except:
        mqtt_device_10_input_values = ""
    try:        
        mqtt_device_11_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(11).input_values
        mqtt_device_11_input_values = mqtt_device_11_input_values.replace(" ", "")
    except:
        mqtt_device_11_input_values = ""
    try:        
        mqtt_device_12_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(12).input_values
        mqtt_device_12_input_values = mqtt_device_12_input_values.replace(" ", "")
    except:
        mqtt_device_12_input_values = ""
    try:        
        mqtt_device_13_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(13).input_values
        mqtt_device_13_input_values = mqtt_device_13_input_values.replace(" ", "")
    except:
        mqtt_device_13_input_values = ""
    try:        
        mqtt_device_14_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(14).input_values
        mqtt_device_14_input_values = mqtt_device_14_input_values.replace(" ", "")
    except:
        mqtt_device_14_input_values = ""
    try:        
        mqtt_device_15_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(15).input_values
        mqtt_device_15_input_values = mqtt_device_15_input_values.replace(" ", "")
    except:
        mqtt_device_15_input_values = ""    
    try:        
        mqtt_device_16_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(16).input_values
        mqtt_device_16_input_values = mqtt_device_16_input_values.replace(" ", "")
    except:
        mqtt_device_16_input_values = ""
    try:        
        mqtt_device_17_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(17).input_values
        mqtt_device_17_input_values = mqtt_device_17_input_values.replace(" ", "")
    except:
        mqtt_device_17_input_values = ""
    try:        
        mqtt_device_18_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(18).input_values
        mqtt_device_18_input_values = mqtt_device_18_input_values.replace(" ", "")
    except:
        mqtt_device_18_input_values = ""
    try:        
        mqtt_device_19_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(19).input_values
        mqtt_device_19_input_values = mqtt_device_19_input_values.replace(" ", "")
    except:
        mqtt_device_19_input_values = ""
    try:        
        mqtt_device_20_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(20).input_values
        mqtt_device_20_input_values = mqtt_device_20_input_values.replace(" ", "")
    except:
        mqtt_device_20_input_values = ""   
    try:        
        mqtt_device_21_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(21).input_values
        mqtt_device_21_input_values = mqtt_device_21_input_values.replace(" ", "")
    except:
        mqtt_device_21_input_values = ""   
    try:        
        mqtt_device_22_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(22).input_values
        mqtt_device_22_input_values = mqtt_device_22_input_values.replace(" ", "")
    except:
        mqtt_device_22_input_values = ""   
    try:        
        mqtt_device_23_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(23).input_values
        mqtt_device_23_input_values = mqtt_device_23_input_values.replace(" ", "")
    except:
        mqtt_device_23_input_values = ""   
    try:        
        mqtt_device_24_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(24).input_values
        mqtt_device_24_input_values = mqtt_device_24_input_values.replace(" ", "")
    except:
        mqtt_device_24_input_values = ""   
    try:        
        mqtt_device_25_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(25).input_values
        mqtt_device_25_input_values = mqtt_device_25_input_values.replace(" ", "")
    except:
        mqtt_device_25_input_values = ""           


    return render_template(template,
                            data_led=data_led,
                            dropdown_list_led_scenes=dropdown_list_led_scenes,
                            dropdown_list_exception_options=dropdown_list_exception_options,
                            dropdown_list_operators=dropdown_list_operators,
                            list_mqtt_devices=list_mqtt_devices,
                            data_device=data_device,
                            data_watering_control=data_watering_control,
                            data_log_system=data_log_system, 
                            data_sensor=data_sensor,
                            program_running=program_running,      
                            dropdown_list_programs=dropdown_list_programs,
                            checkbox_repeat_program=checkbox_repeat_program,
                            spotify_user=spotify_user,  
                            tupel_current_playback=tupel_current_playback,
                            spotify_playlists=spotify_playlists,
                            spotify_devices=spotify_devices,  
                            volume=volume,                              
                            selected_type_event=selected_type_event,
                            selected_type_status=selected_type_status,
                            selected_type_database=selected_type_database,                            
                            selected_type_success=selected_type_success,    
                            selected_type_warning=selected_type_warning,                                                      
                            selected_type_error=selected_type_error,
                            version=version,  
                            error_message_led=error_message_led,
                            error_message_log=error_message_log,  
                            error_message_devices=error_message_devices,   
                            error_message_watering_control=error_message_watering_control,  
                            error_message_device_exceptions=error_message_device_exceptions,
                            error_message_start_program=error_message_start_program,
                            error_message_spotify=error_message_spotify,
                            mqtt_device_1_input_values=mqtt_device_1_input_values,
                            mqtt_device_2_input_values=mqtt_device_2_input_values,
                            mqtt_device_3_input_values=mqtt_device_3_input_values,
                            mqtt_device_4_input_values=mqtt_device_4_input_values,
                            mqtt_device_5_input_values=mqtt_device_5_input_values,
                            mqtt_device_6_input_values=mqtt_device_6_input_values,
                            mqtt_device_7_input_values=mqtt_device_7_input_values,
                            mqtt_device_8_input_values=mqtt_device_8_input_values,
                            mqtt_device_9_input_values=mqtt_device_9_input_values,
                            mqtt_device_10_input_values=mqtt_device_10_input_values,
                            mqtt_device_11_input_values=mqtt_device_11_input_values,
                            mqtt_device_12_input_values=mqtt_device_12_input_values,
                            mqtt_device_13_input_values=mqtt_device_13_input_values,
                            mqtt_device_14_input_values=mqtt_device_14_input_values,
                            mqtt_device_15_input_values=mqtt_device_15_input_values,
                            mqtt_device_16_input_values=mqtt_device_16_input_values,
                            mqtt_device_17_input_values=mqtt_device_17_input_values,
                            mqtt_device_18_input_values=mqtt_device_18_input_values,
                            mqtt_device_19_input_values=mqtt_device_19_input_values,
                            mqtt_device_20_input_values=mqtt_device_20_input_values,  
                            mqtt_device_21_input_values=mqtt_device_21_input_values,
                            mqtt_device_22_input_values=mqtt_device_22_input_values,  
                            mqtt_device_23_input_values=mqtt_device_23_input_values,
                            mqtt_device_24_input_values=mqtt_device_24_input_values,
                            mqtt_device_25_input_values=mqtt_device_25_input_values,
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system, 
                            collapse_dashboard_led_setting=current_user.collapse_dashboard_led_setting,
                            collapse_dashboard_devices_setting=current_user.collapse_dashboard_devices_setting,          
                            collapse_dashboard_watering_setting=current_user.collapse_dashboard_watering_setting,
                            collapse_dashboard_led=collapse_dashboard_led,
                            collapse_dashboard_devices=collapse_dashboard_devices,          
                            collapse_dashboard_watering=collapse_dashboard_watering,                      
                            collapse_dashboard_programs=collapse_dashboard_programs, 
                            collapse_dashboard_spotify=collapse_dashboard_spotify,
                            collapse_dashboard_log=collapse_dashboard_log,                                                
                            )
