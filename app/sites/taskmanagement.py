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

                if request.form.get("set_task_" + str(i)) != None:

                    # set task + day + hour + minute
                    if request.form.get("set_task_" + str(i)) != "":

                        task   = request.form.get("set_task_" + str(i))
                        day    = request.form.get("set_day_" + str(i))
                        hour   = request.form.get("set_hour_" + str(i))
                        minute = request.form.get("set_minute_" + str(i))

                        if request.form.get("checkbox_table_" + str(i)):
                            repeat = "checked"
                        else:
                            repeat = ""  

                        SET_TASKMANAGEMENT_TIME_TASK(i, task, day, hour, minute, repeat)

                    # day + hour + minute
                    else:

                        day    = request.form.get("set_day_" + str(i))
                        hour   = request.form.get("set_hour_" + str(i))
                        minute = request.form.get("set_minute_" + str(i))

                        if request.form.get("checkbox_table_" + str(i)):
                            repeat = "checked"
                        else:
                            repeat = ""  

                        SET_TASKMANAGEMENT_TIME_TASK_WITHOUT_TASK(i, day, hour, minute, repeat)


    schedular_list = GET_ALL_TASKMANAGEMENT_TIME_TASKS()

    # dropdown values
    dropdown_list_days    = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    dropdown_list_hours   = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", 
                             "12","13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]
    dropdown_list_minutes = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", 
                             "12","13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", 
                             "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36","37",
                             "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48","49", "50",
                             "51", "52", "53", "54", "55", "56", "57", "58", "59"]


    return render_template('dashboard_taskmanagement_time.html',
                            dropdown_list_days=dropdown_list_days,
                            dropdown_list_hours=dropdown_list_hours,
                            dropdown_list_minutes=dropdown_list_minutes,
                            schedular_list=schedular_list,
                            error_message=error_message,
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
    set_name = ""
    set_task = ""
    set_value = ""
    set_mqtt_device_id = ""
    set_mqtt_device_name = ""
    set_operator = ""
    

    if request.method == "POST": 
        if request.form.get("add_task") != None:

            if request.form.get("set_name") == "":
                # missing name 
                set_task           = request.form.get("set_task")
                set_value          = request.form.get("set_value")
                set_mqtt_device_id = request.form.get("set_mqtt_device_id")
                set_operator       = request.form.get("set_operator")
                
                error_message = "Keinen Namen angegeben"

            elif request.form.get("set_task") == "":
                # missing task
                set_name           = request.form.get("set_name") 
                set_value          = request.form.get("set_value")
                set_mqtt_device_id = request.form.get("set_mqtt_device_id")
                set_operator       = request.form.get("set_operator")
                
                error_message = "Keine Aufgabe angegeben" 

            elif request.form.get("set_value") == "":
                # missing value
                set_name           = request.form.get("set_name") 
                set_task           = request.form.get("set_task")
                set_mqtt_device_id = request.form.get("set_mqtt_device_id")
                set_operator       = request.form.get("set_operator")
                
                error_message = "Keine Vergleichswert angegeben"  

            else:         
                # add new task
                name           = request.form.get("set_name")
                task           = request.form.get("set_task")
                mqtt_device_id = request.form.get("set_mqtt_device_id")
                operator       = request.form.get("set_operator")
                value          = request.form.get("set_value")

                error_message = ADD_TASKMANAGEMENT_SENSOR_TASK(name, task, mqtt_device_id, operator, value)             
 
        # change settings
        if request.form.get("change_settings") != None:
            for i in range (1,25): 

                if request.form.get("set_task_" + str(i)) != None:

                    # set task + mqtt_device_id + operator + sensor_id + value
                    if request.form.get("set_task_" + str(i)) != "" and request.form.get("set_value_" + str(i)) != "":

                        task   = request.form.get("set_task_" + str(i))
                        mqtt_device_id = request.form.get("set_mqtt_device_id_" + str(i))
                        operator = request.form.get("set_operator_" + str(i))   
                        value = request.form.get("set_value_" + str(i)) 
                      
                        if int(mqtt_device_id) == GET_TASKMANAGEMENT_SENSOR_TASK_ID(i).mqtt_device_id:
                            sensor_id = request.form.get("set_sensor_" + str(i))
                            SET_TASKMANAGEMENT_SENSOR_TASK(i, task, mqtt_device_id, sensor_id, operator, value)

                        else:
                            # reset sensor_id if device changes
                            name = GET_TASKMANAGEMENT_SENSOR_TASK_ID(i).name
                            DELETE_TASKMANAGEMENT_SENSOR_TASK(i, "No_Log")
                            ADD_TASKMANAGEMENT_SENSOR_TASK(name, task, mqtt_device_id, operator, value, "No_Log")  

                    # set mqtt_device_id + operator + sensor_id + value
                    if request.form.get("set_task_" + str(i)) == "" and request.form.get("set_value_" + str(i)) != "":

                        mqtt_device_id = request.form.get("set_mqtt_device_id_" + str(i))
                        operator = request.form.get("set_operator_" + str(i))   
                        value = request.form.get("set_value_" + str(i))

                        if int(mqtt_device_id) == GET_TASKMANAGEMENT_SENSOR_TASK_ID(i).mqtt_device_id:
                            sensor_id = request.form.get("set_sensor_" + str(i))
                            SET_TASKMANAGEMENT_SENSOR_TASK_WITHOUT_TASK(i, mqtt_device_id, sensor_id, operator, value)

                        else:
                            # reset sensor_id if device changes
                            name = GET_TASKMANAGEMENT_SENSOR_TASK_ID(i).name
                            task = GET_TASKMANAGEMENT_SENSOR_TASK_ID(i).task
                            DELETE_TASKMANAGEMENT_SENSOR_TASK(i, "No_Log")
                            ADD_TASKMANAGEMENT_SENSOR_TASK(name, task, mqtt_device_id, operator, value, "No_Log")  

                    # set task + mqtt_device_id + operator + sensor_id
                    if request.form.get("set_task_" + str(i)) != "" and request.form.get("set_value_" + str(i)) == "":

                        task   = request.form.get("set_task_" + str(i))
                        mqtt_device_id = request.form.get("set_mqtt_device_id_" + str(i))
                        operator = request.form.get("set_operator_" + str(i))   
                      
                        if int(mqtt_device_id) == GET_TASKMANAGEMENT_SENSOR_TASK_ID(i).mqtt_device_id:
                            sensor_id = request.form.get("set_sensor_" + str(i))
                            SET_TASKMANAGEMENT_SENSOR_TASK_WITHOUT_VALUE(i, task, mqtt_device_id, sensor_id, operator)

                        else:
                            # reset sensor_id if device changes
                            name  = GET_TASKMANAGEMENT_SENSOR_TASK_ID(i).name
                            value = GET_TASKMANAGEMENT_SENSOR_TASK_ID(i).value
                            DELETE_TASKMANAGEMENT_SENSOR_TASK(i, "No_Log")
                            ADD_TASKMANAGEMENT_SENSOR_TASK(name, task, mqtt_device_id, operator, value, "No_Log")  
                                  
                    # set mqtt_device_id + operator + sensor_id
                    if request.form.get("set_task_" + str(i)) == "" and request.form.get("set_value_" + str(i)) == "":

                        mqtt_device_id = request.form.get("set_mqtt_device_id_" + str(i))
                        operator = request.form.get("set_operator_" + str(i))   

                        if int(mqtt_device_id) == GET_TASKMANAGEMENT_SENSOR_TASK_ID(i).mqtt_device_id:
                            sensor_id = request.form.get("set_sensor_" + str(i))
                            SET_TASKMANAGEMENT_SENSOR_TASK_WITHOUT_TASK_AND_VALUE(i, mqtt_device_id, sensor_id, operator)

                        else:
                            # reset sensor_id if device changes
                            name  = GET_TASKMANAGEMENT_SENSOR_TASK_ID(i).name
                            task  = GET_TASKMANAGEMENT_SENSOR_TASK_ID(i).task
                            value = GET_TASKMANAGEMENT_SENSOR_TASK_ID(i).value
                            DELETE_TASKMANAGEMENT_SENSOR_TASK(i, "No_Log")
                            ADD_TASKMANAGEMENT_SENSOR_TASK(name, task, mqtt_device_id, operator, value, "No_Log")  

    error_message_table = CHECK_TASKMANAGEMENT_SENSOR_TASKS()

    dropdown_list_mqtt_devices = GET_ALL_MQTT_DEVICES("sensor")
    dropdown_list_operators    = ["==", ">", "<"]

    schedular_list = GET_ALL_TASKMANAGEMENT_SENSOR_TASKS()
    
    if set_mqtt_device_id != "":
        set_mqtt_device_name = GET_MQTT_DEVICE_NAME(int(set_mqtt_device_id))

    return render_template('dashboard_taskmanagement_sensor.html',
                            error_message=error_message,
                            error_message_table=error_message_table,
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            dropdown_list_operators=dropdown_list_operators,
                            schedular_list=schedular_list,
                            set_name=set_name,
                            set_task=set_task,
                            set_value=set_value,
                            set_mqtt_device_id=set_mqtt_device_id,
                            set_mqtt_device_name=set_mqtt_device_name,
                            set_operator=set_operator,
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
