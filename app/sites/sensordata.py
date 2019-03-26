from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_apscheduler import APScheduler
from functools import wraps
import datetime

from app import app
from app.database.database import *
from app.components.file_management import *

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


""" ########## """
""" sensordata """
""" ########## """

@app.route('/dashboard/sensordata', methods=['GET'])
@login_required
@superuser_required
def dashboard_sensordata():
    error_message = ""
    error_message_file = ""
    name = ""
    filename = ""

    if request.method == "GET": 
        # add sensordata job
        if request.args.get("set_name") is "":
            error_message = "Kein Name angegeben"   
            filename = request.args.get("set_filename")    
        elif request.args.get("set_filename") is "":
            error_message = "Kein Deteiname angegeben"    
            name = request.args.get("set_name") 
        else:
            name = request.args.get("set_name") 
            filename = request.args.get("set_filename") 
            mqtt_device_id = request.args.get("set_mqtt_device_id") 

            if mqtt_device_id is not None:
                error_message = ADD_SENSORDATA_JOB(name, filename, mqtt_device_id)
                error_message_file = CREATE_SENSORDATA_FILE(filename)
                name = ""
                filename = ""   

        for i in range (1,25):
            # change sensor
            if request.args.get("set_sensor_" + str(i)):
                sensor_id = request.args.get("set_sensor_" + str(i))    
                SET_SENSORDATA_JOB_SENSOR(i, sensor_id) 

    dropdown_list_mqtt_devices = GET_ALL_MQTT_DEVICES()
    sensordata_list = GET_ALL_SENSORDATA_JOBS()
    file_list = GET_SENSORDATA_FILES()

    return render_template('dashboard_sensordata.html',
                            name=name,
                            filename=filename,
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            error_message=error_message,
                            error_message_file=error_message_file,
                            sensordata_list=sensordata_list,
                            file_list=file_list,
                            )


# remove sensordata
@app.route('/dashboard/sensordata/delete/<int:id>')
@login_required
@superuser_required
def remove_sensordata(id):
    DELETE_SENSORDATA_JOB(id)
    return redirect(url_for('dashboard_sensordata'))


# delete sensordata file
@app.route('/dashboard/sensordata/delete/<string:filename>')
@login_required
@superuser_required
def delete_sensordata_file(filename):
    DELETE_SENSORDATA_FILE(filename)
    return redirect(url_for('dashboard_sensordata'))