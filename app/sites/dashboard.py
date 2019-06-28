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


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    error_message_led = []
    error_message_device = ""
    error_message_log = ""
    error_message_start_program = ""
    checkbox_repeat_program = ""
    checkbox = ""
        
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
                        
                        dashboard_check_setting_value = request.form.get("set_dashboard_check_setting_value_" + str(i))
                        
                        if dashboard_check_setting_value == "" or dashboard_check_setting_value == None:
                            dashboard_check_setting_value = "None"  
                           
                                
                        # ######
                        # Sensor
                        # ######

                        if GET_MQTT_DEVICE_BY_NAME(dashboard_check_option) or dashboard_check_option.isdigit(): 

                            if dashboard_check_option.isdigit():        
                                dashboard_check_sensor_ieeeAddr = GET_MQTT_DEVICE_BY_ID(dashboard_check_option).ieeeAddr
                                dashboard_check_sensor_inputs   = GET_MQTT_DEVICE_BY_ID(dashboard_check_option).inputs       
                                dashboard_check_option          = GET_MQTT_DEVICE_BY_ID(dashboard_check_option).name
                                
                            else:
                                dashboard_check_sensor_ieeeAddr = GET_MQTT_DEVICE_BY_NAME(dashboard_check_option).ieeeAddr
                                dashboard_check_sensor_inputs   = GET_MQTT_DEVICE_BY_NAME(dashboard_check_option).inputs                                  
                        
                        
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
                                  
                            dashboard_check_sensor_ieeeAddr = "None"
                            dashboard_check_sensor_inputs   = "None"
                            dashboard_check_value_2         = "None"                        
                            dashboard_check_value_3         = "None"   
               
                                                              
                        else:
                            
                            dashboard_check_option          = "None" 
                            dashboard_check_value_1         = "None" 
                            dashboard_check_value_2         = "None"  
                            dashboard_check_value_3         = "None"  
                            dashboard_check_sensor_ieeeAddr = "None"
                            dashboard_check_sensor_inputs   = "None"                                                            

                        SET_MQTT_DEVICE_DASHBOARD_CHECK(device.ieeeAddr, dashboard_check_option, dashboard_check_setting_value,
                                                        dashboard_check_sensor_ieeeAddr, dashboard_check_sensor_inputs, dashboard_check_value_1, 
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

                        dashboard_setting_key   = dashboard_setting.split("=")[0]
                        dashboard_setting_key   = dashboard_setting_key.replace(" ","")                                         
                        dashboard_setting_value = dashboard_setting.split("=")[1]
                        dashboard_setting_value = dashboard_setting_value.replace(" ","")
                    
                    
                        # new device setting ?
                        if dashboard_setting_value != device.previous_setting_value:
                            
                            change_state = True
                            
                            
                            # ################
                            # check ip_address 
                            # ################
                            
                            if device.dashboard_check_option == "IP-Address" and dashboard_setting_value == device.dashboard_check_setting_value.replace(" ",""):

                                if ping(dashboard_check_value_1, timeout=1) != None:    
                                    error_message_device = device.name + " >>> Gerät ist noch eingeschaltet"
                                    change_state = False
                                

                            # ############
                            # check sensor
                            # ############
                            
                            if device.dashboard_check_sensor_ieeeAddr != "None" and dashboard_setting_value == device.dashboard_check_setting_value.replace(" ",""):
                                
                                sensor_ieeeAddr = device.dashboard_check_sensor_ieeeAddr
                                sensor_key      = device.dashboard_check_value_1
                                
                                operator = device.dashboard_check_value_2
                                value    = device.dashboard_check_value_3
                                
                                # get sensordata 
                                data         = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device.dashboard_check_sensor_ieeeAddr).last_values)
                                sensor_value = data[sensor_key]
                                
                                
                                # compare conditions
                                if operator == "=" and not value.isdigit():
                                    if str(sensor_value) == str(value):
                                        change_state = False
                                    else:
                                        change_state = True
                                    
                                if operator == "=" and value.isdigit():
                                    if int(sensor_value) == int(value):
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

                                # ####
                                # mqtt
                                # ####
                                
                                if device.gateway == "mqtt":
                                    
                                    channel  = "SmartHome/" + device.gateway + "/" + device.ieeeAddr + "/set"
                                    msg      = '{"' + dashboard_setting_key + '":"' + dashboard_setting_value + '"}'
                                    
                                    heapq.heappush(process_management_queue, (1, ("dashboard", "device", channel, msg)))    
                                                    
                                    error_message_device = MQTT_CHECK_SETTING_PROCESS(device.ieeeAddr, dashboard_setting_key, dashboard_setting_value, 1, 5)                                     

                                  
                                # ###########
                                # zigbee2mqtt
                                # ###########    
                                    
                                if device.gateway == "zigbee2mqtt":
                                    
                                    channel = "SmartHome/" + device.gateway + "/" + device.name + "/set"
                                    msg     = '{"' + dashboard_setting_key + '":"' + dashboard_setting_value + '"}'
                                    
                                    heapq.heappush(process_management_queue, (1, ("dashboard", "device", channel, msg)))                                          
                                    
                                    error_message_device = ZIGBEE2MQTT_CHECK_SETTING_PROCESS(device.name, dashboard_setting_key, dashboard_setting_value, 1, 5)      
                                            
                                continue  
                              
                                
                            else:
                                
                                if device.gateway == "mqtt":
                                    WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + device.name + " | " + str(dashboard_setting_value)) 

                                if device.gateway == "zigbee2mqtt":
                                    WRITE_LOGFILE_SYSTEM("STATUS", "Zigbee2MQTT | Device - " + device.name + " | " + str(dashboard_setting_value))                                 
                   


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
                else:
                    NOT_REPEAT_PROGRAM_THREAD()             
            
        elif program_id != "None" and program_running != None:
            error_message_start_program = "Anderes Programm läuft bereits >>> " + program_running 
            
        else:
            error_message_start_program = "Kein Programm ausgewählt"

    # stop program    
    if request.form.get("stop_program") != None:
        STOP_PROGRAM_THREAD()   


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
    """ general control """
    """ ############### """       
    

    data_led = GET_ALL_ACTIVE_LED_GROUPS()
    dropdown_list_led_scenes = GET_ALL_LED_SCENES()

    list_mqtt_devices = GET_ALL_MQTT_DEVICES("sensor")
    
    dropdown_list_check_options = ["IP-Address"] 
    dropdown_list_operators     = ["=", ">", "<"]
    
    data_device = GET_ALL_MQTT_DEVICES("device")
    data_sensor = GET_ALL_MQTT_DEVICES("sensor")
    
    error_message_device_checks = CHECK_DASHBOARD_CHECK_SETTINGS(GET_ALL_MQTT_DEVICES("device"))

    program_running         = GET_PROGRAM_RUNNING()   
    dropdown_list_programs  = GET_ALL_PROGRAMS() 
    
    if GET_REPEAT_PROGRAM() == True:
        checkbox_repeat_program = "checked"
               
    if GET_LOGFILE_SYSTEM(10) is not None:
        data_log_system = GET_LOGFILE_SYSTEM(10)
    else:
        data_log_system = ""
        error_message_log = "Keine Einträge gefunden"

    version = GET_CONFIG_VERSION()       

    # get sensor list
    try:
        mqtt_device_1_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(1).inputs
        mqtt_device_1_inputs = mqtt_device_1_inputs.replace(" ", "")
    except:
        mqtt_device_1_inputs = ""
    try:
        mqtt_device_2_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(2).inputs
        mqtt_device_2_inputs = mqtt_device_2_inputs.replace(" ", "")
    except:
        mqtt_device_2_inputs = ""
    try:        
        mqtt_device_3_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(3).inputs
        mqtt_device_3_inputs = mqtt_device_3_inputs.replace(" ", "")
    except:
        mqtt_device_3_inputs = ""
    try:        
        mqtt_device_4_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(4).inputs
        mqtt_device_4_inputs = mqtt_device_4_inputs.replace(" ", "")
    except:
        mqtt_device_4_inputs = ""
    try:        
        mqtt_device_5_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(5).inputs
        mqtt_device_5_inputs = mqtt_device_5_inputs.replace(" ", "")
    except:
        mqtt_device_5_inputs = ""
    try:        
        mqtt_device_6_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(6).inputs
        mqtt_device_6_inputs = mqtt_device_6_inputs.replace(" ", "")
    except:
        mqtt_device_6_inputs = ""
    try:        
        mqtt_device_7_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(7).inputs
        mqtt_device_7_inputs = mqtt_device_7_inputs.replace(" ", "")
    except:
        mqtt_device_7_inputs = ""
    try:        
        mqtt_device_8_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(8).inputs
        mqtt_device_8_inputs = mqtt_device_8_inputs.replace(" ", "")
    except:
        mqtt_device_8_inputs = ""
    try:        
        mqtt_device_9_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(9).inputs
        mqtt_device_9_inputs = mqtt_device_9_inputs.replace(" ", "")
    except:
        mqtt_device_9_inputs = ""
    try:        
        mqtt_device_10_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(10).inputs
        mqtt_device_10_inputs = mqtt_device_10_inputs.replace(" ", "")
    except:
        mqtt_device_10_inputs = ""
    try:        
        mqtt_device_11_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(11).inputs
        mqtt_device_11_inputs = mqtt_device_11_inputs.replace(" ", "")
    except:
        mqtt_device_11_inputs = ""
    try:        
        mqtt_device_12_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(12).inputs
        mqtt_device_12_inputs = mqtt_device_12_inputs.replace(" ", "")
    except:
        mqtt_device_12_inputs = ""
    try:        
        mqtt_device_13_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(13).inputs
        mqtt_device_13_inputs = mqtt_device_13_inputs.replace(" ", "")
    except:
        mqtt_device_13_inputs = ""
    try:        
        mqtt_device_14_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(14).inputs
        mqtt_device_14_inputs = mqtt_device_14_inputs.replace(" ", "")
    except:
        mqtt_device_14_inputs = ""
    try:        
        mqtt_device_15_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(15).inputs
        mqtt_device_15_inputs = mqtt_device_15_inputs.replace(" ", "")
    except:
        mqtt_device_15_inputs = ""    
    try:        
        mqtt_device_16_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(16).inputs
        mqtt_device_16_inputs = mqtt_device_16_inputs.replace(" ", "")
    except:
        mqtt_device_16_inputs = ""
    try:        
        mqtt_device_17_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(17).inputs
        mqtt_device_17_inputs = mqtt_device_17_inputs.replace(" ", "")
    except:
        mqtt_device_17_inputs = ""
    try:        
        mqtt_device_18_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(18).inputs
        mqtt_device_18_inputs = mqtt_device_18_inputs.replace(" ", "")
    except:
        mqtt_device_18_inputs = ""
    try:        
        mqtt_device_19_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(19).inputs
        mqtt_device_19_inputs = mqtt_device_19_inputs.replace(" ", "")
    except:
        mqtt_device_19_inputs = ""
    try:        
        mqtt_device_20_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(20).inputs
        mqtt_device_20_inputs = mqtt_device_20_inputs.replace(" ", "")
    except:
        mqtt_device_20_inputs = ""   
    try:        
        mqtt_device_21_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(21).inputs
        mqtt_device_21_inputs = mqtt_device_21_inputs.replace(" ", "")
    except:
        mqtt_device_21_inputs = ""   
    try:        
        mqtt_device_22_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(22).inputs
        mqtt_device_22_inputs = mqtt_device_22_inputs.replace(" ", "")
    except:
        mqtt_device_22_inputs = ""   
    try:        
        mqtt_device_23_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(23).inputs
        mqtt_device_23_inputs = mqtt_device_23_inputs.replace(" ", "")
    except:
        mqtt_device_23_inputs = ""   
    try:        
        mqtt_device_24_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(24).inputs
        mqtt_device_24_inputs = mqtt_device_24_inputs.replace(" ", "")
    except:
        mqtt_device_24_inputs = ""   
    try:        
        mqtt_device_25_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(25).inputs
        mqtt_device_25_inputs = mqtt_device_25_inputs.replace(" ", "")
    except:
        mqtt_device_25_inputs = ""           


    return render_template('dashboard.html',
                            data_led=data_led,
                            dropdown_list_led_scenes=dropdown_list_led_scenes,
                            dropdown_list_check_options=dropdown_list_check_options,
                            dropdown_list_operators=dropdown_list_operators,
                            list_mqtt_devices=list_mqtt_devices,
                            data_device=data_device,
                            checkbox=checkbox,
                            data_log_system=data_log_system, 
                            data_sensor=data_sensor,
                            program_running=program_running,      
                            dropdown_list_programs=dropdown_list_programs,
                            checkbox_repeat_program=checkbox_repeat_program,
                            version=version,  
                            error_message_led=error_message_led,
                            error_message_log=error_message_log,  
                            error_message_device=error_message_device,   
                            error_message_device_checks=error_message_device_checks,
                            error_message_start_program=error_message_start_program,
                            mqtt_device_1_inputs=mqtt_device_1_inputs,
                            mqtt_device_2_inputs=mqtt_device_2_inputs,
                            mqtt_device_3_inputs=mqtt_device_3_inputs,
                            mqtt_device_4_inputs=mqtt_device_4_inputs,
                            mqtt_device_5_inputs=mqtt_device_5_inputs,
                            mqtt_device_6_inputs=mqtt_device_6_inputs,
                            mqtt_device_7_inputs=mqtt_device_7_inputs,
                            mqtt_device_8_inputs=mqtt_device_8_inputs,
                            mqtt_device_9_inputs=mqtt_device_9_inputs,
                            mqtt_device_10_inputs=mqtt_device_10_inputs,
                            mqtt_device_11_inputs=mqtt_device_11_inputs,
                            mqtt_device_12_inputs=mqtt_device_12_inputs,
                            mqtt_device_13_inputs=mqtt_device_13_inputs,
                            mqtt_device_14_inputs=mqtt_device_14_inputs,
                            mqtt_device_15_inputs=mqtt_device_15_inputs,
                            mqtt_device_16_inputs=mqtt_device_16_inputs,
                            mqtt_device_17_inputs=mqtt_device_17_inputs,
                            mqtt_device_18_inputs=mqtt_device_18_inputs,
                            mqtt_device_19_inputs=mqtt_device_19_inputs,
                            mqtt_device_20_inputs=mqtt_device_20_inputs,  
                            mqtt_device_21_inputs=mqtt_device_21_inputs,
                            mqtt_device_22_inputs=mqtt_device_22_inputs,  
                            mqtt_device_23_inputs=mqtt_device_23_inputs,
                            mqtt_device_24_inputs=mqtt_device_24_inputs,
                            mqtt_device_25_inputs=mqtt_device_25_inputs,
                            tupel_current_playback=tupel_current_playback,
                            spotify_user=spotify_user,                               
                            role=current_user.role,
                            )
