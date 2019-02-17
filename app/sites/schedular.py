from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_apscheduler import APScheduler
from functools import wraps
import datetime

from app import app
from app.components.led_control import *
from app.components.sensors_control import *
from app.components.plants_control import *
from app.database.database_operations import *


# create role "superuser"
def superuser_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "superuser":
            return f(*args, **kwargs)
        else:
            form = LoginForm()
            return render_template('login.html', form=form, role_check=False)
    return wrap


""" ######### """
""" schedular """
""" ######### """

scheduler = APScheduler()
scheduler.start()   

@scheduler.task('cron', id='scheduler_job', minute='*')
def scheduler_job():
    now    = datetime.datetime.now()
    day    = now.strftime('%a')
    hour   = now.strftime('%H')
    minute = now.strftime('%M')

    entries = GET_ALL_TASKS()

    for entry in entries:
        if entry.day == day or entry.day == "*":
            if entry.hour == hour or entry.hour == "*":
                if entry.minute == minute or entry.minute == "*":
                    print(entry.name)
                    # start scene
                    if "start_scene" in entry.task:
                        task = entry.task.split(":")
                        LED_SET_SCENE(int(task[1]))
                    # start program
                    if "start_program" in entry.task:
                        task = entry.task.split(":")
                        START_PROGRAM(int(task[1]))
                    # turn off leds
                    if "led_off" in entry.task:
                        task = entry.task.split(":")
                        LED_OFF(int(task[1])) 
                    # save sensor
                    if "save_sensor" in entry.task:
                        task = entry.task.split(":")
                        SAVE_SENSOR_GPIO(task[1])                          
                    # watering plants
                    if "watering_plants" in entry.task:
                        WATERING_PLANTS()
                    # start led automatically
                    if "start_smartphone" in entry.task:
                        task = entry.task.split(":")
                        hostname = "google.com"
                        if os.system("ping -n 1 " + hostname) == 0:
                            print("ok")
                            #if READ_SENSOR("GPIO_A07") < 600:
                            #    LED_SET_SCENE(int(task[1]))                                                                                                                        
                    # remove task without repeat
                    if entry.repeat == "":
                        DELETE_TASK(entry.id)


""" ########## """
""" tasks site """
""" ########## """

# Dashboard tasks
@app.route('/dashboard/schedular/', methods=['GET'])
@login_required
@superuser_required
def dashboard_schedular():
    error_massage = ""
    set_name = ""
    set_task = ""

    if request.method == "GET": 
        # add new task
        if request.args.get("set_name") is not None:
            # controll name and task input
            if request.args.get("set_name") == "":
                error_massage = "Kein Name angegeben"
                set_task = request.args.get("set_task")
            elif request.args.get("set_task") == "":
                error_massage = "Keine Aufgabe angegeben"  
                set_name = request.args.get("set_name")             
            else:         
                # get database informations
                name   = request.args.get("set_name")
                day    = request.args.get("set_day") 
                hour   = request.args.get("set_hour") 
                minute = request.args.get("set_minute")
                task   = request.args.get("set_task")
                if request.args.get("checkbox"):
                    repeat = "*"
                else:
                    repeat = ""

                error_massage = ADD_TASK(name, day, hour, minute, task, repeat)
 
    schedular_list = GET_ALL_TASKS()

    # dropdown values
    dropdown_list_days    = ["*", "Mon", "Thu", "Wed", "Thu", "Fri", "Sat", "Sun"]
    dropdown_list_hours   = ["*", "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", 
                             "12","13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]
    dropdown_list_minutes = ["*", "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", 
                             "12","13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", 
                             "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36","37",
                             "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48","49", "50",
                             "51", "52", "53", "54", "55", "56", "57", "58", "59"]

    return render_template('dashboard_schedular.html',
                            dropdown_list_days=dropdown_list_days,
                            dropdown_list_hours=dropdown_list_hours,
                            dropdown_list_minutes=dropdown_list_minutes,
                            schedular_list=schedular_list,
                            error_massage=error_massage,
                            set_name=set_name,
                            set_task=set_task
                            )


# Delete tasks
@app.route('/dashboard/schedular/delete/<int:id>')
@login_required
@superuser_required
def delete_schedular(id):
    DELETE_TASK(id)
    return redirect(url_for('dashboard_schedular'))
