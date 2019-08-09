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
def permission_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.permission_sensordata == "checked":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('logout'))
    return wrap


""" ############## """
""" sensordata jobs"""
""" ############## """

@app.route('/dashboard/sensordata/jobs', methods=['GET', 'POST'])
@login_required
@permission_required
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
                                sensor_list = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr).input_values
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
        mqtt_device_1_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(1).input_values
        mqtt_device_1_input_values = mqtt_device_1_input_values.replace(" ", "")
    except:
        mqtt_device_1_input_values = ""
    try:
        mqtt_device_2_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(2).input_values
        mqtt_device_2_input_values = mqtt_device_2_input_values.replace(" ", "")
    except:
        mqtt_device_2_input_values = ""
    try:        
        mqtt_device_3_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(3).input_values
        mqtt_device_3_input_values = mqtt_device_3_input_values.replace(" ", "")
    except:
        mqtt_device_3_input_values = ""
    try:        
        mqtt_device_4_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(4).input_values
        mqtt_device_4_input_values = mqtt_device_4_input_values.replace(" ", "")
    except:
        mqtt_device_4_input_values = ""
    try:        
        mqtt_device_5_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(5).input_values
        mqtt_device_5_input_values = mqtt_device_5_input_values.replace(" ", "")
    except:
        mqtt_device_5_input_values = ""
    try:        
        mqtt_device_6_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(6).input_values
        mqtt_device_6_input_values = mqtt_device_6_input_values.replace(" ", "")
    except:
        mqtt_device_6_input_values = ""
    try:        
        mqtt_device_7_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(7).input_values
        mqtt_device_7_input_values = mqtt_device_7_input_values.replace(" ", "")
    except:
        mqtt_device_7_input_values = ""
    try:        
        mqtt_device_8_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(8).input_values
        mqtt_device_8_input_values = mqtt_device_8_input_values.replace(" ", "")
    except:
        mqtt_device_8_input_values = ""
    try:        
        mqtt_device_9_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(9).input_values
        mqtt_device_9_input_values = mqtt_device_9_input_values.replace(" ", "")
    except:
        mqtt_device_9_input_values = ""
    try:        
        mqtt_device_10_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(10).input_values
        mqtt_device_10_input_values = mqtt_device_10_input_values.replace(" ", "")
    except:
        mqtt_device_10_input_values = ""
    try:        
        mqtt_device_11_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(11).input_values
        mqtt_device_11_input_values = mqtt_device_11_input_values.replace(" ", "")
    except:
        mqtt_device_11_input_values = ""
    try:        
        mqtt_device_12_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(12).input_values
        mqtt_device_12_input_values = mqtt_device_12_input_values.replace(" ", "")
    except:
        mqtt_device_12_input_values = ""
    try:        
        mqtt_device_13_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(13).input_values
        mqtt_device_13_input_values = mqtt_device_13_input_values.replace(" ", "")
    except:
        mqtt_device_13_input_values = ""
    try:        
        mqtt_device_14_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(14).input_values
        mqtt_device_14_input_values = mqtt_device_14_input_values.replace(" ", "")
    except:
        mqtt_device_14_input_values = ""
    try:        
        mqtt_device_15_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(15).input_values
        mqtt_device_15_input_values = mqtt_device_15_input_values.replace(" ", "")
    except:
        mqtt_device_15_input_values = ""    
    try:        
        mqtt_device_16_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(16).input_values
        mqtt_device_16_input_values = mqtt_device_16_input_values.replace(" ", "")
    except:
        mqtt_device_16_input_values = ""
    try:        
        mqtt_device_17_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(17).input_values
        mqtt_device_17_input_values = mqtt_device_17_input_values.replace(" ", "")
    except:
        mqtt_device_17_input_values = ""
    try:        
        mqtt_device_18_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(18).input_values
        mqtt_device_18_input_values = mqtt_device_18_input_values.replace(" ", "")
    except:
        mqtt_device_18_input_values = ""
    try:        
        mqtt_device_19_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(19).input_values
        mqtt_device_19_input_values = mqtt_device_19_input_values.replace(" ", "")
    except:
        mqtt_device_19_input_values = ""
    try:        
        mqtt_device_20_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(20).input_values
        mqtt_device_20_input_values = mqtt_device_20_input_values.replace(" ", "")
    except:
        mqtt_device_20_input_values = ""   
    try:        
        mqtt_device_21_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(21).input_values
        mqtt_device_21_input_values = mqtt_device_21_input_values.replace(" ", "")
    except:
        mqtt_device_21_input_values = ""   
    try:        
        mqtt_device_22_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(22).input_values
        mqtt_device_22_input_values = mqtt_device_22_input_values.replace(" ", "")
    except:
        mqtt_device_22_input_values = ""   
    try:        
        mqtt_device_23_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(23).input_values
        mqtt_device_23_input_values = mqtt_device_23_input_values.replace(" ", "")
    except:
        mqtt_device_23_input_values = ""   
    try:        
        mqtt_device_24_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(24).input_values
        mqtt_device_24_input_values = mqtt_device_24_input_values.replace(" ", "")
    except:
        mqtt_device_24_input_values = ""   
    try:        
        mqtt_device_25_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(25).input_values
        mqtt_device_25_input_values = mqtt_device_25_input_values.replace(" ", "")
    except:
        mqtt_device_25_input_values = ""       


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
                            mqtt_device_1_input_values=mqtt_device_1_input_values,
                            mqtt_device_2_input_values=mqtt_device_2_input_values,
                            mqtt_device_3_input_values=mqtt_device_3_input_values,
                            mqtt_device_4_input_values=mqtt_device_4_input_values,
                            mqtt_device_5_input_values=mqtt_device_5_input_values,
                            mqtt_device_6_input_values=mqtt_device_6_input_values,
                            mqtt_device_7_input_values=mqtt_device_7_input_values,
                            mqtt_device_8_input_values=mqtt_device_8_input_values,
                            mqtt_device_9_input_values=mqtt_device_9_input_values,
                            mqtt_device_10_input_values=mqtt_device_10_input_values,
                            mqtt_device_11_input_values=mqtt_device_11_input_values,
                            mqtt_device_12_input_values=mqtt_device_12_input_values,
                            mqtt_device_13_input_values=mqtt_device_13_input_values,
                            mqtt_device_14_input_values=mqtt_device_14_input_values,
                            mqtt_device_15_input_values=mqtt_device_15_input_values,
                            mqtt_device_16_input_values=mqtt_device_16_input_values,
                            mqtt_device_17_input_values=mqtt_device_17_input_values,
                            mqtt_device_18_input_values=mqtt_device_18_input_values,
                            mqtt_device_19_input_values=mqtt_device_19_input_values,
                            mqtt_device_20_input_values=mqtt_device_20_input_values,  
                            mqtt_device_21_input_values=mqtt_device_21_input_values,
                            mqtt_device_22_input_values=mqtt_device_22_input_values,  
                            mqtt_device_23_input_values=mqtt_device_23_input_values,
                            mqtt_device_24_input_values=mqtt_device_24_input_values,
                            mqtt_device_25_input_values=mqtt_device_25_input_values,                                                                                                                                                                   
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system,                      
                            )


