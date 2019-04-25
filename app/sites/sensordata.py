from flask import render_template, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from flask_apscheduler import APScheduler
from functools import wraps

import datetime
import time
import pandas as pd

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.checks import CHECK_SENSORDATA_JOBS

# access rights
def user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "user" or current_user.role == "superuser":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


""" ############## """
""" sensordata jobs"""
""" ############## """

@app.route('/dashboard/sensordata/jobs', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_sensordata_jobs():
    error_message = ""
    error_message_table = ""
    error_message_form = ""
    error_message_file = ""
    name = ""
    filename = ""
    set_mqtt_device_id = ""
    set_mqtt_device_name = ""
    set_checkbox = ""

    if request.method == 'POST':
        if request.form.get("add_job") is not None: 

            if request.form.get("set_name") is "":
                # missing name
                error_message = "Kein Name angegeben"   
                filename = request.form.get("set_filename")  
                set_mqtt_device_id = request.form.get("set_mqtt_device_id") 
                
                if request.form.get("checkbox"):
                    set_checkbox = "checked"
                else:
                    set_checkbox = ""
                  
            elif request.form.get("set_filename") is "":
                # missing file name
                error_message = "Kein Deteiname angegeben"    
                name = request.form.get("set_name") 
                set_mqtt_device_id = request.form.get("set_mqtt_device_id")
                
                if request.form.get("checkbox"):
                    set_checkbox = "checked"
                else:
                    set_checkbox = ""
                
            else:
                # add sensordata job
                name = request.form.get("set_name") 
                filename = request.form.get("set_filename") 
                mqtt_device_id = request.form.get("set_mqtt_device_id") 
                
                if request.form.get("checkbox"):
                    always_active = "checked"
                else:
                    always_active = ""

                if mqtt_device_id is not None:
                    error_message = ADD_SENSORDATA_JOB(name, filename, mqtt_device_id, always_active)
                    error_message_file = CREATE_SENSORDATA_FILE(filename)
                    name = ""
                    filename = ""   


        # change settings
        if request.form.get("change_settings") != None: 
            for i in range (1,25):

                if request.form.get("set_name_" + str(i)) != None:  
                    
                    # check name
                    if (request.form.get("set_name_" + str(i)) != "" and 
                        GET_SENSORDATA_JOB_BY_NAME(request.form.get("set_name_" + str(i))) == None):
                        name = request.form.get("set_name_" + str(i)) 
                        
                    elif request.form.get("set_name_" + str(i)) == GET_SENSORDATA_JOB_BY_ID(i).name:
                        name = GET_SENSORDATA_JOB_BY_ID(i).name                        
                        
                    else:
                        name = GET_SENSORDATA_JOB_BY_ID(i).name 
                        error_message_form = "Ungültige Eingabe (leeres Feld / Name schon vergeben"                          
                    
                    # check filename
                    if request.form.get("set_filename_" + str(i)) != "":
                        filename = request.form.get("set_filename_" + str(i)) 
                    
                    else:
                        filename = GET_SENSORDATA_JOB_BY_ID(i).filename 
                        error_message_form = "Ungültige Eingabe (leeres Feld / Name schon vergeben"   
                                           
                
                    mqtt_device_id = request.form.get("set_mqtt_device_id_" + str(i)) 

                    if request.form.get("checkbox_table_" + str(i)):
                        always_active = "checked"
                    else:
                        always_active = ""  


                    if int(mqtt_device_id) == GET_SENSORDATA_JOB_BY_ID(i).mqtt_device_id:
                        sensor_key = request.form.get("set_sensor_" + str(i))
                        SET_SENSORDATA_JOB(i, name, filename, int(mqtt_device_id), sensor_key, always_active)

                    else:
                        # reset sensor_id if device changes
                        DELETE_SENSORDATA_JOB(i, "No_Log")
                        ADD_SENSORDATA_JOB(name, filename, mqtt_device_id, always_active, "Log_Change")
                        
                        
    error_message_table = CHECK_SENSORDATA_JOBS()

    dropdown_list_mqtt_devices = GET_ALL_MQTT_DEVICES("sensor")
    
    list_sensordata = GET_ALL_SENSORDATA_JOBS()
    list_files      = GET_SENSORDATA_FILES()

    if set_mqtt_device_id != "":
        set_mqtt_device_name = GET_MQTT_DEVICE_BY_ID(int(set_mqtt_device_id)).name

    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 

    return render_template('dashboard_sensordata_jobs.html',
                            name=name,
                            filename=filename,
                            set_mqtt_device_id=set_mqtt_device_id,
                            set_mqtt_device_name=set_mqtt_device_name,
                            set_checkbox=set_checkbox,
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            error_message=error_message,
                            error_message_table=error_message_table,
                            error_message_form=error_message_form,
                            error_message_file=error_message_file,
                            list_sensordata=list_sensordata,
                            list_files=list_files,     
                            timestamp=timestamp, 
                            jobs="active",
                            role=current_user.role,                      
                            )


# remove sensordata job
@app.route('/dashboard/sensordata/jobs/delete/job/<int:id>')
@login_required
@user_required
def remove_sensordata_job(id):
    DELETE_SENSORDATA_JOB(id)  
    return redirect(url_for('dashboard_sensordata_jobs'))


# download sensordata file
@app.route('/dashboard/sensordata/jobs/download/file/<path:filepath>')
@login_required
@user_required
def download_sensordata_file(filepath):
    if filepath is None:
        print("Ungültiger Pfad angegeben")     
    try:
        path = GET_PATH() + "/csv/"     
        WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /csv/" + filepath + " >>> downloaded")
        return send_from_directory(path, filepath)
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /csv/" + filepath + " >>> " + str(e)) 


# delete sensordata file
@app.route('/dashboard/sensordata/jobs/delete/file/<string:filename>')
@login_required
@user_required
def delete_sensordata_file(filename):
    DELETE_SENSORDATA_FILE(filename)
    return redirect(url_for('dashboard_sensordata_jobs'))


""" ##################### """
""" sensordata statistics """
""" ##################### """

@app.route('/dashboard/sensordata/statistics', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_sensordata_statistics():
    error_message = ""
    devices = ""
    sensors = ""
    time_min = ""
    time_max = ""
    data_file_1 = ""
    data_file_2 = ""
    data_file_3 = ""

    if request.method == 'POST':

        # get data
        if request.form.get("get_data") is not None: 
            data_file_1 = request.form.get("get_file_1")
            data_file_2 = request.form.get("get_file_2")
            data_file_3 = request.form.get("get_file_3")

            df_1 = READ_SENSORDATA_FILE(data_file_1)     

            # merge data sources
            if data_file_1 != data_file_2 and data_file_1 != data_file_3 and data_file_2 != data_file_3:

                try:
                    df_2 = READ_SENSORDATA_FILE(data_file_2)
                    df_1 = pd.concat([df_1, df_2], ignore_index=True)
                except:
                    pass           
                try:
                    df_3 = READ_SENSORDATA_FILE(data_file_3)
                    df_1 = pd.concat([df_1, df_3], ignore_index=True)
                except:
                    pass

                df = df_1

            else:
                df = df_1
                if data_file_2 == data_file_3 and data_file_2 != "":
                    error_message = "Datei " + data_file_2 + " mehrmals ausgewählt"
                if data_file_1 == data_file_2 or data_file_1 == data_file_3:
                    error_message = "Datei " + data_file_1 + " mehrmals ausgewählt"  

            # format data
            try:
                devices  = df.Device.unique().tolist()
                devices  = str(devices)
                devices  = devices[1:]
                devices  = devices[:-1]
                devices  = devices.replace("'", "") 
                sensors  = df.Sensor.unique().tolist()
                sensors  = str(sensors)                
                sensors  = sensors[1:]
                sensors  = sensors[:-1]
                sensors  = sensors.replace("'", "")

                time_min = min(df['Timestamp'])
                time_max = max(df['Timestamp'])

            except:
                error_message = "Datei konnte nicht geöffnet werden"


        # create table
        if request.form.get("create_table") is not None: 
            data_file_1 = request.form.get("get_file_1")
            data_file_2 = request.form.get("get_file_2")
            data_file_3 = request.form.get("get_file_3")

            df_1 = READ_SENSORDATA_FILE(data_file_1)     

            # merge data sources
            if data_file_1 != data_file_2 and data_file_1 != data_file_3 and data_file_2 != data_file_3:

                try:
                    df_2 = READ_SENSORDATA_FILE(data_file_2)
                    df_1 = pd.concat([df_1, df_2], ignore_index=True)
                except:
                    pass           
                try:
                    df_3 = READ_SENSORDATA_FILE(data_file_3)
                    df_1 = pd.concat([df_1, df_3], ignore_index=True)
                except:
                    pass

                df = df_1

            else:
                df = df_1
                if data_file_2 == data_file_3 and data_file_2 != "":
                    error_message = "Datei " + data_file_2 + " mehrmals ausgewählt"
                if data_file_1 == data_file_2 or data_file_1 == data_file_3:
                    error_message = "Datei " + data_file_1 + " mehrmals ausgewählt"                
           
            # create table           
            try:
                devices = request.form.get("set_devices")
                sensors = request.form.get("set_sensors")  

                selected_devices = devices.replace(" ", "")
                selected_devices = selected_devices.split(",")
                selected_sensors = sensors.replace(" ", "")
                selected_sensors = selected_sensors.split(",")

                df_devices = df.loc[df['Device'].isin(selected_devices)]
                df_sensors = df_devices.loc[df['Sensor'].isin(selected_sensors)]



                print(df_devices)
                print(df_sensors)

            except:
                error_message = "Datei konnte nicht verarbeitet werden"
        

    dropdown_list_files = GET_SENSORDATA_FILES()

    return render_template('dashboard_sensordata_statistics.html', 
                            error_message=error_message,
                            dropdown_list_files=dropdown_list_files,
                            devices=devices,
                            sensors=sensors,
                            data_file_1=data_file_1,
                            data_file_2=data_file_2,
                            data_file_3=data_file_3,
                            time_min=time_min,
                            time_max=time_max,
                            statistics="active",
                            role=current_user.role,                      
                            )
