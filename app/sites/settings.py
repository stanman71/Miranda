from flask import render_template, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from functools import wraps
import os
import datetime
import json

from app import app
from app.components.led_control import *
from app.database.database import *
from app.components.tasks import UPDATE_MQTT_DEVICES, CHECK_MQTT
from app.components.file_management import *
from app.components.email import SEND_EMAIL
from app.components.mqtt import *
from app.components.checks import CHECK_TASKS


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


""" ############# """
""" mqtt settings """
""" ############# """

@app.route('/dashboard/settings/mqtt', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_mqtt():   
    error_message = ""
    error_message_mqtt = ""
    error_message_table = ""
    mqtt_device_name = ""   
    check_value_mqtt   = ["", ""]

    if GET_ERROR_LIST() is not "":
        error_message_table = GET_ERROR_LIST()
        SET_ERROR_LIST("")

    if request.method == "POST":     
        # change mqtt settings   
        if request.form.get("set_setting_mqtt") is not None:
            setting_mqtt = str(request.form.get("radio_mqtt"))
            SET_SETTING_VALUE("mqtt", setting_mqtt)

    # change radio check  
    mqtt_setting = GET_SETTING_VALUE("mqtt")    
    if mqtt_setting == "True":
        check_value_mqtt[0] = "checked = 'on'"
        check_value_mqtt[1] = ""
    else:
        check_value_mqtt[0] = ""
        check_value_mqtt[1] = "checked = 'on'"

    if mqtt_setting == "True":

        # check mqtt
        try:
            CHECK_MQTT()
        except Exception as e:
            error_message_mqtt = "Fehler in MQTT: " + str(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "MQTT >>> " + str(e)) 

        # change settings
        if request.form.get("change_settings") != None:    
            for i in range (1,25):
                if request.form.get("set_name_" + str(i)) != "" and request.form.get("set_name_" + str(i)) != None:
                    # rename devices
                    new_name = request.form.get("set_name_" + str(i)) 
                    SET_MQTT_DEVICE_MQTT(i, new_name)
 
        # update device list
        if request.form.get("update_mqtt_devices") != None:
            UPDATE_MQTT_DEVICES("mqtt")
            
        # reset logfile
        if request.form.get("reset_logfile") != None: 
            print("OK")
            RESET_LOGFILE("log_mqtt")   
            

    mqtt_device_list = GET_ALL_MQTT_DEVICES("mqtt")
    
    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 

    return render_template('dashboard_settings_mqtt.html',                    
                            error_message=error_message,
                            error_message_mqtt=error_message_mqtt,
                            error_message_table=error_message_table,
                            mqtt_device_name=mqtt_device_name,
                            mqtt_setting=mqtt_setting,
                            check_value_mqtt=check_value_mqtt,
                            mqtt_device_list=mqtt_device_list,
                            active01="active",
                            timestamp=timestamp,
                            )
     
# remove mqtt device
@app.route('/dashboard/settings/mqtt/delete/<int:id>')
@login_required
@superuser_required
def remove_mqtt_device(id):
    DELETE_MQTT_DEVICE(id)
    return redirect(url_for('dashboard_settings_mqtt'))
     
     
# download mqtt logfile
@app.route('/dashboard/settings/mqtt/download/<path:filepath>')
@login_required
@superuser_required
def download_mqtt_logfile(filepath): 
    try:
        path = GET_PATH() + "/logs/"     
        WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /logs/" + filepath + " >>> downloaded")
        return send_from_directory(path, filepath)
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /logs/" + filepath + " >>> " + str(e))
             

""" ############### """
""" zigbee settings """
""" ############### """

@app.route('/dashboard/settings/zigbee', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_zigbee():
    error_message = ""
    error_message_zigbee = ""
    error_message_table = ""
    check_value_zigbee = ["", ""]
    check_value_pairing = ["", ""]

    if request.method == "POST":     
        # change mqtt settings   
        if request.form.get("set_setting_zigbee") is not None:
            setting_zigbee = str(request.form.get("radio_zigbee"))
            SET_SETTING_VALUE("zigbee", setting_zigbee)

    # change radio check  
    zigbee_setting = GET_SETTING_VALUE("zigbee")    
    if zigbee_setting == "True":
        check_value_zigbee[0] = "checked = 'on'"
        check_value_zigbee[1] = ""
    else:
        check_value_zigbee[0] = ""
        check_value_zigbee[1] = "checked = 'on'"


    if zigbee_setting == "True":

        if GET_ERROR_LIST() is not "":
            error_message_table = GET_ERROR_LIST()
            SET_ERROR_LIST("")
        
        error_message_zigbee = MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/", "")
        
        if request.method == 'POST':

            # change settings
            if request.form.get("change_settings") != None:
                for i in range (1,25):
                    # set name + inputs
                    if (request.form.get("set_name_" + str(i)) != "" and
                        request.form.get("set_name_" + str(i)) != None):
                            
                        new_name = request.form.get("set_name_" + str(i))
                        old_name = GET_MQTT_DEVICE_NAME(i) 
                        
                        if new_name != old_name:
                            MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/rename", 
                                         '{"old": "' + old_name + '", "new": "' + new_name + '"}')   

                        inputs = request.form.get("set_inputs_" + str(i))         
                        SET_MQTT_DEVICE_ZigBee(i, new_name, inputs)
                   

            # update device list
            if request.form.get("update_zigbee_devices") is not None:
                UPDATE_MQTT_DEVICES("zigbee")

                
            # change pairing setting
            if request.form.get("set_pairing") is not None: 
                setting_pairing = str(request.form.get("radio_pairing"))
                SET_ZIGBEE_PAIRING(setting_pairing)

            # reset logfile
            if request.form.get("reset_logfile") is not None: 
                RESET_LOGFILE("log_zigbee")
     
        # set pairing checkbox  
        pairing_setting = GET_ZIGBEE_PAIRING()    
        if pairing_setting == "True":
            check_value_pairing[0] = "checked = 'on'"
            check_value_pairing[1] = ""        
            #MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/permit_join", "true")  
        else:
            check_value_pairing[0] = ""
            check_value_pairing[1] = "checked = 'on'"        
            #MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/permit_join", "false")

        if READ_LOGFILE_MQTT("zigbee", "") != "Message nicht gefunden":
            error_message_zigbee = READ_LOGFILE_MQTT("zigbee", "") 
            WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT >>> No connection")

    zigbee_device_list = GET_ALL_MQTT_DEVICES("zigbee")

    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return render_template('dashboard_settings_zigbee.html',
                            error_message=error_message,
                            error_message_zigbee=error_message_zigbee,
                            error_message_table=error_message_table,
                            check_value_zigbee=check_value_zigbee,  
                            check_value_pairing=check_value_pairing,
                            zigbee_device_list=zigbee_device_list, 
                            zigbee_setting=zigbee_setting,                  
                            active02="active",
                            timestamp=timestamp,
                            )


# remove zigbee device
@app.route('/dashboard/settings/zigbee/delete/<int:id>')
@login_required
@superuser_required
def remove_zigbee_device(id):
    MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/remove", GET_MQTT_DEVICE_NAME(id)) 
    DELETE_MQTT_DEVICE(id)
    return redirect(url_for('dashboard_settings_zigbee'))


# download zigbee logfile
@app.route('/dashboard/settings/zigbee/download/<path:filepath>')
@login_required
@superuser_required
def download_zigbee_logfile(filepath): 
    try:
        path = GET_PATH() + "/logs/"     
        WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /logs/" + filepath + " >>> downloaded")
        return send_from_directory(path, filepath)
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /logs/" + filepath + " >>> " + str(e))             


""" ################ """
""" snowboy settings """
""" ################ """

@app.route('/dashboard/settings/snowboy', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_snowboy():
    error_message = ""
    error_message_snowboy = ""
    error_message_form = ""
    error_message_tasks = ""
    error_message_fileupload = ""
    error_message_hotword = ""
    sensitivity = ""
    check_value_snowboy = ["", ""]
    set_name = ""
    set_task = ""

    if request.method == "POST":     
        # change snowboy settings   
        if request.form.get("radio_snowboy") is not None:
            setting_snowboy = str(request.form.get("radio_snowboy"))
            SET_SETTING_VALUE("snowboy", setting_snowboy) 

    # change radio check    
    if GET_SETTING_VALUE("snowboy") == "True":
        check_value_snowboy[0] = "checked = 'on'"
        check_value_snowboy[1] = ""
    else:
        check_value_snowboy[0] = ""
        check_value_snowboy[1] = "checked = 'on'"

    if GET_SETTING_VALUE("snowboy") == "True":

        # check snowboy
        def START_SNOWBOY():
            from app.snowboy.snowboy import SNOWBOY_START
            SNOWBOY_START()
          
        try:
            START_SNOWBOY()
        except Exception as e:  
            if "signal only works in main thread" not in str(e):      
                error_message_snowboy = "Fehler in SnowBoy: " + str(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Snowboy >>> " + str(e)) 
                
        if request.method == 'POST':
            # change sensitivity
            if request.form.get("change_settings") is not None: 

                sensitivity = request.form.get("set_sensitivity") 
                if sensitivity is not None:
                    SET_SNOWBOY_SENSITIVITY(sensitivity)    

            # add new task
            if request.form.get("add_task") is not None:

                if request.form.get("set_name") == "":
                    error_message = "Kein Name angegeben"
                    set_task = request.form.get("set_task")
                elif request.form.get("set_task") == "":
                    error_message = "Keine Aufgabe angegeben"  
                    set_name = request.form.get("set_name")  
                else:         
                    name   = request.form.get("set_name")
                    task   = request.form.get("set_task")
                    error_message = ADD_SNOWBOY_TASK(name, task)
                    

            # change settings
            if request.form.get("change_settings") != None: 
                for i in range (1,25):

                    if request.form.get("set_name_" + str(i)) != None:  
                        
                        # check name
                        if (request.form.get("set_name_" + str(i)) != "" and 
                            GET_SNOWBOY_TASK_BY_NAME(request.form.get("set_name_" + str(i))) == None):
                            name = request.form.get("set_name_" + str(i)) 
                            
                        elif request.form.get("set_name_" + str(i)) == GET_SNOWBOY_TASK_BY_ID(i).name:
                            name = GET_SNOWBOY_TASK_BY_ID(i).name                        
                            
                        else:
                            name = GET_SNOWBOY_TASK_BY_ID(i).name 
                            error_message_form = "Ungültige Eingabe (leeres Feld / Name schon vergeben"                          
                        
                        # check task
                        if request.form.get("set_task_" + str(i)) != "":
                            task = request.form.get("set_task_" + str(i)) 
                        
                        else:
                            task = GET_SNOWBOY_TASK_BY_ID(i).task 
                            error_message_form = "Ungültige Eingabe (leeres Feld / Name schon vergeben"   
                                            
            
                        SET_SNOWBOY_TASK(i, name, task)
                    
                    
            if request.form.get("file_upload") is not None:
                # file upload
                if 'file' not in request.files:
                    error_message_fileupload = "Keine Datei angegeben"
                else:
                    file = request.files['file']
                    error_message_fileupload = UPLOAD_HOTWORD_FILE(file)

    snowboy_setting = GET_SETTING_VALUE("snowboy")
    sensitivity = GET_SNOWBOY_SENSITIVITY()
    snowboy_list = GET_ALL_SNOWBOY_TASKS()
    file_list = GET_ALL_HOTWORD_FILES()
    
    error_message_tasks   = CHECK_TASKS(GET_ALL_SNOWBOY_TASKS(), "snowboy")
    error_message_hotword = CHECK_HOTWORD_FILE_EXIST(GET_ALL_SNOWBOY_TASKS())

    return render_template('dashboard_settings_snowboy.html',
                            sensitivity=sensitivity,
                            error_message=error_message,    
                            error_message_snowboy=error_message_snowboy,   
                            error_message_form=error_message_form,  
                            error_message_tasks=error_message_tasks,        
                            error_message_fileupload=error_message_fileupload,
                            error_message_hotword=error_message_hotword,
                            snowboy_setting=snowboy_setting,
                            check_value_snowboy=check_value_snowboy,
                            snowboy_list=snowboy_list,
                            file_list=file_list,
                            set_name=set_name,
                            set_task=set_task,
                            active03="active",
                            )


# delete snowboy tasks
@app.route('/dashboard/settings/snowboy/delete/task/<int:id>')
@login_required
@superuser_required
def delete_snowboy_task(id):
    DELETE_SNOWBOY_TASK(id)
    return redirect(url_for('dashboard_settings_snowboy'))


# download hotword file
@app.route('/dashboard/settings/snowboy/download/hotword/<path:filepath>')
@login_required
@superuser_required
def download_hotword_file(filepath):
    if filepath is None:
        print(Error(400))     
    try:
        path = GET_PATH() + "/app/snowboy/resources/"     
        WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /app/snowboy/resources/" + filepath + " >>> downloaded")
        return send_from_directory(path, filepath)
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /app/snowboy/resources/" + filepath + " >>> " + str(e)) 


# delete snowboy hotwords
@app.route('/dashboard/settings/snowboy/delete/hotword/<string:filename>')
@login_required
@superuser_required
def delete_snowboy_hotword(filename):
    DELETE_HOTWORD_FILE(filename)
    return redirect(url_for('dashboard_settings_snowboy'))


""" ############# """
""" user settings """
""" ############# """

# dashboard user management
@app.route('/dashboard/settings/user', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_user():
    error_message = ""
    error_message_form = ""

    if request.method == "POST":     
        # change user settings
        if request.form.get("change_user_settings") != None:
            for i in range (1,25): 
                
                if request.form.get("set_username_" + str(i)) != None:

                    # check name
                    if (request.form.get("set_username_" + str(i)) != "" and 
                        GET_USER_BY_NAME(request.form.get("set_username_" + str(i))) == None):
                        username = request.form.get("set_username_" + str(i)) 
                        
                    elif request.form.get("set_username_" + str(i)) == GET_USER_BY_ID(i).username:
                        username = GET_USER_BY_ID(i).username                        
                        
                    else:
                        username = GET_USER_BY_ID(i).username 
                        error_message_form = "Ungültige Eingabe (leeres Feld / Name schon vergeben"                          
                    
                    # check email
                    if (request.form.get("set_email_" + str(i)) != "" and 
                        GET_EMAIL(request.form.get("set_email_" + str(i))) == None):
                        email = request.form.get("set_email_" + str(i)) 
                    
                    elif request.form.get("set_email_" + str(i)) == GET_USER_BY_ID(i).email:
                        email = GET_USER_BY_ID(i).email                        
                    
                    else:
                        email = GET_USER_BY_ID(i).email 
                        error_message_form = "Ungültige Eingabe (leeres Feld / Name schon vergeben"   

                    # change user role
                    role = request.form.get("set_role_" + str(i))

                    # change email notification
                    if request.form.get("checkbox_info_" + str(i)):
                        email_notification_info = "checked"
                    else:
                        email_notification_info = ""
                    if request.form.get("checkbox_error_" + str(i)):
                        email_notification_error = "checked"
                    else:
                        email_notification_error = ""
                    if request.form.get("checkbox_camera_" + str(i)):
                        email_notification_camera = "checked"
                    else:
                        email_notification_camera = ""
           
                    SET_USER_SETTINGS(i, username, email, role, email_notification_info, email_notification_error, email_notification_camera)


    user_list = GET_ALL_USERS()
    dropdown_list_roles = ["guest", "user", "superuser"]

    return render_template('dashboard_settings_user.html',
                            error_message=error_message,
                            error_message_form=error_message_form,
                            user_list=user_list,  
                            dropdown_list_roles=dropdown_list_roles,             
                            active04="active",
                            )


# delete user
@app.route('/dashboard/settings/user/delete/<int:id>')
@login_required
@superuser_required
def delete_user(id):
    DELETE_USER(id)
    return redirect(url_for('dashboard_settings_user'))


""" ############# """
""" email settings """
""" ############# """

# dashboard email settings
@app.route('/dashboard/settings/email', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_email():
    error_message = ""
    error_message_test = ""
    message_test = ""

    if request.method == "POST":     
        # update email settings
        if request.form.get("change_email_settings") is not None:      
            set_mail_server_address = request.form.get("set_mail_server_address")
            set_mail_server_port    = request.form.get("set_mail_server_port")
            set_mail_encoding       = request.form.get("set_mail_encoding")
            set_mail_username       = request.form.get("set_mail_username")               
            set_mail_password       = request.form.get("set_mail_password")

            error_message = SET_EMAIL_SETTINGS(set_mail_server_address, 
                                                    set_mail_server_port, 
                                                    set_mail_encoding, 
                                                    set_mail_username, 
                                                    set_mail_password)

        # test email settings
        if request.form.get("test_email_config") is not None:
            error_message_test = SEND_EMAIL(GET_EMAIL_ADDRESS("test"), "TEST", "TEST")

    email_config = GET_EMAIL_CONFIG()[0]
    mail_encoding_list = ["TLS", "SSL"]
    
    # eMail-Muster
    # SEND_EMAIL(GET_EMAIL_ADDRESS("info"), "TEST", "Das ist eine eMail mit Anhang")

    return render_template('dashboard_settings_email.html',
                            error_message=error_message,
                            error_message_test=error_message_test,
                            email_config=email_config,
                            mail_encoding_list=mail_encoding_list,                          
                            active05="active",
                            )


""" ############### """
""" system settings """
""" ############### """

@app.route('/dashboard/settings/system', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_system():
    error_message = ""

    def GET_CPU_TEMPERATURE():
        res = os.popen('vcgencmd measure_temp').readline()
        return(res.replace("temp=","").replace("'C\n"," C"))

    if request.method == "POST":     
        # restart raspi 
        if request.form.get("restart") is not None:
            os.system("sudo shutdown -r now")
            sys.exit()
        # shutdown raspi 
        if request.form.get("shutdown") is not None:
            os.system("sudo shutdown -h now")
            sys.exit()
        # save database   
        if request.form.get("database_save") is not None:
            SAVE_DATABASE() 
 
    file_list = GET_BACKUP_FILES()
    cpu_temperature = GET_CPU_TEMPERATURE()

    return render_template('dashboard_settings_system.html',
                            error_message=error_message,
                            file_list=file_list,
                            cpu_temperature=cpu_temperature,                                                     
                            active06="active",
                            )


# restore database backup
@app.route('/dashboard/settings/system/restore/backup_database/<string:filename>')
@login_required
@superuser_required
def restore_database_backup(filename):
    RESTORE_DATABASE(filename)
    return redirect(url_for('dashboard_settings_system'))


# delete database backup
@app.route('/dashboard/settings/system/delete/backup_database/<string:filename>')
@login_required
@superuser_required
def delete_database_backup(filename):
    DELETE_DATABASE_BACKUP(filename)
    return redirect(url_for('dashboard_settings_system'))


""" ########### """
""" system logs """
""" ########### """

@app.route('/dashboard/settings/system_log', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_system_log():
    error_message = ""

    if request.method == 'POST':
        if request.form.get("reset_logfile") is not None: 
            RESET_LOGFILE("log_system")   
            
    if GET_LOGFILE_SYSTEM(30) is not None:
        data_log_system = GET_LOGFILE_SYSTEM(30)
    else:
        data_log_system = ""

    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 

    return render_template('dashboard_settings_system_log.html',
                            error_message=error_message,
                            timestamp=timestamp,
                            data_log_system=data_log_system,                                                       
                            active07="active",
                            )


# download system logfile
@app.route('/dashboard/settings/system_log/download/<path:filepath>')
@login_required
@superuser_required
def download_system_logfile(filepath): 
    try:
        path = GET_PATH() + "/logs/"    
        WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /logs/" + filepath + " >>> downloaded")
        return send_from_directory(path, filepath)
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /logs/" + filepath + " >>> " + str(e))
