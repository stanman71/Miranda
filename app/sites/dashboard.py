from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from functools import wraps

from app import app
from app.components.file_management import GET_LOGFILE_SYSTEM, GET_CONFIG_VERSION
from app.database.database import *
from app.components.checks import CHECK_DASHBOARD_CHECK_SETTINGS
from app.components.shared_resources import process_management_queue
from app.components.control_led import LED_GROUP_CHECK_SETTING_PROCESS
from app.components.mqtt import MQTT_CHECK_SETTING_PROCESS, ZIGBEE2MQTT_CHECK_SETTING_PROCESS
from app.components.process_program import *
from app.sites.spotify import authorization_header
from app.components.control_spotify import *

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
            return redirect(url_for('login'))
    return wrap


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@permission_required
def dashboard():
    error_message_led = []
    error_message_device = ""
    error_message_watering_control = ""
    error_message_log = ""
    error_message_start_program = ""
    checkbox_repeat_program = ""
    checkbox_type_event="checked"
    checkbox_type_status="checked"
    checkbox_type_success="checked"        
    checkbox_type_error="checked"
        
    # check sensor name changed ?
    UPDATE_DASHBOARD_CHECK_SENSOR_NAMES()
    
    
    """ ########### """
    """ led control """
    """ ########### """   
    
    
    if request.method == "POST":
        
        if request.form.get("change_led_settings") != None:
            
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
                            
                            scene = GET_LED_SCENE_BY_NAME(scene_name)
                            
                            heapq.heappush(process_management_queue, (1,  ("dashboard", "led_off_group", i))) 
                            error_message_led = LED_GROUP_CHECK_SETTING_PROCESS(i, scene.id, "OFF", 0, 2, 10)                                  
                            continue  
                            
                        else:
                            WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %")                        
     
                                
    """ ############## """
    """ device control """
    """ ############## """       
    
    
    if request.method == "POST":
    
        if request.form.get("change_device_settings") != None:
            
            for i in range (1,21):
                
                try:
                    
                    device = GET_MQTT_DEVICE_BY_ID(i)
                    
                    if device in GET_ALL_MQTT_DEVICES("device"):
                        
                        
                        # #################
                        #   Check Options
                        # #################

                        dashboard_check_option = request.form.get("set_dashboard_check_option_" + str(i))
                        dashboard_check_option = dashboard_check_option.replace(" ","")
                        
                        dashboard_check_setting = request.form.get("set_dashboard_check_setting_" + str(i))
                                               
                        if dashboard_check_setting == "" or dashboard_check_setting == None:
                            dashboard_check_setting = "None"  
                            
                        else:
                            
                            # format dashboard_check_setting
                            if "|" in dashboard_check_setting:
                                dashboard_check_setting = dashboard_check_setting.replace("|", ",")
                                
                            dashboard_check_setting = dashboard_check_setting.replace(" ", "")                            
                           
                                
                        # ######
                        # Sensor
                        # ######

                        if GET_MQTT_DEVICE_BY_NAME(dashboard_check_option) or dashboard_check_option.isdigit(): 

                            if dashboard_check_option.isdigit():        
                                dashboard_check_sensor_ieeeAddr     = GET_MQTT_DEVICE_BY_ID(dashboard_check_option).ieeeAddr
                                dashboard_check_sensor_input_values = GET_MQTT_DEVICE_BY_ID(dashboard_check_option).input_values       
                                dashboard_check_option              = GET_MQTT_DEVICE_BY_ID(dashboard_check_option).name
                                
                            else:
                                dashboard_check_sensor_ieeeAddr     = GET_MQTT_DEVICE_BY_NAME(dashboard_check_option).ieeeAddr
                                dashboard_check_sensor_input_values = GET_MQTT_DEVICE_BY_NAME(dashboard_check_option).input_values                                  
                        
                        
                            # set dashboard check value 1
                            if device.dashboard_check_option == "IP-Address":
                                dashboard_check_value_1 = "None" 
                        
                            else:
                                dashboard_check_value_1 = request.form.get("set_dashboard_check_value_1_" + str(i))

                                if dashboard_check_value_1 != None:                  
                                    dashboard_check_value_1 = dashboard_check_value_1.replace(" ", "")

                                    # replace array_position to sensor name 
                                    if dashboard_check_value_1.isdigit():
                                        
                                        # first two array elements are no sensors
                                        if dashboard_check_value_1 == "0" or dashboard_check_value_1 == "1":
                                            dashboard_check_value_1 = "None"
                                            
                                        else:           
                                            sensor_list             = GET_MQTT_DEVICE_BY_IEEEADDR(dashboard_check_sensor_ieeeAddr).inputs
                                            sensor_list             = sensor_list.split(",")
                                            dashboard_check_value_1 = sensor_list[int(dashboard_check_value_1)-2]
                                            
                                else:
                                   dashboard_check_value_1 = "None" 


                            # set dashboard check value 2
                            dashboard_check_value_2 = request.form.get("set_dashboard_check_value_2_" + str(i))
                            
                            if dashboard_check_value_2 == "" or dashboard_check_value_2 == None:
                                dashboard_check_value_2 = "None"       
                            
                            
                            # set dashboard check value 3
                            dashboard_check_value_3 = request.form.get("set_dashboard_check_value_3_" + str(i))
                            
                            if dashboard_check_value_3 == "" or dashboard_check_value_3 == None:
                                dashboard_check_value_3 = "None"       


                        # ##########
                        # IP Address
                        # ##########

                        elif dashboard_check_option == "IP-Address":
                            
                            # set dashboard check value 1
                            dashboard_check_value_1 = request.form.get("set_dashboard_check_value_1_" + str(i))
                           
                            if dashboard_check_value_1 == "" or dashboard_check_value_1 == None:
                                dashboard_check_value_1 = "None" 
                                  
                            dashboard_check_sensor_ieeeAddr     = "None"
                            dashboard_check_sensor_input_values = "None"
                            dashboard_check_value_2             = "None"                        
                            dashboard_check_value_3             = "None"   
               
                                                              
                        else:
                            
                            dashboard_check_option              = "None" 
                            dashboard_check_value_1             = "None" 
                            dashboard_check_value_2             = "None"  
                            dashboard_check_value_3             = "None"  
                            dashboard_check_sensor_ieeeAddr     = "None"
                            dashboard_check_sensor_input_values = "None"                                                            

                        SET_MQTT_DEVICE_DASHBOARD_CHECK(device.ieeeAddr, dashboard_check_option, dashboard_check_setting,
                                                        dashboard_check_sensor_ieeeAddr, dashboard_check_sensor_input_values, dashboard_check_value_1, 
                                                        dashboard_check_value_2, dashboard_check_value_3)
                    
                
                except Exception as e:
                    if "NoneType" not in str(e):
                        print(e)                        
                        
                            
                # ###############
                #  setting_value
                # ###############
                      
                try:  
                      
                    dashboard_setting = request.form.get("set_dashboard_setting_" + str(i))    

                    if dashboard_setting != "None" and dashboard_setting != None:
                        
                        
                        # format dashboard_setting
                        if "|" in dashboard_setting:
                            dashboard_setting = dashboard_setting.replace("|", ",")

                                                    
                        # new device setting ?
                        if dashboard_setting != device.previous_setting:
                            
                            change_state = True
                            
                            # ################
                            # check ip_address 
                            # ################
                            
                            if device.dashboard_check_option == "IP-Address" and dashboard_setting == device.dashboard_check_setting.replace(" ",""):

                                if ping(dashboard_check_value_1, timeout=1) != None:    
                                    error_message_device = device.name + " >>> Gerät ist noch eingeschaltet"
                                    change_state = False

                            # ############
                            # check sensor
                            # ############
                            
                            if device.dashboard_check_sensor_ieeeAddr != "None" and dashboard_setting == device.dashboard_check_setting.replace(" ",""):
                                
                                sensor_ieeeAddr = device.dashboard_check_sensor_ieeeAddr
                                sensor_key      = device.dashboard_check_value_1
                                
                                operator = device.dashboard_check_value_2
                                value    = device.dashboard_check_value_3
    
                                try:
                                     value = str(value).lower()
                                except:
                                     pass
                                         
                                
                                # get sensordata 
                                data         = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device.dashboard_check_sensor_ieeeAddr).last_values)
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
                                             
                                error_message_device = device.name + " >>> Sensor erteilt keine Freigabe"
                                                              
                                
                            # ##############    
                            # state changing
                            # ##############

                            if change_state == True: 

                                # mqtt
                                if device.gateway == "mqtt":
                                    
                                    channel  = "SmartHome/mqtt/" + device.ieeeAddr + "/set"                  
                                    msg      = dashboard_setting

                                    heapq.heappush(process_management_queue, (1, ("dashboard", "device", channel, msg)))   
                       
                                    error_message_device = MQTT_CHECK_SETTING_PROCESS(device.ieeeAddr, dashboard_setting, 1, 5)                                     
                                  

                                # zigbee2mqtt
                                if device.gateway == "zigbee2mqtt":
                                    
                                    channel  = "SmartHome/zigbee2mqtt/" + device.name + "/set"                  
                                    msg      = dashboard_setting

                                    heapq.heappush(process_management_queue, (1, ("dashboard", "device", channel, msg)))   
                       
                                    error_message_device = ZIGBEE2MQTT_CHECK_SETTING_PROCESS(device.name, dashboard_setting, 1, 5)                                        
                                
                        else:
                            
                            if device.gateway == "mqtt":
                                WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + device.name + " | " + str(dashboard_setting)) 

                            if device.gateway == "zigbee2mqtt":
                                WRITE_LOGFILE_SYSTEM("STATUS", "Zigbee2MQTT | Device - " + device.name + " | " + str(dashboard_setting))                                 
               
                   
                except Exception as e:
                    if "NoneType" not in str(e):
                        print(e)
           
           
    """ ############## """
    """ device control """
    """ ############## """       
    
    if request.method == "POST":
    
        if request.form.get("change_watering_control_settings") != None:

            for i in range (1,21):
                
                try:      
                    plant = GET_PLANT_BY_ID(i)
                    
                    watering_control_setting = request.form.get("set_watering_control_setting_" + str(i)) 
                    
                    if watering_control_setting != "None" and watering_control_setting != None:
       
       
                        # format watering_control_setting
                        if "|" in watering_control_setting:
                            watering_control_setting = watering_control_setting.replace("|", ",")
                            
                        watering_control_setting = watering_control_setting.replace(" ", "")
                        
                        
                        if watering_control_setting != plant.mqtt_device.previous_setting:

                            channel  = "SmartHome/" + plant.mqtt_device.gateway + "/" + plant.mqtt_device.ieeeAddr + "/set"                        
                            msg      = watering_control_setting.replace(" ", "")

                            heapq.heappush(process_management_queue, (1, ("dashboard", "device", channel, msg)))   
                       
                            error_message_watering_control = MQTT_CHECK_SETTING_PROCESS(plant.mqtt_device.ieeeAddr, watering_control_setting, 1, 5)                                     

                        else:
                            WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + plant.name + " | " + str(watering_control_setting)) 


                except Exception as e:
                    if "NoneType" not in str(e):
                        print(e)           
       
                       
    """ ############### """
    """ program control """
    """ ############### """              
           
    program_running = GET_PROGRAM_RUNNING() 
           
    # start program
    if request.form.get("start_program") != None:
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
        STOP_PROGRAM_THREAD()   

    program_running         = GET_PROGRAM_RUNNING()   
    dropdown_list_programs  = GET_ALL_PROGRAMS() 
    
    if GET_REPEAT_PROGRAM():
        checkbox_repeat_program = "checked"


    """ ############### """
    """ spotify control """
    """ ############### """   


    global authorization_header
    

    # check spotify login 
    try:
        
        sp              = spotipy.Spotify(auth=authorization_header)
        sp.trace        = False
        
        if request.method == "POST": 
            
            
            """ ####################### """
            """ spotify general control """
            """ ####################### """
        
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


    except Exception as e:
        print(e)
        tupel_current_playback = ""
        spotify_user = "Nicht eingeloggt"
        volume = 50       

    tupel_current_playback = ""
    spotify_user = "Nicht eingeloggt"
    
    
    """ ############### """
    """  log selection  """
    """ ############### """         
   
    # request settings
    if request.form.get("select_log_types") != None:
                   
        if request.form.get("type_event") == None:
            checkbox_type_event = ""       
        if request.form.get("type_status") == None:
            checkbox_type_status = ""    
        if request.form.get("type_error") == None:
            checkbox_type_error = ""    
        if request.form.get("type_success") == None:
            checkbox_type_success = ""    

    # create log types list
    selected_log_types = []
    
    if checkbox_type_event != "":
        selected_log_types.append("EVENT")
    if checkbox_type_status != "":
        selected_log_types.append("STATUS")
    if checkbox_type_success != "":
        selected_log_types.append("SUCCESS")           
    if checkbox_type_error != "":
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
    
    dropdown_list_check_options = ["IP-Address"] 
    dropdown_list_operators     = ["=", ">", "<"]
    
    data_device           = GET_ALL_MQTT_DEVICES("device")
    data_watering_control = GET_ALL_PLANTS()   
    data_sensor           = GET_ALL_MQTT_DEVICES("sensor")
    
    # remove watering_control sensors from list
    list_data_sensor = []
    
    for sensor in data_sensor:
        if sensor.device_type != "watering_control":
            list_data_sensor.append(sensor)
            
    data_sensor = list_data_sensor

    error_message_device_checks = CHECK_DASHBOARD_CHECK_SETTINGS(GET_ALL_MQTT_DEVICES("device"))

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


    return render_template('dashboard.html',
                            data_led=data_led,
                            dropdown_list_led_scenes=dropdown_list_led_scenes,
                            dropdown_list_check_options=dropdown_list_check_options,
                            dropdown_list_operators=dropdown_list_operators,
                            list_mqtt_devices=list_mqtt_devices,
                            data_device=data_device,
                            data_watering_control=data_watering_control,
                            data_log_system=data_log_system, 
                            data_sensor=data_sensor,
                            program_running=program_running,      
                            dropdown_list_programs=dropdown_list_programs,
                            checkbox_repeat_program=checkbox_repeat_program,
                            checkbox_type_event=checkbox_type_event,
                            checkbox_type_status=checkbox_type_status,
                            checkbox_type_success=checkbox_type_success,                            
                            checkbox_type_error=checkbox_type_error,
                            version=version,  
                            error_message_led=error_message_led,
                            error_message_log=error_message_log,  
                            error_message_device=error_message_device,   
                            error_message_watering_control=error_message_watering_control,  
                            error_message_device_checks=error_message_device_checks,
                            error_message_start_program=error_message_start_program,
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
                            tupel_current_playback=tupel_current_playback,
                            spotify_user=spotify_user, 
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
