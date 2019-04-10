from flask import render_template, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from flask_apscheduler import APScheduler
from functools import wraps
import datetime

from app import app
from app.database.database import *
from app.components.file_management import *

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


""" ########## """
""" sensordata """
""" ########## """

@app.route('/dashboard/sensordata', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_sensordata():
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
    
    sensordata_list = GET_ALL_SENSORDATA_JOBS()
    file_list = GET_SENSORDATA_FILES()

    if set_mqtt_device_id != "":
        set_mqtt_device_name = GET_MQTT_DEVICE_NAME(int(set_mqtt_device_id))

    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 

    return render_template('dashboard_sensordata.html',
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
                            sensordata_list=sensordata_list,
                            file_list=file_list,     
                            timestamp=timestamp, 
                            role=current_user.role,                      
                            )


# remove sensordata job
@app.route('/dashboard/sensordata/delete/job/<int:id>')
@login_required
@user_required
def remove_sensordata_job(id):
    DELETE_SENSORDATA_JOB(id)  
    return redirect(url_for('dashboard_sensordata'))


# download sensordata file
@app.route('/dashboard/sensordata/download/file/<path:filepath>')
@login_required
@user_required
def download_sensordata_file(filepath):
    if filepath is None:
        print(Error(400))     
    try:
        path = GET_PATH() + "/csv/"     
        WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /csv/" + filepath + " >>> downloaded")
        return send_from_directory(path, filepath)
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /csv/" + filepath + " >>> " + str(e)) 


# delete sensordata file
@app.route('/dashboard/sensordata/delete/file/<string:filename>')
@login_required
@user_required
def delete_sensordata_file(filename):
    DELETE_SENSORDATA_FILE(filename)
    return redirect(url_for('dashboard_sensordata'))