# change sensordata job position 
@app.route('/dashboard/sensordata/jobs/position/<string:direction>/<int:id>')
@login_required
@permission_required
def change_sensordata_jobs_position(id, direction):
    CHANGE_SENSORDATA_JOBS_POSITION(id, direction)
    return redirect(url_for('dashboard_sensordata_jobs'))


# remove sensordata job
@app.route('/dashboard/sensordata/jobs/delete/job/<int:id>')
@login_required
@permission_required
def remove_sensordata_job(id):
    DELETE_SENSORDATA_JOB(id)  
    return redirect(url_for('dashboard_sensordata_jobs'))


# download sensordata file
@app.route('/dashboard/sensordata/jobs/download/file/<path:filepath>')
@login_required
@permission_required
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
@permission_required
def delete_sensordata_file(filename):
    DELETE_SENSORDATA_FILE(filename)
    return redirect(url_for('dashboard_sensordata_jobs'))


""" ##################### """
""" sensordata statistics """
""" ##################### """

dropdown_list_dates_temp = ""

@app.route('/dashboard/sensordata/statistics', methods=['GET', 'POST'])
@login_required
@permission_required
def dashboard_sensordata_statistics():
    global dropdown_list_dates_temp

    error_message = ""
    devices = ""
    sensors = ""
    date    = ""
    date_min = ""
    date_max = ""
    dropdown_list_dates = dropdown_list_dates_temp
    data_file_1 = ""
    data_file_2 = ""
    data_file_3 = ""
    graph = False

    if request.method == 'POST':

        # get data
        if request.form.get("load_data") is not None: 
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

            import datetime as dt

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
                
                # get all dates
                list_dates = []
                
                for date in pd.to_datetime(df['Timestamp']).dt.date.unique().tolist():
                    
                    date_temp = ""
                    date_temp = date_temp + str(date.year) + "-" 
                    
                    if len(str(date.month)) == 1:
                        date_temp = date_temp + "0" + str(date.month) + "-" 
                    else:
                        date_temp = date_temp + str(date.month) + "-" 
                    
                    if len(str(date.day)) == 1:
                        date_temp = date_temp + "0" + str(date.day)
                    else:
                        date_temp = date_temp + str(date.day)
                           
                    list_dates.append(date_temp)     
                    
                dropdown_list_dates      = list_dates
                date_min                 = list_dates[0]
                date_max                 = list_dates[-1]
                dropdown_list_dates_temp = list_dates   

            except Exception as e:
                error_message = "Fehler beim Öffnen der Datein >>> " + str(e)
                

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
           
                    
            try:
                devices = request.form.get("set_devices")
                sensors = request.form.get("set_sensors")  

                selected_devices = devices.replace(" ", "")
                selected_devices = selected_devices.split(",")
                selected_sensors = sensors.replace(" ", "")
                selected_sensors = selected_sensors.split(",")
            
                # complete list
                df_devices = df.loc[df['Device'].isin(selected_devices)]

                # selected divices
                df_sensors = df_devices.loc[df['Sensor'].isin(selected_sensors)]

                # selected date
                date_min = request.form.get("set_date_min")
                date_max = request.form.get("set_date_max")

                if date_min != None and date_min != "" and date_max != None and date_max != "":

                    if dropdown_list_dates_temp.index(date_min) >= dropdown_list_dates_temp.index(date_max):
                        error_message = ("Ungültiger Zeitraum")

                    else:
                        minimum_from_gui = date_min + " 00:00:00"
                        maximum_from_gui = date_max + " 00:00:00"
                        df_sensors_filtered_min = df_sensors[df_sensors['Timestamp']>=minimum_from_gui]
                        df_sensors_filtered_max = df_sensors[df_sensors['Timestamp']<=maximum_from_gui]

                        df_sensors = pd.merge(df_sensors_filtered_min, df_sensors_filtered_max, how='inner')


                # set datetime as index and remove former row datetime
                df_sensors['date'] = pd.to_datetime(df_sensors['Timestamp'], format='%Y-%m-%d %H:%M:%S', utc=True).values
                    
                df_sensors = df_sensors.set_index('date')
                df_sensors = df_sensors.drop(columns=['Timestamp'])
                
                graph  = BUILD_GRAPH(df_sensors)

            except:
                error_message = "Daten konnten nicht verarbeitet werden"
                     

    dropdown_list_files = GET_SENSORDATA_FILES()

    return render_template('dashboard_sensordata_statistics.html', 
                            error_message=error_message,
                            dropdown_list_files=dropdown_list_files,
                            devices=devices,
                            sensors=sensors,
                            date_min=date_min,
                            date_max=date_max,
                            dropdown_list_dates=dropdown_list_dates,                        
                            data_file_1=data_file_1,
                            data_file_2=data_file_2,
                            data_file_3=data_file_3,
                            graph=graph,
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system,                      
                            )
