from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps
import datetime

from app import app
from app.database.database import *
from app.components.scheduler_tasks import *
from app.components.checks import *


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
    error_message_time_settings              = ""
    error_message_timer_settings             = ""
    error_message_sensor_settings            = ""
    error_message_expanded_settings          = ""
    error_message_scheduler_tasks            = ""


    for i in range (1,26):
        try:
            RESET_SCHEDULER_ERRORS(i)
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


                    option_time          = "checked"
                    option_timer         = "None"
                    option_sensors       = "None"
                    option_expanded      = "None"
                    timer_hour           = "None"
                    timer_minute         = "None"
                    timer_endtask        = "None"
                    mqtt_device_id_1     = "None"
                    mqtt_device_name_1   = "None"
                    mqtt_device_inputs_1 = "None"
                    sensor_key_1         = "None"
                    operator_1           = "None"
                    value_1              = "None"
                    operator_main_1      = "None"
                    mqtt_device_id_2     = "None"
                    mqtt_device_name_2   = "None"
                    mqtt_device_inputs_2 = "None"
                    sensor_key_2         = "None"
                    operator_2           = "None"
                    value_2              = "None"
                    operator_main_2      = "None"
                    mqtt_device_id_3     = "None"
                    mqtt_device_name_3   = "None"
                    mqtt_device_inputs_3 = "None"
                    sensor_key_3         = "None"
                    operator_3           = "None"
                    value_3              = "None"
                    expanded_home        = "None"
                    expanded_away        = "None"
                    expanded_ip_adresses = "None"
                    expanded_sunrise     = "None"
                    expanded_sunset      = "None"     

                    if error_message_reduced_change_settings != "":
                        error_message_reduced_change_settings = error_message_reduced_change_settings[:-1]

                    SET_SCHEDULER_TASK(i, name, task, 
                                          option_time, option_timer, option_sensors, option_expanded, option_repeat, 
                                          day, hour, minute,
                                          timer_hour, timer_minute, timer_endtask,
                                          mqtt_device_id_1, mqtt_device_name_1, mqtt_device_inputs_1, 
                                          sensor_key_1, operator_1, value_1, operator_main_1,
                                          mqtt_device_id_2, mqtt_device_name_2, mqtt_device_inputs_2, 
                                          sensor_key_2, operator_2, value_2, operator_main_2,
                                          mqtt_device_id_3, mqtt_device_name_3, mqtt_device_inputs_3, 
                                          sensor_key_3, operator_3, value_3,
                                          expanded_home, expanded_away, expanded_ip_adresses, expanded_sunrise, expanded_sunset)


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
                error_message_add_scheduler_task = ADD_SCHEDULER_TASK(scheduler_task_name, "")          

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

                    ### set task
                    if request.form.get("set_task_" + str(i)) != "":
                        task = request.form.get("set_task_" + str(i))
                    else:
                        task = GET_SCHEDULER_TASK_BY_ID(i).task


                    # #################
                    # checkbox settings
                    # #################

                    ### set checkbox time
                    if request.form.get("checkbox_option_time_" + str(i)):
                        option_time = "checked"
                    else:
                        option_time = "None"  

                    ### set checkbox timer
                    if request.form.get("checkbox_option_timer_" + str(i)):
                        option_timer = "checked"
                    else:
                        option_timer = "None"  

                    ### set checkbox sensors
                    if request.form.get("checkbox_option_sensors_" + str(i)):
                        option_sensors = "checked"
                    else:
                        option_sensors = "None"  

                    ### set checkbox expanded
                    if request.form.get("checkbox_option_expanded_" + str(i)):
                        option_expanded = "checked"
                    else:
                        option_expanded = "None"  

                    ### set checkbox repeat
                    if request.form.get("checkbox_option_repeat_" + str(i)):
                        option_repeat = "checked"
                    else:
                        option_repeat = "None"  


                    # #############
                    # time settings
                    # #############

                    ### set day
                    if request.form.get("set_day_" + str(i)) != "":
                        day = request.form.get("set_day_" + str(i))
                    else:
                        day = GET_SCHEDULER_TASK_BY_ID(i).day

                    ### set hour
                    if request.form.get("set_hour_" + str(i)) != "":
                        hour = request.form.get("set_hour_" + str(i))
                    else:
                        hour = GET_SCHEDULER_TASK_BY_ID(i).hour

                    ### set minute
                    if request.form.get("set_minute_" + str(i)) != "":
                        minute = request.form.get("set_minute_" + str(i))
                    else:
                        minute = GET_SCHEDULER_TASK_BY_ID(i).minute 


                    # ##############
                    # timer settings
                    # ##############    

                    ### set minutes
                    if request.form.get("set_timer_minutes_" + str(i)) != "":
                        timer_minutes = request.form.get("set_timer_minutes_" + str(i))
                    else:
                        timer_minutes = GET_SCHEDULER_TASK_BY_ID(i).timer_minutes

                    ### set seconds
                    if request.form.get("set_timer_seconds_" + str(i)) != "":
                        timer_seconds = request.form.get("set_timer_seconds_" + str(i))
                    else:
                        timer_seconds = GET_SCHEDULER_TASK_BY_ID(i).timer_seconds

                    ### set end task
                    if request.form.get("set_timer_endtask_" + str(i)) != "":
                        timer_endtask = request.form.get("set_timer_endtask_" + str(i))
                    else:
                        timer_endtask = GET_SCHEDULER_TASK_BY_ID(i).timer_endtask 


                    # ###############
                    # sensor settings
                    # ###############              

                    mqtt_device_id_1 = request.form.get("set_mqtt_device_id_1_" + str(i))
                    mqtt_device_id_2 = request.form.get("set_mqtt_device_id_2_" + str(i))
                    mqtt_device_id_3 = request.form.get("set_mqtt_device_id_3_" + str(i))                    
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
                        mqtt_device_name_1   = GET_MQTT_DEVICE_BY_ID(int(mqtt_device_id_1)).name
                        mqtt_device_inputs_1 = GET_MQTT_DEVICE_BY_ID(int(mqtt_device_id_1)).inputs

                        sensor_key_1 = request.form.get("set_sensor_1_" + str(i))
                        sensor_key_1 = sensor_key_1.replace(" ", "") 
                        if sensor_key_1.isdigit():
                            if sensor_key_1 == "0" or sensor_key_1 == "1":
                                sensor_key_1 = "None"
                            else:                                
                                sensor_list  = GET_MQTT_DEVICE_BY_ID(mqtt_device_id_1).inputs
                                sensor_list  = sensor_list.split(",")
                                sensor_key_1 = sensor_list[int(sensor_key_1)-2]
                            
                    except:
                        sensor_key_1 = "None"
                        mqtt_device_id_1 = "None"
                        mqtt_device_name_1 = "None"
                        mqtt_device_inputs_1 = "None"  

                    # get mqtt device 2
                    try:
                        mqtt_device_name_2   = GET_MQTT_DEVICE_BY_ID(int(mqtt_device_id_2)).name
                        mqtt_device_inputs_2 = GET_MQTT_DEVICE_BY_ID(int(mqtt_device_id_2)).inputs

                        sensor_key_2 = request.form.get("set_sensor_2_" + str(i))
                        sensor_key_2 = sensor_key_2.replace(" ", "") 
                        if sensor_key_2.isdigit():
                            if sensor_key_2 == "0" or sensor_key_2 == "1":
                                sensor_key_2 = "None"
                            else:                                
                                sensor_list  = GET_MQTT_DEVICE_BY_ID(mqtt_device_id_2).inputs
                                sensor_list  = sensor_list.split(",")
                                sensor_key_2 = sensor_list[int(sensor_key_2)-2]                   

                    except:
                        sensor_key_2 = "None"
                        mqtt_device_id_2 = "None"
                        mqtt_device_name_2 = "None"  
                        mqtt_device_inputs_2 = "None"   

                    # get mqtt device 3 
                    try:
                        mqtt_device_name_3   = GET_MQTT_DEVICE_BY_ID(int(mqtt_device_id_3)).name
                        mqtt_device_inputs_3 = GET_MQTT_DEVICE_BY_ID(int(mqtt_device_id_3)).inputs

                        sensor_key_3 = request.form.get("set_sensor_3_" + str(i))
                        sensor_key_3 = sensor_key_3.replace(" ", "") 
                        if sensor_key_3.isdigit():
                            if sensor_key_3 == "0" or sensor_key_3 == "1":
                                sensor_key_3 = "None"
                            else:                                
                                sensor_list  = GET_MQTT_DEVICE_BY_ID(mqtt_device_id_3).inputs
                                sensor_list  = sensor_list.split(",")
                                sensor_key_3 = sensor_list[int(sensor_key_3)-2]        

                    except:
                        sensor_key_3 = "None"
                        mqtt_device_id_3 = "None"
                        mqtt_device_name_3 = "None"  
                        mqtt_device_inputs_3 = "None"  


                    # #################
                    # expanded settings
                    # #################   

                    ### set expanded home
                    if request.form.get("checkbox_expanded_home_" + str(i)):
                        expanded_home = "checked"
                    else:
                        expanded_home = "None"  

                    ### set expanded away
                    if request.form.get("checkbox_expanded_away_" + str(i)):
                        expanded_away = "checked"
                    else:
                        expanded_away = "None"  


                    if expanded_home != "None" or expanded_away != "None":

                        ### set ip_addresses
                        if request.form.get("set_expanded_ip_adresses_" + str(i)) != "":
                            expanded_ip_adresses = request.form.get("set_expanded_ip_adresses_" + str(i))
                        else:
                            expanded_ip_adresses = "None"
                    
                    else:
                        expanded_ip_adresses = "None"


                    ### set expanded sunrise
                    if request.form.get("checkbox_expanded_sunrise_" + str(i)):
                        expanded_sunrise = "checked"
                    else:
                        expanded_sunrise = "None"  

                    ### set expanded sunset
                    if request.form.get("checkbox_expanded_sunset_" + str(i)):
                        expanded_sunset = "checked"
                    else:              
                        expanded_sunset = "None"  



                    SET_SCHEDULER_CHANGE_ERRORS(i, error_change_settings)

                    SET_SCHEDULER_TASK(i, name, task, 
                                          option_time, option_timer, option_sensors, option_expanded, option_repeat, 
                                          day, hour, minute,
                                          timer_minutes, timer_seconds, timer_endtask,
                                          mqtt_device_id_1, mqtt_device_name_1, mqtt_device_inputs_1, 
                                          sensor_key_1, operator_1, value_1, operator_main_1,
                                          mqtt_device_id_2, mqtt_device_name_2, mqtt_device_inputs_2, 
                                          sensor_key_2, operator_2, value_2, operator_main_2,
                                          mqtt_device_id_3, mqtt_device_name_3, mqtt_device_inputs_3, 
                                          sensor_key_3, operator_3, value_3,
                                          expanded_home, expanded_away, expanded_ip_adresses, expanded_sunrise, expanded_sunset)


    error_message_reduced_scheduler_tasks = CHECK_TASKS(GET_ALL_SCHEDULER_TASKS_BY_TYPE("reduced"), "scheduler")
    error_message_reduced_time_settings   = CHECK_SCHEDULER_TIME_SETTINGS(GET_ALL_SCHEDULER_TASKS_BY_TYPE("reduced"))

    error_message_scheduler_tasks   = CHECK_TASKS(GET_ALL_SCHEDULER_TASKS_BY_TYPE(""), "scheduler")
    error_message_time_settings     = CHECK_SCHEDULER_TIME_SETTINGS(GET_ALL_SCHEDULER_TASKS_BY_TYPE(""))
    error_message_timer_settings    = CHECK_SCHEDULER_TIMER_SETTINGS(GET_ALL_SCHEDULER_TASKS_BY_TYPE(""))
    error_message_sensor_settings   = CHECK_SCHEDULER_SENSOR_SETTINGS(GET_ALL_SCHEDULER_TASKS_BY_TYPE(""))
    error_message_expanded_settings = CHECK_SCHEDULER_EXPANDED_SETTINGS(GET_ALL_SCHEDULER_TASKS_BY_TYPE(""))

    scheduler_task_list = GET_ALL_SCHEDULER_TASKS()

    dropdown_list_mqtt_devices  = GET_ALL_MQTT_DEVICES("sensor")
    dropdown_list_operators     = ["=", ">", "<"]
    dropdown_list_operator_main = ["and", "or", "=", ">", "<"]

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
                            error_message_time_settings=error_message_time_settings,
                            error_message_timer_settings=error_message_timer_settings,
                            error_message_sensor_settings=error_message_sensor_settings,
                            error_message_expanded_settings=error_message_expanded_settings,
                            error_message_scheduler_tasks=error_message_scheduler_tasks,                        
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            dropdown_list_operators=dropdown_list_operators,
                            dropdown_list_operator_main=dropdown_list_operator_main,
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


# add scheduler sensor task option
@app.route('/dashboard/scheduler/sensor_option/add/<int:id>')
@login_required
@user_required
def add_scheduler_sensor_option(id):
    ADD_SCHEDULER_TASK_OPTION(id)
    return redirect(url_for('dashboard_scheduler'))


# remove scheduler sensor task option
@app.route('/dashboard/scheduler/sensor_option/remove/<int:id>')
@login_required
@user_required
def remove_scheduler_sensor_option(id):
    REMOVE_SCHEDULER_TASK_OPTION(id)
    return redirect(url_for('dashboard_scheduler'))


# delete scheduler task
@app.route('/dashboard/scheduler/delete/<int:id>')
@login_required
@user_required
def delete_scheduler_task(id):
    DELETE_SCHEDULER_TASK(id)
    return redirect(url_for('dashboard_scheduler'))
