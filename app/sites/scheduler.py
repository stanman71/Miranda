from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps
import datetime

from app import app
from app.database.database import *
from app.components.checks import *
from app.components.file_management import GET_ALL_LOCATIONS, GET_LOCATION_COORDINATES
from app.components.control_scheduler import GET_SUNRISE_TIME, GET_SUNSET_TIME


# access rights
def user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "user" or current_user.role == "superuser":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


""" ######### """
""" scheduler """
""" ######### """

@app.route('/dashboard/scheduler', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_scheduler():
    error_message_add_reduced_scheduler_task = ""
    error_message_reduced_change_settings    = ""
    error_message_reduced_time_settings      = ""
    error_message_reduced_scheduler_tasks    = ""

    error_message_add_scheduler_task         = ""    
    error_change_settings                    = ""
    error_message_general_settings           = ""    
    error_message_time_settings              = ""
    error_message_sun_settings               = ""
    error_message_sensor_settings            = ""
    error_message_position_settings          = ""
    error_message_scheduler_tasks            = ""
    error_message_locations_import           = ""

    UPDATE_MQTT_DEVICE_NAMES()

    for i in range (1,26):
        try:
            RESET_SCHEDULER_TASK_ERRORS(i)
        except:
            pass

    if request.method == "POST": 

        # add reduced scheduler task
        if request.form.get("add_reduced_scheduler_task") is not None:
            scheduler_task_name = request.form.get("set_reduced_scheduler_task_name")

            if scheduler_task_name == "":               
                error_message_add_reduced_scheduler_task = "Keinen Namen angegeben"
            else:         
                error_message_add_reduced_scheduler_task = ADD_SCHEDULER_TASK(scheduler_task_name, "reduced", "checked")          


        # ################
        # ################
        #   reduced task
        # ################
        # ################


        # change reduced settings
        if request.form.get("change_reduced_settings") != None: 
            for i in range (1,26):

                if request.form.get("set_name_reduced_" + str(i)) != None:
             
                    # ############
                    # name setting
                    # ############

                    scheduler_data = GET_SCHEDULER_TASK_BY_ID(i)
                    new_name       = request.form.get("set_name_reduced_" + str(i))                    

                    # add new name
                    if ((new_name != "") and (GET_SCHEDULER_TASK_BY_NAME(new_name) == None)):
                        name = request.form.get("set_name_reduced_" + str(i)) 
                      
                    # nothing changed 
                    elif new_name == scheduler_data.name:
                        name = scheduler_data.name                        
                        
                    # name already exist
                    elif ((GET_SCHEDULER_TASK_BY_NAME(new_name) != None) and (scheduler_data.name != new_name)):
                        name = scheduler_data.name 
                        error_message_reduced_change_settings = error_message_reduced_change_settings + (new_name + " >>> Name schon vergeben,")

                    # no input commited
                    else:                          
                        name = GET_SCHEDULER_TASK_BY_ID(i).name 
                        error_message_reduced_change_settings = error_message_reduced_change_settings + (name + " >>> Keinen Namen angegeben,")


                    # ############
                    # task setting
                    # ############

                    ### set task
                    if request.form.get("set_task_reduced_" + str(i)) != "":
                        task = request.form.get("set_task_reduced_" + str(i))
                    else:
                        task = GET_SCHEDULER_TASK_BY_ID(i).task


                    # #############
                    # time settings
                    # #############

                    ### set day
                    if request.form.get("set_day_reduced_" + str(i)) != "":
                        day = request.form.get("set_day_reduced_" + str(i))
                    else:
                        day = GET_SCHEDULER_TASK_BY_ID(i).day

                    ### set hour
                    if request.form.get("set_hour_reduced_" + str(i)) != "":
                        hour = request.form.get("set_hour_reduced_" + str(i))
                    else:
                        hour = GET_SCHEDULER_TASK_BY_ID(i).hour

                    ### set minute
                    if request.form.get("set_minute_reduced_" + str(i)) != "":
                        minute = request.form.get("set_minute_reduced_" + str(i))
                    else:
                        minute = GET_SCHEDULER_TASK_BY_ID(i).minute 


                    # #################
                    # checkbox settings
                    # #################

                    ### set checkbox repeat
                    if request.form.get("checkbox_option_repeat_reduced_" + str(i)):
                        option_repeat = "checked"
                    else:
                        option_repeat = "None"  

                    option_time             = "checked"
                    option_sun              = "None"
                    option_sensors          = "None"
                    option_position         = "None"
                    option_sunrise          = "None"
                    option_sunset           = "None" 
                    location                = "None" 
                    mqtt_device_ieeeAddr_1  = "None"
                    mqtt_device_name_1      = "None"
                    mqtt_device_inputs_1    = "None"
                    sensor_key_1            = "None"
                    operator_1              = "None"
                    value_1                 = "None"
                    operator_main_1         = "None"
                    mqtt_device_ieeeAddr_2  = "None"
                    mqtt_device_name_2      = "None"
                    mqtt_device_inputs_2    = "None"
                    sensor_key_2            = "None"
                    operator_2              = "None"
                    value_2                 = "None"
                    operator_main_2         = "None"
                    mqtt_device_ieeeAddr_3  = "None"
                    mqtt_device_name_3      = "None"
                    mqtt_device_inputs_3    = "None"
                    sensor_key_3            = "None"
                    operator_3              = "None"
                    value_3                 = "None"
                    option_home             = "None"
                    option_away             = "None"
                    ip_addresses             = "None"   

                    if error_message_reduced_change_settings != "":
                        error_message_reduced_change_settings = error_message_reduced_change_settings[:-1]

                    SET_SCHEDULER_TASK(i, name, task, 
                                          option_time, option_sun, option_sensors, option_position, option_repeat, 
                                          day, hour, minute,
                                          option_sunrise, option_sunset, location,
                                          mqtt_device_ieeeAddr_1, mqtt_device_name_1, mqtt_device_inputs_1, 
                                          sensor_key_1, operator_1, value_1, operator_main_1,
                                          mqtt_device_ieeeAddr_2, mqtt_device_name_2, mqtt_device_inputs_2, 
                                          sensor_key_2, operator_2, value_2, operator_main_2,
                                          mqtt_device_ieeeAddr_3, mqtt_device_name_3, mqtt_device_inputs_3, 
                                          sensor_key_3, operator_3, value_3,
                                          option_home, option_away, ip_addresses)


        # #################
        # #################
        #   complete task
        # #################
        # #################

        # add scheduler task
        if request.form.get("add_scheduler_task") is not None:
            scheduler_task_name = request.form.get("set_scheduler_task_name")

            if scheduler_task_name == "":               
                error_message_add_scheduler_task = "Keinen Namen angegeben"
            else:         
                error_message_add_scheduler_task = ADD_SCHEDULER_TASK(scheduler_task_name, "complete")          

        # change settings
        if request.form.get("change_settings") != None: 
            for i in range (1,26):

                if request.form.get("set_name_" + str(i)) != None:


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
                        mqtt_device_name_1   = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_1).name
                        mqtt_device_inputs_1 = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_1).inputs

                        # get sensorkey value
                        sensor_key_1 = request.form.get("set_sensor_1_" + str(i))
                        sensor_key_1 = sensor_key_1.replace(" ", "") 
                        if sensor_key_1.isdigit():
                            if sensor_key_1 == "0" or sensor_key_1 == "1":
                                sensor_key_1 = "None"
                            else:                                
                                sensor_list  = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_1).inputs
                                sensor_list  = sensor_list.split(",")
                                sensor_key_1 = sensor_list[int(sensor_key_1)-2]
                            
                    except:
                        sensor_key_1           = "None"
                        mqtt_device_ieeeAddr_1 = "None"
                        mqtt_device_name_1     = "None"
                        mqtt_device_inputs_1   = "None"  


                    # get mqtt device 2
                    try:
                        mqtt_device_name_2   = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_2).name
                        mqtt_device_inputs_2 = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_2).inputs

                        # get sensorkey value
                        sensor_key_2 = request.form.get("set_sensor_2_" + str(i))
                        sensor_key_2 = sensor_key_2.replace(" ", "") 
                        if sensor_key_2.isdigit():
                            if sensor_key_2 == "0" or sensor_key_2 == "2":
                                sensor_key_2 = "None"
                            else:                                
                                sensor_list  = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_2).inputs
                                sensor_list  = sensor_list.split(",")
                                sensor_key_2 = sensor_list[int(sensor_key_2)-2]
                            
                    except:
                        sensor_key_2           = "None"
                        mqtt_device_ieeeAddr_2 = "None"
                        mqtt_device_name_2     = "None"
                        mqtt_device_inputs_2   = "None"   


                    # get mqtt device 3
                    try:
                        mqtt_device_name_3   = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_3).name
                        mqtt_device_inputs_3 = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_3).inputs

                        # get sensorkey value
                        sensor_key_3 = request.form.get("set_sensor_3_" + str(i))
                        sensor_key_3 = sensor_key_3.replace(" ", "") 
                        if sensor_key_3.isdigit():
                            if sensor_key_3 == "0" or sensor_key_3 == "3":
                                sensor_key_3 = "None"
                            else:                                
                                sensor_list  = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr_3).inputs
                                sensor_list  = sensor_list.split(",")
                                sensor_key_3 = sensor_list[int(sensor_key_3)-2]
                            
                    except:
                        sensor_key_3           = "None"
                        mqtt_device_ieeeAddr_3 = "None"
                        mqtt_device_name_3     = "None"
                        mqtt_device_inputs_3   = "None"   


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
                                          mqtt_device_ieeeAddr_1, mqtt_device_name_1, mqtt_device_inputs_1, 
                                          sensor_key_1, operator_1, value_1, operator_main_1,
                                          mqtt_device_ieeeAddr_2, mqtt_device_name_2, mqtt_device_inputs_2, 
                                          sensor_key_2, operator_2, value_2, operator_main_2,
                                          mqtt_device_ieeeAddr_3, mqtt_device_name_3, mqtt_device_inputs_3, 
                                          sensor_key_3, operator_3, value_3,
                                          option_home, option_away, ip_addresses)


    error_message_reduced_scheduler_tasks = CHECK_TASKS(GET_ALL_SCHEDULER_TASKS_BY_TYPE("reduced"), "scheduler")
    error_message_reduced_time_settings   = CHECK_SCHEDULER_TIME_SETTINGS(GET_ALL_SCHEDULER_TASKS_BY_TYPE("reduced"))

    error_message_scheduler_tasks   = CHECK_TASKS(GET_ALL_SCHEDULER_TASKS_BY_TYPE("complete"), "scheduler")
    error_message_general_settings  = CHECK_SCHEDULER_GENERAL_SETTINGS(GET_ALL_SCHEDULER_TASKS_BY_TYPE("complete"))
    error_message_time_settings     = CHECK_SCHEDULER_TIME_SETTINGS(GET_ALL_SCHEDULER_TASKS_BY_TYPE("complete"))
    error_message_sun_settings      = CHECK_SCHEDULER_SUN_SETTINGS(GET_ALL_SCHEDULER_TASKS_BY_TYPE("complete"))
    error_message_sensor_settings   = CHECK_SCHEDULER_SENSOR_SETTINGS(GET_ALL_SCHEDULER_TASKS_BY_TYPE("complete"))
    error_message_position_settings = CHECK_SCHEDULER_POSITION_SETTINGS(GET_ALL_SCHEDULER_TASKS_BY_TYPE("complete"))

    scheduler_task_list = GET_ALL_SCHEDULER_TASKS()

    dropdown_list_mqtt_devices  = GET_ALL_MQTT_DEVICES("sensor")
    dropdown_list_operators     = ["=", ">", "<"]
    dropdown_list_operator_main = ["and", "or", "=", ">", "<"]

    dropdown_list_locations = GET_ALL_LOCATIONS()
    
    if "ERROR" in dropdown_list_locations:
        error_message_locations_import = dropdown_list_locations
        dropdown_list_locations = ""

    # get sensor list
    try:
        mqtt_device_1_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(1).inputs
        mqtt_device_1_inputs = mqtt_device_1_inputs.replace(" ", "")
    except:
        mqtt_device_1_inputs = ""
    try:
        mqtt_device_2_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(2).inputs
        mqtt_device_2_inputs = mqtt_device_2_inputs.replace(" ", "")
    except:
        mqtt_device_2_inputs = ""
    try:        
        mqtt_device_3_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(3).inputs
        mqtt_device_3_inputs = mqtt_device_3_inputs.replace(" ", "")
    except:
        mqtt_device_3_inputs = ""
    try:        
        mqtt_device_4_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(4).inputs
        mqtt_device_4_inputs = mqtt_device_4_inputs.replace(" ", "")
    except:
        mqtt_device_4_inputs = ""
    try:        
        mqtt_device_5_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(5).inputs
        mqtt_device_5_inputs = mqtt_device_5_inputs.replace(" ", "")
    except:
        mqtt_device_5_inputs = ""
    try:        
        mqtt_device_6_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(6).inputs
        mqtt_device_6_inputs = mqtt_device_6_inputs.replace(" ", "")
    except:
        mqtt_device_6_inputs = ""
    try:        
        mqtt_device_7_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(7).inputs
        mqtt_device_7_inputs = mqtt_device_7_inputs.replace(" ", "")
    except:
        mqtt_device_7_inputs = ""
    try:        
        mqtt_device_8_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(8).inputs
        mqtt_device_8_inputs = mqtt_device_8_inputs.replace(" ", "")
    except:
        mqtt_device_8_inputs = ""
    try:        
        mqtt_device_9_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(9).inputs
        mqtt_device_9_inputs = mqtt_device_9_inputs.replace(" ", "")
    except:
        mqtt_device_9_inputs = ""
    try:        
        mqtt_device_10_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(10).inputs
        mqtt_device_10_inputs = mqtt_device_10_inputs.replace(" ", "")
    except:
        mqtt_device_10_inputs = ""
    try:        
        mqtt_device_11_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(11).inputs
        mqtt_device_11_inputs = mqtt_device_11_inputs.replace(" ", "")
    except:
        mqtt_device_11_inputs = ""
    try:        
        mqtt_device_12_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(12).inputs
        mqtt_device_12_inputs = mqtt_device_12_inputs.replace(" ", "")
    except:
        mqtt_device_12_inputs = ""
    try:        
        mqtt_device_13_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(13).inputs
        mqtt_device_13_inputs = mqtt_device_13_inputs.replace(" ", "")
    except:
        mqtt_device_13_inputs = ""
    try:        
        mqtt_device_14_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(14).inputs
        mqtt_device_14_inputs = mqtt_device_14_inputs.replace(" ", "")
    except:
        mqtt_device_14_inputs = ""
    try:        
        mqtt_device_15_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(15).inputs
        mqtt_device_15_inputs = mqtt_device_15_inputs.replace(" ", "")
    except:
        mqtt_device_15_inputs = ""    
    try:        
        mqtt_device_16_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(16).inputs
        mqtt_device_16_inputs = mqtt_device_16_inputs.replace(" ", "")
    except:
        mqtt_device_16_inputs = ""
    try:        
        mqtt_device_17_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(17).inputs
        mqtt_device_17_inputs = mqtt_device_17_inputs.replace(" ", "")
    except:
        mqtt_device_17_inputs = ""
    try:        
        mqtt_device_18_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(18).inputs
        mqtt_device_18_inputs = mqtt_device_18_inputs.replace(" ", "")
    except:
        mqtt_device_18_inputs = ""
    try:        
        mqtt_device_19_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(19).inputs
        mqtt_device_19_inputs = mqtt_device_19_inputs.replace(" ", "")
    except:
        mqtt_device_19_inputs = ""
    try:        
        mqtt_device_20_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(20).inputs
        mqtt_device_20_inputs = mqtt_device_20_inputs.replace(" ", "")
    except:
        mqtt_device_20_inputs = ""   
    try:        
        mqtt_device_21_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(21).inputs
        mqtt_device_21_inputs = mqtt_device_21_inputs.replace(" ", "")
    except:
        mqtt_device_21_inputs = ""   
    try:        
        mqtt_device_22_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(22).inputs
        mqtt_device_22_inputs = mqtt_device_22_inputs.replace(" ", "")
    except:
        mqtt_device_22_inputs = ""   
    try:        
        mqtt_device_23_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(23).inputs
        mqtt_device_23_inputs = mqtt_device_23_inputs.replace(" ", "")
    except:
        mqtt_device_23_inputs = ""   
    try:        
        mqtt_device_24_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(24).inputs
        mqtt_device_24_inputs = mqtt_device_24_inputs.replace(" ", "")
    except:
        mqtt_device_24_inputs = ""   
    try:        
        mqtt_device_25_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(25).inputs
        mqtt_device_25_inputs = mqtt_device_25_inputs.replace(" ", "")
    except:
        mqtt_device_25_inputs = ""           


    return render_template('dashboard_scheduler.html',
                            scheduler_task_list=scheduler_task_list,
                            error_message_add_reduced_scheduler_task=error_message_add_reduced_scheduler_task,
                            error_message_reduced_change_settings=error_message_reduced_change_settings,
                            error_message_reduced_time_settings=error_message_reduced_time_settings,
                            error_message_reduced_scheduler_tasks=error_message_reduced_scheduler_tasks,
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
                            role=current_user.role,                                 
                            )


# change scheduler task position 
@app.route('/dashboard/scheduler/position/<string:direction>/<string:task_type>/<int:id>')
@login_required
@user_required
def change_scheduler_task_position(id, task_type, direction):
    CHANGE_SCHEDULER_TASK_POSITION(id, task_type, direction)
    return redirect(url_for('dashboard_scheduler'))


# add scheduler sensor row
@app.route('/dashboard/scheduler/sensor_row/add/<int:id>')
@login_required
@user_required
def add_scheduler_sensor_row(id):
    ADD_SCHEDULER_TASK_SENSOR_ROW(id)
    return redirect(url_for('dashboard_scheduler'))


# remove scheduler sensor row
@app.route('/dashboard/scheduler/sensor_row/remove/<int:id>')
@login_required
@user_required
def remove_scheduler_sensor_row(id):
    REMOVE_SCHEDULER_TASK_SENSOR_ROW(id)
    return redirect(url_for('dashboard_scheduler'))


# delete scheduler task
@app.route('/dashboard/scheduler/delete/<int:id>')
@login_required
@user_required
def delete_scheduler_task(id):
    DELETE_SCHEDULER_TASK(id)
    return redirect(url_for('dashboard_scheduler'))
