from flask import render_template, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from functools import wraps
import os
import datetime

from app import app
from app.components.led_control import *
from app.database.database import *
from app.components.tasks import UPDATE_MQTT_DEVICES
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


""" ############# """
""" mqtt settings """
""" ############# """

@app.route('/dashboard/settings/mqtt', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_mqtt():   
    error_message = ""
    mqtt_device_channel_path = ""
    mqtt_device_name = ""   
    check_value_mqtt   = ["", ""]

    if request.method == "POST":     
        # change mqtt settings   
        if request.form.get("radio_mqtt") is not None:
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

        if request.method == 'POST':
            if request.form.get("add_mqtt_device") is not None: 
                # add mqtt device
                if request.form.get("set_mqtt_device_name") is "":
                    error_message = "Kein Name angegeben"   
                    mqtt_device_channel_path = request.form.get("set_mqtt_device_channel_path")    
                elif request.form.get("set_mqtt_device_channel_path") is "":
                    error_message = "Kein Kanal angegeben"    
                    mqtt_device_name = request.form.get("set_mqtt_device_name") 
                else:
                    mqtt_device_name = request.form.get("set_mqtt_device_name") 
                    mqtt_device_channel_path = request.form.get("set_mqtt_device_channel_path") 
                    
                    if mqtt_device_name is not None or mqtt_device_channel_path is not None:
                        error_message = ADD_MQTT_DEVICE(mqtt_device_name, mqtt_device_channel_path)                         
                        if error_message == "":
                            time.sleep(1)
                            try:
                                UPDATE_MQTT_DEVICES(GET_ALL_MQTT_DEVICES())
                            except Exception as e:
                                error_message = "Fehler in MQTT: " + str(e)
                                WRITE_LOGFILE_SYSTEM("ERROR", "MQTT: " + str(e))                                 
                            time.sleep(2)
                            mqtt_device_channel_path = ""
                            mqtt_device_name = ""                       

        if request.method == 'POST':
            # reset logfile
            if request.form.get("reset_logfile") is not None: 
                RESET_LOGFILE("log_mqtt")   
            # update mqtt devices
            if request.form.get("update_mqtt_devices") is not None:         
                try:
                    UPDATE_MQTT_DEVICES(GET_ALL_MQTT_DEVICES())
                except Exception as e:
                    error_message = "Fehler in MQTT: " + str(e)
                    WRITE_LOGFILE_SYSTEM("ERROR", "MQTT: " + str(e)) 
                time.sleep(2)

    mqtt_device_list = GET_ALL_MQTT_DEVICES()
    
    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 

    return render_template('dashboard_settings_mqtt.html',                    
                            error_message=error_message,
                            mqtt_device_channel_path=mqtt_device_channel_path,
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
    check_value_zigbee = ["", ""]

    if request.method == "POST":     
        # change mqtt settings   
        if request.form.get("radio_zigbee") is not None:
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

    return render_template('dashboard_settings_zigbee.html',
                            error_message=error_message,
                            check_value_zigbee=check_value_zigbee,                            
                            active02="active",
                            )


""" ################ """
""" snowboy settings """
""" ################ """

@app.route('/dashboard/settings/snowboy', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_snowboy():
    error_message = ""
    error_message_table = ""
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
                error_message = "Fehler in SnowBoy: " + str(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Snowboy: " + str(e)) 

        if request.method == 'POST':
            if request.form.get("change_settings") is not None: 
                # change sensitivity
                sensitivity = request.form.get("set_sensitivity") 
                if sensitivity is not None:
                    SET_SNOWBOY_SENSITIVITY(sensitivity)    

            if request.form.get("add_task") is not None:
                # add new task
                if request.form.get("set_name") == "":
                    error_message_table = "Kein Name angegeben"
                    set_task = request.form.get("set_task")
                elif request.form.get("set_task") == "":
                    error_message_table = "Keine Aufgabe angegeben"  
                    set_name = request.form.get("set_name")  
                else:         
                    name   = request.form.get("set_name")
                    task   = request.form.get("set_task")
                    error_message = ADD_SNOWBOY_TASK(name, task)
                    
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
    
    error_message_hotword = CHECK_HOTWORD_FILE_EXIST(GET_ALL_SNOWBOY_TASKS())

    return render_template('dashboard_settings_snowboy.html',
                            sensitivity=sensitivity,
                            error_message=error_message,    
                            error_message_table=error_message_table,             
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


""" ################### """
""" hue bridge settings """
""" ################### """

@app.route('/dashboard/settings/hue_bridge/', methods=['GET'])
@login_required
@superuser_required
def dashboard_settings_hue_bridge():
    led_update = "" 
    error_message_hue_bridge = ""
    hue_bridge_ip = ""
    led_list = ""
    check_value_hue_bridge = ["", ""]

    if request.method == "GET":     
        # change hue settings   
        if request.args.get("radio_hue_bridge") is not None:
            setting_hue_bridge = str(request.args.get("radio_hue_bridge"))
            SET_SETTING_VALUE("hue_bridge", setting_hue_bridge)

    # change radio check  
    hue_bridge_setting = GET_SETTING_VALUE("hue_bridge")     
    if hue_bridge_setting == "True":
        check_value_hue_bridge[0] = "checked = 'on'"
        check_value_hue_bridge[1] = ""
    else:
        check_value_hue_bridge[0] = ""
        check_value_hue_bridge[1] = "checked = 'on'"

    if hue_bridge_setting == "True":
        if request.method == "GET": 
            # change HUE ip
            hue_bridge_ip = request.args.get("hue_bridge_ip") 
            if hue_bridge_ip is not None:
                SET_HUE_BRIDGE_IP(hue_bridge_ip)
            # update_led_entries
            update_led_entries = request.args.get("update_led_entries") 
            if update_led_entries is not None:           
                UPDATE_LED(GET_LED_NAMES_HUE())    

        led_list = GET_ALL_LEDS()
        hue_bridge_ip = GET_HUE_BRIDGE_IP()  
        error_message_hue_bridge = TEST_HUE_BRIDGE()

    return render_template('dashboard_settings_hue_bridge.html',
                            hue_bridge_ip=hue_bridge_ip,
                            led_list=led_list,
                            error_message_hue_bridge=error_message_hue_bridge,
                            hue_bridge_setting=hue_bridge_setting,
                            check_value_hue_bridge=check_value_hue_bridge,
                            )
    

# remove led
@app.route('/dashboard/settings/hue_bridge/delete/<int:id>')
@login_required
@superuser_required
def remove_hue_bridge_led(id):
    remove_message_led = REMOVE_LED(id)
    return redirect(url_for('dashboard_settings_hue_bridge'))
    

""" ############# """
""" user settings """
""" ############# """

# dashboard user management
@app.route('/dashboard/settings/user/', methods=['GET'])
@login_required
@superuser_required
def dashboard_settings_user():
    user_list = GET_ALL_USERS()
    return render_template('dashboard_settings_user.html',
                            name=current_user.username,
                            user_list=user_list,
                            active04="active",
                            )


# activate user
@app.route('/dashboard/settings/user/role/<int:id>')
@login_required
@superuser_required
def activate_user(id):
    ACTIVATE_USER(id)
    return redirect(url_for('dashboard_settings_user'))


# delete user
@app.route('/dashboard/settings/user/delete/<int:id>')
@login_required
@superuser_required
def delete_user(id):
    DELETE_USER(id)
    return redirect(url_for('dashboard_settings_user'))


""" ############### """
""" system settings """
""" ############### """

# dashboard system settings
@app.route('/dashboard/settings/system/', methods=['GET', 'POST'])
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
                            active05="active",
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

# dashboard system settings
@app.route('/dashboard/settings/system_log/', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_system_log():
    error_message = ""

    if request.method == 'POST':
        if request.form.get("reset_logfile") is not None: 
            RESET_LOGFILE("log_system")   
            
    if GET_LOGFILE_SYSTEM() is not None:
        data_log_system = GET_LOGFILE_SYSTEM()
    else:
        data_log_system = ""

    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 

    return render_template('dashboard_settings_system_log.html',
                            error_message=error_message,
                            timestamp=timestamp,
                            data_log_system=data_log_system,
                            active06="active",
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
