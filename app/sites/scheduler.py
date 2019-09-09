from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps

from app import app
from app.database.database import *
from app.components.checks import *
from app.components.file_management import GET_ALL_LOCATIONS, GET_LOCATION_COORDINATES
from app.components.process_scheduler import GET_SUNRISE_TIME, GET_SUNSET_TIME
from app.components.backend_spotify import GET_SPOTIFY_TOKEN

import datetime
import spotipy


# access rights
def permission_required(f):
    @wraps(f)
    def wrap(*args, **kwargs): 
        try:
            if current_user.permission_dashboard == "checked":
                return f(*args, **kwargs)
            else:
                return redirect(url_for('logout'))
        except:
            return redirect(url_for('logout'))
        
    return wrap


""" ######### """
""" scheduler """
""" ######### """

@app.route('/scheduler', methods=['GET', 'POST'])
@login_required
@permission_required
def scheduler():
    error_message_add_scheduler_task         = ""    
    error_change_settings                    = ""
    error_message_general_settings           = ""    
    error_message_time_settings              = ""
    error_message_sun_settings               = ""
    error_message_sensor_settings            = ""
    error_message_position_settings          = ""
    error_message_scheduler_tasks            = ""
    error_message_locations_import           = ""

    RESET_SCHEDULER_TASK_ERRORS()
    RESET_SCHEDULER_TASK_COLLAPSE()
    UPDATE_MQTT_DEVICE_NAMES()
        

    if request.method == "POST": 


        # add scheduler task
        if request.form.get("add_scheduler_task") is not None:
            scheduler_task_name = request.form.get("set_scheduler_task_name")

            if scheduler_task_name == "":               
                error_message_add_scheduler_task = "Keinen Namen angegeben"
            else:         
                error_message_add_scheduler_task = ADD_SCHEDULER_TASK(scheduler_task_name, "")          

        # change settings
        for i in range (1,26):
            
            if request.form.get("set_name_" + str(i)) != None:
                
                SET_SCHEDULER_TASK_COLLAPSE(i)    

                # ############
                # name setting
                # ############

                scheduler_data = GET_SCHEDULER_TASK_BY_ID(i)
                new_name       = request.form.get("set_name_" + str(i))                    

                # add new name
                if ((new_name != "") and (GET_SCHEDULER_TASK_BY_NAME(new_name) == None)):
                    name = request.form.get("set_name_" + str(i)) 
                  
                # nothing changed 
                elif new_name == scheduler_data.name:
                    name = scheduler_data.name                        
                    
                # name already exist
                elif ((GET_SCHEDULER_TASK_BY_NAME(new_name) != None) and (scheduler_data.name != new_name)):
                    name = scheduler_data.name 
                    error_change_settings = "Name schon vergeben"

                # no input commited
                else:                          
                    name = GET_SCHEDULER_TASK_BY_ID(i).name 
                    error_change_settings = "Keinen Namen angegeben"


                # ############
                # task setting
                # ############


                # set task
                if request.form.get("set_task_" + str(i)) != "":
                    task = request.form.get("set_task_" + str(i))
                else:
                    task = GET_SCHEDULER_TASK_BY_ID(i).task
                    error_change_settings = "Keine Aufgabe angegeben"


                # #################
                # checkbox settings
                # #################


                # set checkbox time
                if request.form.get("checkbox_option_time_" + str(i)):
                    option_time = "checked"
                else:
                    option_time = "None"  


                # set checkbox sun
                if request.form.get("checkbox_option_sun_" + str(i)):
                    option_sun = "checked"
                else:
                    option_sun = "None" 


                # set checkbox sensors
                if request.form.get("checkbox_option_sensors_" + str(i)):
                    option_sensors = "checked"
                else:
                    option_sensors = "None"  


                # set checkbox position
                if request.form.get("checkbox_option_position_" + str(i)):
                    option_position = "checked"
                else:
                    option_position = "None"  
                    
                    
                # set checkbox repeat
                if request.form.get("checkbox_option_repeat_" + str(i)):
                    option_repeat = "checked"
                else:
                    option_repeat = "None"  


                # #############
                # time settings
                # #############


                # set day
                if request.form.get("set_day_" + str(i)) != "":
                    day = request.form.get("set_day_" + str(i))
                else:
                    day = GET_SCHEDULER_TASK_BY_ID(i).day


                # set hour
                if request.form.get("set_hour_" + str(i)) != "":
                    hour = request.form.get("set_hour_" + str(i))
                else:
                    hour = GET_SCHEDULER_TASK_BY_ID(i).hour


                # set minute
                if request.form.get("set_minute_" + str(i)) != "":
                    minute = request.form.get("set_minute_" + str(i))
                else:
                    minute = GET_SCHEDULER_TASK_BY_ID(i).minute 


                # ############
                # sun settings
                # ############


                # set option sunrise
                if request.form.get("checkbox_option_sunrise_" + str(i)):
                    option_sunrise = "checked"
                else:
                    option_sunrise = "None"  


                # set option sunset
                if request.form.get("checkbox_option_sunset_" + str(i)):
                    option_sunset = "checked"
                else:              
                    option_sunset = "None"  


                # set location
                location = request.form.get("set_location_" + str(i))
                
                if location == "" or location == None:           
                    location = "None"  
                    
                               
                # update sunrise / sunset  
                if location != "None":
                    
                    # get coordinates
                    coordinates = GET_LOCATION_COORDINATES(location)
                     
                    SET_SCHEDULER_TASK_SUNRISE(i, GET_SUNRISE_TIME(float(coordinates[0]), float(coordinates[1])))
                    SET_SCHEDULER_TASK_SUNSET(i, GET_SUNSET_TIME(float(coordinates[0]), float(coordinates[1])))
                            
                else:
                    SET_SCHEDULER_TASK_SUNRISE(i, "None")
                    SET_SCHEDULER_TASK_SUNSET(i, "None")                        


                # ###############
                # sensor settings
                # ###############              

                # set mqtt_device 1
                mqtt_device_1 = request.form.get("set_mqtt_device_1_" + str(i))

                if GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_1):
                    mqtt_device_ieeeAddr_1 = mqtt_device_1
                elif GET_MQTT_DEVICE_BY_ID(mqtt_device_1):
                    mqtt_device_ieeeAddr_1 = GET_MQTT_DEVICE_BY_ID(mqtt_device_1).ieeeAddr
                else:
                    mqtt_device_ieeeAddr_1 = "None"
                     
                     
                # set mqtt_device 2
                mqtt_device_2 = request.form.get("set_mqtt_device_2_" + str(i))

                if GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_2):
                    mqtt_device_ieeeAddr_2 = mqtt_device_2
                elif GET_MQTT_DEVICE_BY_ID(mqtt_device_2):
                    mqtt_device_ieeeAddr_2 = GET_MQTT_DEVICE_BY_ID(mqtt_device_2).ieeeAddr
                else:
                    mqtt_device_ieeeAddr_2 = "None"
                    
                    
                # set mqtt_device 3
                mqtt_device_3 = request.form.get("set_mqtt_device_3_" + str(i)) 

                if GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_3):
                    mqtt_device_ieeeAddr_3 = mqtt_device_3
                elif GET_MQTT_DEVICE_BY_ID(mqtt_device_3):
                    mqtt_device_ieeeAddr_3 = GET_MQTT_DEVICE_BY_ID(mqtt_device_3).ieeeAddr
                else:
                    mqtt_device_ieeeAddr_3 = "None"
                    
                    
                operator_1       = request.form.get("set_operator_1_" + str(i))
                operator_2       = request.form.get("set_operator_2_" + str(i))
                operator_3       = request.form.get("set_operator_3_" + str(i))     
                value_1          = request.form.get("set_value_1_" + str(i))
                value_2          = request.form.get("set_value_2_" + str(i))
                value_3          = request.form.get("set_value_3_" + str(i))                                    
                operator_main_1  = request.form.get("set_operator_main_1_" + str(i))
                operator_main_2  = request.form.get("set_operator_main_2_" + str(i))


                if operator_1 == None:
                    operator_1 = "None"
                if operator_2 == None:
                    operator_2 = "None"    
                if operator_3 == None:
                    operator_3 = "None"  
                if value_1 == None or value_1 == "":
                    value_1 = "None"
                if value_2 == None or value_2 == "":
                    value_2 = "None"
                if value_3 == None or value_3 == "":
                    value_3 = "None"                       
                if operator_main_1 == None:
                    operator_main_1 = "None"
                if operator_main_2 == None:
                    operator_main_2 = "None"                   


                # get mqtt device 1
                try:
                    mqtt_device_name_1         = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_1).name
                    mqtt_device_input_values_1 = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_1).input_values

                    # get sensorkey value
                    sensor_key_1 = request.form.get("set_sensor_1_" + str(i))
                    sensor_key_1 = sensor_key_1.replace(" ", "") 
                    if sensor_key_1.isdigit():
                        if sensor_key_1 == "0" or sensor_key_1 == "1":
                            sensor_key_1 = "None"
                        else:                                
                            sensor_list  = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_1).input_values
                            sensor_list  = sensor_list.split(",")
                            sensor_key_1 = sensor_list[int(sensor_key_1)-2]
                        
                except:  
                    sensor_key_1               = "None"
                    mqtt_device_ieeeAddr_1     = "None"
                    mqtt_device_name_1         = "None"
                    mqtt_device_input_values_1 = "None"  


                # get mqtt device 2
                try:
                    mqtt_device_name_2         = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_2).name
                    mqtt_device_input_values_2 = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_2).input_values

                    # get sensorkey value
                    sensor_key_2 = request.form.get("set_sensor_2_" + str(i))
                    sensor_key_2 = sensor_key_2.replace(" ", "") 
                    if sensor_key_2.isdigit():
                        if sensor_key_2 == "0" or sensor_key_2 == "1":
                            sensor_key_2 = "None"
                        else:                                
                            sensor_list  = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_2).input_values
                            sensor_list  = sensor_list.split(",")
                            sensor_key_2 = sensor_list[int(sensor_key_2)-2]
                        
                except:
                    sensor_key_2               = "None"
                    mqtt_device_ieeeAddr_2     = "None"
                    mqtt_device_name_2         = "None"
                    mqtt_device_input_values_2 = "None"   


                # get mqtt device 3
                try:
                    mqtt_device_name_3         = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_3).name
                    mqtt_device_input_values_3 = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_3).input_values



                    # get sensorkey value
                    sensor_key_3 = request.form.get("set_sensor_3_" + str(i))
                    sensor_key_3 = sensor_key_3.replace(" ", "") 
                    
                    if sensor_key_3.isdigit():
                        if sensor_key_3 == "0" or sensor_key_3 == "1":
                            sensor_key_3 = "None"
                        else:                                
                            sensor_list  = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_3).input_values
                            sensor_list  = sensor_list.split(",")
                            sensor_key_3 = sensor_list[int(sensor_key_3)-2]
                        
                except: 
                    sensor_key_3               = "None"
                    mqtt_device_ieeeAddr_3     = "None"
                    mqtt_device_name_3         = "None"
                    mqtt_device_input_values_3 = "None"   


                # #################
                # position settings
                # #################   


                # set option home
                if request.form.get("checkbox_option_home_" + str(i)):
                    option_home = "checked"
                else:
                    option_home = "None"  


                # set option away
                if request.form.get("checkbox_option_away_" + str(i)):
                    option_away = "checked"
                else:
                    option_away = "None"  

                # set ip_addresses
                if request.form.get("set_ip_addresses_" + str(i)) != "":
                    ip_addresses = request.form.get("set_ip_addresses_" + str(i))
                else:
                    ip_addresses = "None"
                    
                SET_SCHEDULER_TASK_CHANGE_ERRORS(i, error_change_settings)
                
                SET_SCHEDULER_TASK(i, name, task, 
                                      option_time, option_sun, option_sensors, option_position, option_repeat, 
                                      day, hour, minute,
                                      option_sunrise, option_sunset, location,
                                      mqtt_device_ieeeAddr_1, mqtt_device_name_1, mqtt_device_input_values_1, 
                                      sensor_key_1, operator_1, value_1, operator_main_1,
                                      mqtt_device_ieeeAddr_2, mqtt_device_name_2, mqtt_device_input_values_2, 
                                      sensor_key_2, operator_2, value_2, operator_main_2,
                                      mqtt_device_ieeeAddr_3, mqtt_device_name_3, mqtt_device_input_values_3, 
                                      sensor_key_3, operator_3, value_3,
                                      option_home, option_away, ip_addresses)


            # add sensor row
            if request.form.get("add_sensor_row_" + str(i)) != None:
                ADD_SCHEDULER_TASK_SENSOR_ROW(i)
                
            # remove sensor
            if request.form.get("remove_sensor_row_" + str(i)) != None:
                REMOVE_SCHEDULER_TASK_SENSOR_ROW(i)


    error_message_scheduler_tasks   = CHECK_TASKS(GET_ALL_SCHEDULER_TASKS(), "scheduler")
    error_message_general_settings  = CHECK_SCHEDULER_GENERAL_SETTINGS(GET_ALL_SCHEDULER_TASKS())
    error_message_time_settings     = CHECK_SCHEDULER_TIME_SETTINGS(GET_ALL_SCHEDULER_TASKS())
    error_message_sun_settings      = CHECK_SCHEDULER_SUN_SETTINGS(GET_ALL_SCHEDULER_TASKS())
    error_message_sensor_settings   = CHECK_SCHEDULER_SENSOR_SETTINGS(GET_ALL_SCHEDULER_TASKS())
    error_message_position_settings = CHECK_SCHEDULER_POSITION_SETTINGS(GET_ALL_SCHEDULER_TASKS())
    
    scheduler_task_list = GET_ALL_SCHEDULER_TASKS()

    dropdown_list_mqtt_devices  = GET_ALL_MQTT_DEVICES("sensor")
    dropdown_list_operators     = ["=", ">", "<"]
    dropdown_list_operator_main = ["and", "or", "=", ">", "<"]


    # list locations
    dropdown_list_locations = GET_ALL_LOCATIONS()

    if "ERROR" in dropdown_list_locations:
        error_message_locations_import = dropdown_list_locations
        dropdown_list_locations = ""


    # list device command option
    list_device_command_options = []
    
    for device in GET_ALL_MQTT_DEVICES("device"):
        list_device_command_options.append((device.name, device.commands))
        
    
    # list spotify devices / playlists
    spotify_token = GET_SPOTIFY_TOKEN()    
    
    try:
        sp       = spotipy.Spotify(auth=spotify_token)
        sp.trace = False
        
        spotify_devices   = sp.devices()["devices"]        
        spotify_playlists = sp.current_user_playlists(limit=20)["items"]   
        
    except:
        spotify_devices   = ""       
        spotify_playlists = ""   


    # get sensor list
    try:
        mqtt_device_1_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(1).input_values
        mqtt_device_1_input_values = mqtt_device_1_input_values.replace(" ", "")
    except:
        mqtt_device_1_input_values = ""
    try:
        mqtt_device_2_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(2).input_values
        mqtt_device_2_input_values = mqtt_device_2_input_values.replace(" ", "")
    except:
        mqtt_device_2_input_values = ""
    try:        
        mqtt_device_3_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(3).input_values
        mqtt_device_3_input_values = mqtt_device_3_input_values.replace(" ", "")
    except:
        mqtt_device_3_input_values = ""
    try:        
        mqtt_device_4_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(4).input_values
        mqtt_device_4_input_values = mqtt_device_4_input_values.replace(" ", "")
    except:
        mqtt_device_4_input_values = ""
    try:        
        mqtt_device_5_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(5).input_values
        mqtt_device_5_input_values = mqtt_device_5_input_values.replace(" ", "")
    except:
        mqtt_device_5_input_values = ""
    try:        
        mqtt_device_6_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(6).input_values
        mqtt_device_6_input_values = mqtt_device_6_input_values.replace(" ", "")
    except:
        mqtt_device_6_input_values = ""
    try:        
        mqtt_device_7_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(7).input_values
        mqtt_device_7_input_values = mqtt_device_7_input_values.replace(" ", "")
    except:
        mqtt_device_7_input_values = ""
    try:        
        mqtt_device_8_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(8).input_values
        mqtt_device_8_input_values = mqtt_device_8_input_values.replace(" ", "")
    except:
        mqtt_device_8_input_values = ""
    try:        
        mqtt_device_9_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(9).input_values
        mqtt_device_9_input_values = mqtt_device_9_input_values.replace(" ", "")
    except:
        mqtt_device_9_input_values = ""
    try:        
        mqtt_device_10_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(10).input_values
        mqtt_device_10_input_values = mqtt_device_10_input_values.replace(" ", "")
    except:
        mqtt_device_10_input_values = ""
    try:        
        mqtt_device_11_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(11).input_values
        mqtt_device_11_input_values = mqtt_device_11_input_values.replace(" ", "")
    except:
        mqtt_device_11_input_values = ""
    try:        
        mqtt_device_12_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(12).input_values
        mqtt_device_12_input_values = mqtt_device_12_input_values.replace(" ", "")
    except:
        mqtt_device_12_input_values = ""
    try:        
        mqtt_device_13_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(13).input_values
        mqtt_device_13_input_values = mqtt_device_13_input_values.replace(" ", "")
    except:
        mqtt_device_13_input_values = ""
    try:        
        mqtt_device_14_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(14).input_values
        mqtt_device_14_input_values = mqtt_device_14_input_values.replace(" ", "")
    except:
        mqtt_device_14_input_values = ""
    try:        
        mqtt_device_15_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(15).input_values
        mqtt_device_15_input_values = mqtt_device_15_input_values.replace(" ", "")
    except:
        mqtt_device_15_input_values = ""    
    try:        
        mqtt_device_16_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(16).input_values
        mqtt_device_16_input_values = mqtt_device_16_input_values.replace(" ", "")
    except:
        mqtt_device_16_input_values = ""
    try:        
        mqtt_device_17_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(17).input_values
        mqtt_device_17_input_values = mqtt_device_17_input_values.replace(" ", "")
    except:
        mqtt_device_17_input_values = ""
    try:        
        mqtt_device_18_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(18).input_values
        mqtt_device_18_input_values = mqtt_device_18_input_values.replace(" ", "")
    except:
        mqtt_device_18_input_values = ""
    try:        
        mqtt_device_19_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(19).input_values
        mqtt_device_19_input_values = mqtt_device_19_input_values.replace(" ", "")
    except:
        mqtt_device_19_input_values = ""
    try:        
        mqtt_device_20_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(20).input_values
        mqtt_device_20_input_values = mqtt_device_20_input_values.replace(" ", "")
    except:
        mqtt_device_20_input_values = ""   
    try:        
        mqtt_device_21_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(21).input_values
        mqtt_device_21_input_values = mqtt_device_21_input_values.replace(" ", "")
    except:
        mqtt_device_21_input_values = ""   
    try:        
        mqtt_device_22_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(22).input_values
        mqtt_device_22_input_values = mqtt_device_22_input_values.replace(" ", "")
    except:
        mqtt_device_22_input_values = ""   
    try:        
        mqtt_device_23_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(23).input_values
        mqtt_device_23_input_values = mqtt_device_23_input_values.replace(" ", "")
    except:
        mqtt_device_23_input_values = ""   
    try:        
        mqtt_device_24_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(24).input_values
        mqtt_device_24_input_values = mqtt_device_24_input_values.replace(" ", "")
    except:
        mqtt_device_24_input_values = ""   
    try:        
        mqtt_device_25_input_values = "Sensor,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(25).input_values
        mqtt_device_25_input_values = mqtt_device_25_input_values.replace(" ", "")
    except:
        mqtt_device_25_input_values = ""      
        

    return render_template('scheduler.html',
                            scheduler_task_list=scheduler_task_list,
                            error_message_add_scheduler_task=error_message_add_scheduler_task,
                            error_message_general_settings=error_message_general_settings,
                            error_message_time_settings=error_message_time_settings,
                            error_message_sun_settings=error_message_sun_settings,
                            error_message_sensor_settings=error_message_sensor_settings,
                            error_message_position_settings=error_message_position_settings,
                            error_message_scheduler_tasks=error_message_scheduler_tasks,   
                            error_message_locations_import=error_message_locations_import,                     
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            dropdown_list_operators=dropdown_list_operators,
                            dropdown_list_operator_main=dropdown_list_operator_main,
                            dropdown_list_locations=dropdown_list_locations,
                            spotify_devices=spotify_devices,
                            spotify_playlists=spotify_playlists,   
                            list_device_command_options=list_device_command_options,                            
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
                            permission_heating=current_user.permission_heating,                           
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system,                                 
                            )


# change scheduler task position 
@app.route('/scheduler/position/<string:direction>/<int:id>')
@login_required
@permission_required
def change_scheduler_task_position(id, direction):
    CHANGE_SCHEDULER_TASK_POSITION(id, direction)
    return redirect(url_for('scheduler'))


# delete scheduler task
@app.route('/scheduler/delete/<int:id>')
@login_required
@permission_required
def delete_scheduler_task(id):
    DELETE_SCHEDULER_TASK(id)
    return redirect(url_for('scheduler'))
