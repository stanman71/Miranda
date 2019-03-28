from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_apscheduler import APScheduler
from functools import wraps
import datetime

from app import app
from app.database.database import *
from app.components.tasks import *


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
@superuser_required
def dashboard_taskmanagement_time():
    error_message = ""
    set_name = ""
    set_task = ""

    if request.method == "POST": 
        # add new task
        if request.form.get("add_task") is not None:

            # controll name and task input
            if request.form.get("set_name") == "":
                error_message = "Kein Name angegeben"
                set_task = request.form.get("set_task")

            elif request.form.get("set_task") == "":
                error_message = "Keine Aufgabe angegeben"  
                set_name = request.form.get("set_name")  
                          
            else:         
                # get database informations
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
 
                name   = ""
                day    = ""
                hour   = ""
                minute = ""
                task   = ""
                repeat = ""      

    schedular_list = GET_ALL_TASKMANAGEMENT_TIME_TASKS()

    # dropdown values
    dropdown_list_days    = ["*", "Mon", "Thu", "Wed", "Thu", "Fri", "Sat", "Sun"]
    dropdown_list_hours   = ["*", "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", 
                             "12","13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]
    dropdown_list_minutes = ["*", "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", 
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
                            active01="active",
                            )


# delete taskmanagement time tasks
@app.route('/dashboard/taskmanagement/time/delete/<int:id>')
@login_required
@superuser_required
def delete_schedular_task(id):
    DELETE_TASKMANAGEMENT_TIME_TASK(id)
    return redirect(url_for('dashboard_taskmanagement_time'))


""" ##################### """
""" taskmanagement sensor """
""" ##################### """

@app.route('/dashboard/taskmanagement/sensor', methods=['GET'])
@login_required
@superuser_required
def dashboard_taskmanagement_sensor():
    error_message = ""

    return render_template('dashboard_taskmanagement_sensor.html',
                            error_message=error_message,
                            active02="active",
                            )
