from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_apscheduler import APScheduler
from functools import wraps
import datetime

from app import app
from app.database.database import *
from app.components.tasks import *


# access rights
def user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "user" or current_user.role == "superuser":
            return f(*args, **kwargs)
        else:
            form = LoginForm()
            return render_template('login.html', form=form, role_check=False)
    return wrap


""" ################### """
""" taskmanagement time """
""" ################### """

scheduler = APScheduler()
scheduler.start()   

@scheduler.task('cron', id='scheduler_job', minute='*')
def scheduler_job():
    entries = GET_ALL_TASKMANAGEMENT_TIME_TASKS()
    TASKMANAGEMENT_TIME_TASKS(entries)


@app.route('/dashboard/taskmanagement/time', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_taskmanagement_time():
    error_message = ""
    error_message_form = "" 
    error_message_tasks = ""
    set_name = ""
    set_task = ""
    set_day = ""
    set_hour = ""
    set_minute = ""
    set_checkbox = ""

    if request.method == "POST": 

        # add task
        if request.form.get("add_task") is not None:

            if request.form.get("set_name") == "":
                # missing name
                set_task   = request.form.get("set_task")
                set_day    = request.form.get("set_day") 
                set_hour   = request.form.get("set_hour") 
                set_minute = request.form.get("set_minute")
  
                if request.form.get("checkbox"):
                    set_checkbox = "checked"
                else:
                    set_checkbox = ""
                
                error_message = "Keinen Namen angegeben"

            elif request.form.get("set_task") == "":
                # missing task
                set_name = request.form.get("set_name")  
                set_day    = request.form.get("set_day") 
                set_hour   = request.form.get("set_hour") 
                set_minute = request.form.get("set_minute")  
   
                if request.form.get("checkbox"):
                    set_checkbox = "checked"
                else:
                    set_checkbox = ""  
                             
                error_message = "Keine Aufgabe angegeben"               
                          
            else:         
                # add new task
                name   = request.form.get("set_name")
                task   = request.form.get("set_task")
                day    = request.form.get("set_day") 
                hour   = request.form.get("set_hour") 
                minute = request.form.get("set_minute")
                
                if request.form.get("checkbox"):
                    repeat = "checked"
                else:
                    repeat = ""

                error_message = ADD_TASKMANAGEMENT_TIME_TASK(name, task, day, hour, minute, repeat)             
 

        # change settings
        if request.form.get("change_settings") != None: 
            for i in range (1,25):

                if request.form.get("set_name_" + str(i)) != None:

                    # ########
                    # set name
                    # ########

                    ### own name    
                    if request.form.get("set_name_" + str(i)) == GET_TASKMANAGEMENT_TIME_TASK_BY_ID(i).name:
                        name = GET_TASKMANAGEMENT_TIME_TASK_BY_ID(i).name
                    ### set new name
                    elif (request.form.get("set_name_" + str(i)) != "" and 
                        GET_TASKMANAGEMENT_TIME_TASK_BY_NAME(request.form.get("set_name_" + str(i))) == None):
                        name = request.form.get("set_name_" + str(i))  
                    ### name used
                    elif GET_TASKMANAGEMENT_TIME_TASK_BY_NAME(request.form.get("set_name_" + str(i))):
                        name = GET_TASKMANAGEMENT_TIME_TASK_BY_ID(i).name
                        error_message_form = name + " >>> Name schon vergeben"
                    ### name field empty
                    else:
                        name = GET_TASKMANAGEMENT_TIME_TASK_BY_ID(i).name
                              
                    ### set task
                    if request.form.get("set_task_" + str(i)) != "":
                        task = request.form.get("set_task_" + str(i))
                    else:
                        task = GET_TASKMANAGEMENT_TIME_TASK_BY_ID(i).task

                    ### set day
                    if request.form.get("set_day_" + str(i)) != "":
                        day = request.form.get("set_day_" + str(i))
                    else:
                        day = GET_TASKMANAGEMENT_TIME_TASK_BY_ID(i).day

                    ### set hour
                    if request.form.get("set_hour_" + str(i)) != "":
                        hour = request.form.get("set_hour_" + str(i))
                    else:
                        hour = GET_TASKMANAGEMENT_TIME_TASK_BY_ID(i).hour

                    ### set minute
                    if request.form.get("set_minute_" + str(i)) != "":
                        minute = request.form.get("set_minute_" + str(i))
                    else:
                        minute = GET_TASKMANAGEMENT_TIME_TASK_BY_ID(i).minute                                                                                      
                        
                    ### set checkbox
                    if request.form.get("checkbox_table_" + str(i)):
                        repeat = "checked"
                    else:
                        repeat = ""  

                    SET_TASKMANAGEMENT_TIME_TASK(i, name, task, day, hour, minute, repeat)


    error_message_settings = CHECK_ALL_TIMER_SETTINGS(GET_ALL_TASKMANAGEMENT_TIME_TASKS())
    error_message_tasks    = CHECK_TASKS(GET_ALL_TASKMANAGEMENT_TIME_TASKS(), "timer")
    
    schedular_list = GET_ALL_TASKMANAGEMENT_TIME_TASKS()


    return render_template('dashboard_taskmanagement_time.html',
                            schedular_list=schedular_list,
                            error_message=error_message,
                            error_message_form=error_message_form,
                            error_message_tasks=error_message_tasks,
                            error_message_settings=error_message_settings,
                            set_name=set_name,
                            set_task=set_task,
                            set_day=set_day,
                            set_hour=set_hour,
                            set_minute=set_minute,
                            set_checkbox=set_checkbox,
                            active01="active",
                            role=current_user.role,
                            )


# delete taskmanagement time tasks
@app.route('/dashboard/taskmanagement/time/delete/<int:id>')
@login_required
@user_required
def delete_schedular_task(id):
    DELETE_TASKMANAGEMENT_TIME_TASK(id)
    return redirect(url_for('dashboard_taskmanagement_time'))


""" ##################### """
""" taskmanagement sensor """
""" ##################### """

@app.route('/dashboard/taskmanagement/sensor', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_taskmanagement_sensor():
    error_message = ""
    error_message_table = ""
    error_message_form = ""
    error_message_tasks = ""
    set_name = ""
    set_task = ""
    mqtt_device_id_1 = "None"
    mqtt_device_name_1 = "None"
    mqtt_device_inputs_1 = "None"
    sensor_key_1 = "None"
    operator_1 = "None"
    value_1 = ""  
    operator_main_1 = "None"  
    mqtt_device_id_2 = "None"
    mqtt_device_name_2 = "None"
    mqtt_device_inputs_2 = "None"    
    sensor_key_2 = "None"
    operator_2 = "None"
    value_2 = ""
    operator_main_2 = "None"  
    mqtt_device_id_3 = "None"
    mqtt_device_name_3 = "None"
    mqtt_device_inputs_3 = "None"    
    sensor_key_3 = "None"
    operator_3 = "None"
    value_3 = ""

    if request.method == "POST": 
        if request.form.get("add_task") != None:

            if request.form.get("set_name") == "":
                # missing name 
                set_task           = request.form.get("set_task")
                error_message = "Keinen Namen angegeben"
            elif request.form.get("set_task") == "":
                # missing task
                set_name           = request.form.get("set_name")                
                error_message = "Keine Aufgabe angegeben" 
            else:         
                # add new task
                name           = request.form.get("set_name")
                task           = request.form.get("set_task")
                error_message = ADD_TASKMANAGEMENT_SENSOR_TASK(name, task)             
 
        # change settings
        if request.form.get("change_settings") != None:

            for i in range (1,25): 
                
                if request.form.get("set_name_" + str(i)) != None:
                    
                    # check name
                    if (request.form.get("set_name_" + str(i)) != "" and 
                        GET_TASKMANAGEMENT_SENSOR_TASK_BY_NAME(request.form.get("set_name_" + str(i))) == None):
                        name = request.form.get("set_name_" + str(i))              
                    elif request.form.get("set_name_" + str(i)) == GET_TASKMANAGEMENT_SENSOR_TASK_BY_ID(i).name:
                        name = GET_TASKMANAGEMENT_SENSOR_TASK_BY_ID(i).name                                               
                    else:
                        name = GET_TASKMANAGEMENT_SENSOR_TASK_BY_ID(i).name 
                        error_message_form = "Ungültige Eingabe (leeres Feld / Name schon vergeben" 
                        
                    # check task
                    if request.form.get("set_task_" + str(i)) != "":
                        task = request.form.get("set_task_" + str(i))
                    else:
                        task = GET_TASKMANAGEMENT_SENSOR_TASK_BY_ID(i).task 
                        error_message_form = "Ungültige Eingabe (leeres Feld / Name schon vergeben"                        

                    # check value 1
                    if request.form.get("set_value_1_" + str(i)) != "":
                        value_1 = request.form.get("set_value_1_" + str(i))
                    else:
                        value_1 = ""

                    # check value 2
                    if request.form.get("set_value_2_" + str(i)) != "":
                        value_2 = request.form.get("set_value_2_" + str(i))
                    else:
                        value_2 = ""

                    # check value 3
                    if request.form.get("set_value_2_" + str(i)) != "":
                        value_3 = request.form.get("set_value_2_" + str(i))                  
                    else:
                        value_3 = ""     

                    mqtt_device_id_1 = request.form.get("set_mqtt_device_id_1_" + str(i))
                    mqtt_device_id_2 = request.form.get("set_mqtt_device_id_2_" + str(i))
                    mqtt_device_id_3 = request.form.get("set_mqtt_device_id_3_" + str(i))                    
                    operator_1       = request.form.get("set_operator_1_" + str(i))
                    operator_2       = request.form.get("set_operator_2_" + str(i))
                    operator_3       = request.form.get("set_operator_3_" + str(i))                    
                    operator_main_1  = request.form.get("set_operator_main_1_" + str(i))
                    operator_main_2  = request.form.get("set_operator_main_2_" + str(i))

                    try:
                        if int(mqtt_device_id_1) != GET_TASKMANAGEMENT_SENSOR_TASK_BY_ID(i).mqtt_device_id_1:
                            sensor_key_1 = "None"
                        else:
                            sensor_key_1 = request.form.get("set_sensor_1_" + str(i))
                    except:
                        pass
                    try:
                        mqtt_device_name_1   = GET_MQTT_DEVICE_NAME(int(mqtt_device_id_1))
                        mqtt_device_inputs_1 = GET_MQTT_DEVICE_INPUTS_BY_ID(int(mqtt_device_id_1))
                    except:
                        pass

                    try:
                        if int(mqtt_device_id_2) != GET_TASKMANAGEMENT_SENSOR_TASK_BY_ID(i).mqtt_device_id_2:
                            sensor_key_2 = "None"
                        else:
                            sensor_key_2 = request.form.get("set_sensor_2_" + str(i))
                    except:
                        sensor_key_2 = "None"
                    try:
                        mqtt_device_name_2   = GET_MQTT_DEVICE_NAME(int(mqtt_device_id_2))
                        mqtt_device_inputs_2 = GET_MQTT_DEVICE_INPUTS_BY_ID(int(mqtt_device_id_2))
                    except:
                        pass  

                    try:
                        if int(mqtt_device_id_3) != GET_TASKMANAGEMENT_SENSOR_TASK_BY_ID(i).mqtt_device_id_3:
                            sensor_key_3 = "None"
                        else:
                            sensor_key_3 = request.form.get("set_sensor_3_" + str(i))
                    except:
                        sensor_key_3 = "None"
                    try:
                        mqtt_device_name_3   = GET_MQTT_DEVICE_NAME(int(mqtt_device_id_3))
                        mqtt_device_inputs_3 = GET_MQTT_DEVICE_INPUTS_BY_ID(int(mqtt_device_id_3))
                    except:
                        pass      

                    SET_TASKMANAGEMENT_SENSOR_TASK(i, name, task, mqtt_device_id_1, mqtt_device_name_1, mqtt_device_inputs_1, 
                                                                  sensor_key_1, operator_1, value_1, operator_main_1,
                                                                  mqtt_device_id_2, mqtt_device_name_2, mqtt_device_inputs_2, 
                                                                  sensor_key_2, operator_2, value_2, operator_main_2,
                                                                  mqtt_device_id_3, mqtt_device_name_3, mqtt_device_inputs_3, 
                                                                  sensor_key_3, operator_3, value_3)

                    mqtt_device_id_1 = "None"
                    mqtt_device_name_1 = "None"
                    mqtt_device_inputs_1 = "None"
                    sensor_key_1 = "None"
                    operator_1 = "None"
                    value_1 = ""  
                    operator_main_1 = "None"  
                    mqtt_device_id_2 = "None"
                    mqtt_device_name_2 = "None"
                    mqtt_device_inputs_2 = "None"    
                    sensor_key_2 = "None"
                    operator_2 = "None"
                    value_2 = ""
                    operator_main_2 = "None"  
                    mqtt_device_id_3 = "None"
                    mqtt_device_name_3 = "None"
                    mqtt_device_inputs_3 = "None"    
                    sensor_key_3 = "None"
                    operator_3 = "None"
                    value_3 = ""

    error_message_settings = CHECK_ALL_SENSOR_SETTINGS(GET_ALL_TASKMANAGEMENT_SENSOR_TASKS())
    error_message_tasks    = CHECK_TASKS(GET_ALL_TASKMANAGEMENT_SENSOR_TASKS(), "sensor")

    dropdown_list_mqtt_devices  = GET_ALL_MQTT_DEVICES("sensor")
    dropdown_list_operators     = ["=", ">", "<", "not"]
    dropdown_list_operator_main = ["and", "or", "=", ">", "<", "not"]

    schedular_list = GET_ALL_TASKMANAGEMENT_SENSOR_TASKS()
    
    return render_template('dashboard_taskmanagement_sensor.html',
                            error_message=error_message,
                            error_message_table=error_message_table,
                            error_message_form=error_message_form,
                            error_message_tasks=error_message_tasks,
                            error_message_settings=error_message_settings,
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            dropdown_list_operators=dropdown_list_operators,
                            dropdown_list_operator_main=dropdown_list_operator_main,
                            schedular_list=schedular_list,
                            set_name=set_name,
                            set_task=set_task,
                            active02="active",
                            role=current_user.role,
                            )


# delete taskmanagement time tasks
@app.route('/dashboard/taskmanagement/sensor/delete/<int:id>')
@login_required
@user_required
def delete_schedular_sensor(id):
    DELETE_TASKMANAGEMENT_SENSOR_TASK(id)
    return redirect(url_for('dashboard_taskmanagement_sensor'))
