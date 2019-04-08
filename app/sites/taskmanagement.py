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
                day    = request.form.get("set_day") 
                hour   = request.form.get("set_hour") 
                minute = request.form.get("set_minute")
                task   = request.form.get("set_task")
                
                if request.form.get("checkbox"):
                    repeat = "*"
                else:
                    repeat = ""

                error_message = ADD_TASKMANAGEMENT_TIME_TASK(name, day, hour, minute, task, repeat)             
 
    schedular_list = GET_ALL_TASKMANAGEMENT_TIME_TASKS()

    # dropdown values
    dropdown_list_days    = ["Mon", "Thu", "Wed", "Thu", "Fri", "Sat", "Sun"]
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
        if request.form.get("add_task") is not None:

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
        for i in range (1,25):
            if request.form.get("change_settings_" + str(i)) != None: 
                
                if request.form.get("set_sensor") != "None" and request.form.get("set_value") != "":
                    # set sensor + operator + value
                    sensor_id = request.form.get("set_sensor")   
                    operator = request.form.get("set_operator")   
                    value = request.form.get("set_value") 
                    SET_TASKMANAGEMENT_SENSOR(i, sensor_id, operator, value)                        
                        
                elif request.form.get("set_sensor") != "None" and request.form.get("set_value") == "":
                    # set sensor + operator
                    sensor_id = request.form.get("set_sensor")   
                    operator = request.form.get("set_operator")   
                    value = ""
                    SET_TASKMANAGEMENT_SENSOR(i, sensor_id, operator, value)
                    
                    error_message_table = "Keinen Vergleichswert angegeben"                 
   
                elif request.form.get("set_sensor") == "None" and request.form.get("set_value") != "":
                    # set operator + value
                    operator = request.form.get("set_operator")  
                    value = request.form.get("set_value") 
                    SET_TASKMANAGEMENT_SENSOR_WITHOUT_SENSOR(i, operator, value)  
                    
                    error_message_table = "Keinen Sensor angegeben"
                
                else:
                    error_message_table = "Keinen Sensor und keinen Vergleichswert angegeben"                                            
                    

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
