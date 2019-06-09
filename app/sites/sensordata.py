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
from app.components.checks import CHECK_SENSORDATA_JOBS_SETTINGS
from app.components.build_graph import BUILD_GRAPH

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
    error_message_add_sensordata_job = ""
    error_message_settings = ""
    error_message_change_settings = []
    error_message_file = ""
    job_name = ""
    job_filename = ""
    mqtt_device_id = ""
    mqtt_device_name = ""
    checkbox = ""

    if request.method == 'POST':
        if request.form.get("add_job") is not None: 

            if request.form.get("set_job_name") is "":
                # missing name
                error_message_add_sensordata_job = "Kein Name angegeben"   
                job_filename = request.form.get("set_job_filename")  
                  
            elif request.form.get("set_job_filename") is "":
                # missing file name
                error_message_add_sensordata_job = "Kein Deteiname angegeben"    
                job_name = request.form.get("set_job_name") 
                
            else:
                # add sensordata job
                job_name = request.form.get("set_job_name") 
                job_filename = request.form.get("set_job_filename") 

                error_message_add_sensordata_job = ADD_SENSORDATA_JOB(job_name, job_filename)
                error_message_file = CREATE_SENSORDATA_FILE(job_filename)
                job_name = ""
                job_filename = ""   


        # change settings
        if request.form.get("change_settings") != None: 
            for i in range (1,26):

                if request.form.get("set_name_" + str(i)) != None:  
                    
                    job_data = GET_SENSORDATA_JOB_BY_ID(i)
                    new_name = request.form.get("set_name_" + str(i))

                    # add new name
                    if ((new_name != "") and (GET_SENSORDATA_JOB_BY_NAME(new_name) == None)):
                        name = request.form.get("set_name_" + str(i)) 
                      
                    # nothing changed 
                    elif new_name == job_data.name:
                        name = job_data.name                        
                        
                    # name already exist
                    elif ((GET_SENSORDATA_JOB_BY_NAME(new_name) != None) and (job_data.name != name)):
                        name = job_data.name 
                        error_message_change_settings.append(job_data.name + " >>> Name schon vergeben")

                    # no input commited
                    else:                          
                        name = GET_SENSORDATA_JOB_BY_ID(i).name 
                        error_message_change_settings.append(job_data.name + " >>> Keinen Namen angegeben")


                    # check filename
                    if request.form.get("set_filename_" + str(i)) != "":
                        filename = request.form.get("set_filename_" + str(i)) 
                    
                    else:
                        filename = GET_SENSORDATA_JOB_BY_ID(i).filename 
                        error_message_change_settings.append(job_data.name + " >>> Keine Datei angegeben")  
                                           
                    # check sensor
                    mqtt_device = request.form.get("set_mqtt_device_" + str(i)) 

                    if GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device):
                        mqtt_device_ieeeAddr = mqtt_device
                    elif GET_MQTT_DEVICE_BY_ID(mqtt_device):
                        mqtt_device_ieeeAddr = GET_MQTT_DEVICE_BY_ID(mqtt_device).ieeeAddr
                    else:
                        mqtt_device_ieeeAddr == ""

                    if mqtt_device_ieeeAddr == "":
                        error_message_change_settings.append(job_data.name + " >>> Keinen Sensor angegeben") 

                    else:
                        # replace array_position to sensor name 
                        sensor_key = request.form.get("set_sensor_" + str(i))
                        sensor_key = sensor_key.replace(" ", "")
                        
                        if sensor_key.isdigit():
                            
                            # first two array elements are no sensors
                            if sensor_key == "0" or sensor_key == "1":
                                sensor_key = "None"
                                
                            else:                                
                                sensor_list = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr).inputs
                                sensor_list = sensor_list.split(",")
                                sensor_key  = sensor_list[int(sensor_key)-2]

                        # get checkbox
                        if request.form.get("checkbox_table_" + str(i)):
                            always_active = "checked"
                        else:
                            always_active = ""  

                        SET_SENSORDATA_JOB(i, name, filename, mqtt_device_ieeeAddr, sensor_key, always_active)

    # get sensor list
    try:
        mqtt_device_1_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(1).inputs
        mqtt_device_1_inputs = mqtt_device_1_inputs.replace(" ", "")
    except:
        mqtt_device_1_inputs = ""
    try:
        mqtt_device_2_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(2).inputs
        mqtt_device_2_inputs = mqtt_device_2_inputs.replace(" ", "")
    except:
        mqtt_device_2_inputs = ""
    try:        
        mqtt_device_3_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(3).inputs
        mqtt_device_3_inputs = mqtt_device_3_inputs.replace(" ", "")
    except:
        mqtt_device_3_inputs = ""
    try:        
        mqtt_device_4_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(4).inputs
        mqtt_device_4_inputs = mqtt_device_4_inputs.replace(" ", "")
    except:
        mqtt_device_4_inputs = ""
    try:        
        mqtt_device_5_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(5).inputs
        mqtt_device_5_inputs = mqtt_device_5_inputs.replace(" ", "")
    except:
        mqtt_device_5_inputs = ""
    try:        
        mqtt_device_6_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(6).inputs
        mqtt_device_6_inputs = mqtt_device_6_inputs.replace(" ", "")
    except:
        mqtt_device_6_inputs = ""
    try:        
        mqtt_device_7_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(7).inputs
        mqtt_device_7_inputs = mqtt_device_7_inputs.replace(" ", "")
    except:
        mqtt_device_7_inputs = ""
    try:        
        mqtt_device_8_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(8).inputs
        mqtt_device_8_inputs = mqtt_device_8_inputs.replace(" ", "")
    except:
        mqtt_device_8_inputs = ""
    try:        
        mqtt_device_9_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(9).inputs
        mqtt_device_9_inputs = mqtt_device_9_inputs.replace(" ", "")
    except:
        mqtt_device_9_inputs = ""
    try:        
        mqtt_device_10_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(10).inputs
        mqtt_device_10_inputs = mqtt_device_10_inputs.replace(" ", "")
    except:
        mqtt_device_10_inputs = ""
    try:        
        mqtt_device_11_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(11).inputs
        mqtt_device_11_inputs = mqtt_device_11_inputs.replace(" ", "")
    except:
        mqtt_device_11_inputs = ""
    try:        
        mqtt_device_12_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(12).inputs
        mqtt_device_12_inputs = mqtt_device_12_inputs.replace(" ", "")
    except:
        mqtt_device_12_inputs = ""
    try:        
        mqtt_device_13_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(13).inputs
        mqtt_device_13_inputs = mqtt_device_13_inputs.replace(" ", "")
    except:
        mqtt_device_13_inputs = ""
    try:        
        mqtt_device_14_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(14).inputs
        mqtt_device_14_inputs = mqtt_device_14_inputs.replace(" ", "")
    except:
        mqtt_device_14_inputs = ""
    try:        
        mqtt_device_15_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(15).inputs
        mqtt_device_15_inputs = mqtt_device_15_inputs.replace(" ", "")
    except:
        mqtt_device_15_inputs = ""    
    try:        
        mqtt_device_16_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(16).inputs
        mqtt_device_16_inputs = mqtt_device_16_inputs.replace(" ", "")
    except:
        mqtt_device_16_inputs = ""
    try:        
        mqtt_device_17_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(17).inputs
        mqtt_device_17_inputs = mqtt_device_17_inputs.replace(" ", "")
    except:
        mqtt_device_17_inputs = ""
    try:        
        mqtt_device_18_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(18).inputs
        mqtt_device_18_inputs = mqtt_device_18_inputs.replace(" ", "")
    except:
        mqtt_device_18_inputs = ""
    try:        
        mqtt_device_19_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(19).inputs
        mqtt_device_19_inputs = mqtt_device_19_inputs.replace(" ", "")
    except:
        mqtt_device_19_inputs = ""
    try:        
        mqtt_device_20_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(20).inputs
        mqtt_device_20_inputs = mqtt_device_20_inputs.replace(" ", "")
    except:
        mqtt_device_20_inputs = ""   
    try:        
        mqtt_device_21_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(21).inputs
        mqtt_device_21_inputs = mqtt_device_21_inputs.replace(" ", "")
    except:
        mqtt_device_21_inputs = ""   
    try:        
        mqtt_device_22_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(22).inputs
        mqtt_device_22_inputs = mqtt_device_22_inputs.replace(" ", "")
    except:
        mqtt_device_22_inputs = ""   
    try:        
        mqtt_device_23_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(23).inputs
        mqtt_device_23_inputs = mqtt_device_23_inputs.replace(" ", "")
    except:
        mqtt_device_23_inputs = ""   
    try:        
        mqtt_device_24_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(24).inputs
        mqtt_device_24_inputs = mqtt_device_24_inputs.replace(" ", "")
    except:
        mqtt_device_24_inputs = ""   
    try:        
        mqtt_device_25_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(25).inputs
        mqtt_device_25_inputs = mqtt_device_25_inputs.replace(" ", "")
    except:
        mqtt_device_25_inputs = ""           


    if error_message_change_settings == []:
        error_message_change_settings = ""

    error_message_settings = CHECK_SENSORDATA_JOBS_SETTINGS()

    dropdown_list_mqtt_devices = GET_ALL_MQTT_DEVICES("sensor")
    
    list_sensordata = GET_ALL_SENSORDATA_JOBS()
    list_files      = GET_SENSORDATA_FILES()

    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 

    return render_template('dashboard_sensordata_jobs.html',
                            job_name=job_name,
                            job_filename=job_filename,
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            error_message_add_sensordata_job=error_message_add_sensordata_job,
                            error_message_settings=error_message_settings,
                            error_message_change_settings=error_message_change_settings,
                            error_message_file=error_message_file,
                            list_sensordata=list_sensordata,
                            list_files=list_files,     
                            timestamp=timestamp, 
                            jobs="active",
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


# change sensordata job position 
@app.route('/dashboard/sensordata/jobs/position/<string:direction>/<int:id>')
@login_required
@user_required
def change_sensordata_jobs_position(id, direction):
    CHANGE_SENSORDATA_JOBS_POSITION(id, direction)
    return redirect(url_for('dashboard_sensordata_jobs'))


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
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /csv/" + filepath + " | downloaded")
        return send_from_directory(path, filepath)
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /csv/" + filepath + " | " + str(e)) 


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
    graph = False

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
            
                # complete list
                df_devices = df.loc[df['Device'].isin(selected_devices)]
                #print(df_devices)
                
                # selected divices
                df_sensors = df_devices.loc[df['Sensor'].isin(selected_sensors)]
                #print(df_sensors)

                
                # set datetime as index and remove former row datetime
                df_sensors['date'] = pd.to_datetime(df_sensors['Timestamp'], format='%Y-%m-%d %H:%M:%S', utc=True).values
                
                df_sensors = df_sensors.set_index('date')
                df_sensors = df_sensors.drop(columns=['Timestamp'])


                #print(df_sensors.index)

                graph  = BUILD_GRAPH(df_sensors)

            except:
                error_message = "Daten konnten nicht verarbeitet werden"
                     

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
                            graph=graph,
                            statistics="active",
                            role=current_user.role,                      
                            )
