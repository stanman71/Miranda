from flask import render_template, redirect, url_for, request, send_from_directory
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

@app.route('/dashboard/sensordata', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_sensordata():
    error_message = ""
    error_message_file = ""
    name = ""
    filename = ""

    if request.method == 'POST':
        if request.form.get("add_job") is not None: 
            # add sensordata job
            if request.form.get("set_name") is "":
                error_message = "Kein Name angegeben"   
                filename = request.form.get("set_filename")    
            elif request.form.get("set_filename") is "":
                error_message = "Kein Deteiname angegeben"    
                name = request.form.get("set_name") 
            else:
                name = request.form.get("set_name") 
                filename = request.form.get("set_filename") 
                mqtt_device_id = request.form.get("set_mqtt_device_id") 

                if mqtt_device_id is not None:
                    error_message = ADD_SENSORDATA_JOB(name, filename, mqtt_device_id)
                    error_message_file = CREATE_SENSORDATA_FILE(filename)
                    name = ""
                    filename = ""   

        # change settings
        if request.form.get("change_settings") is not None: 
            for i in range (1,25):
                if request.form.get("set_sensor_" + str(i)):
                    sensor_id = request.form.get("set_sensor_" + str(i))    
                    SET_SENSORDATA_JOB_SENSOR(i, int(sensor_id))

    dropdown_list_mqtt_devices = GET_ALL_MQTT_DEVICES()
    sensordata_list = GET_ALL_SENSORDATA_JOBS()
    file_list = GET_SENSORDATA_FILES()

    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 

    return render_template('dashboard_sensordata.html',
                            name=name,
                            filename=filename,
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            error_message=error_message,
                            error_message_file=error_message_file,
                            sensordata_list=sensordata_list,
                            file_list=file_list,     
                            timestamp=timestamp,                       
                            )


# remove sensordata job
@app.route('/dashboard/sensordata/delete/job/<int:id>')
@login_required
@superuser_required
def remove_sensordata_job(id):
    DELETE_SENSORDATA_JOB(id)  
    return redirect(url_for('dashboard_sensordata'))


# download sensordata file
@app.route('/dashboard/sensordata/download/file/<path:filepath>')
@login_required
@superuser_required
def download_sensordata_file(filepath):
    if filepath is None:
        print(Error(400))     
    try:
        path = GET_PATH() + "/csv/"     
        return send_from_directory(path, filepath)
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Sensordata_File: " + filepath + ", " + e) 


# delete sensordata file
@app.route('/dashboard/sensordata/delete/file/<string:filename>')
@login_required
@superuser_required
def delete_sensordata_file(filename):
    DELETE_SENSORDATA_FILE(filename)
    return redirect(url_for('dashboard_sensordata'))
