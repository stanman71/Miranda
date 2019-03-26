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

    if request.method == "GET":     
        # change mqtt settings   
        if request.args.get("radio_mqtt") is not None:
            setting_mqtt = str(request.args.get("radio_mqtt"))
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

        try:
            UPDATE_MQTT_DEVICES(GET_ALL_MQTT_DEVICES())
        except Exception as e:
            error_message = "Fehler in MQTT: " + str(e)

        if request.method == "GET": 
            # add mqtt device
            if request.args.get("set_mqtt_device_name") is "":
                error_message = "Kein Name angegeben"   
                mqtt_device_channel_path = request.args.get("set_mqtt_device_channel_path")    
            elif request.args.get("set_mqtt_device_channel_path") is "":
                error_message = "Kein Kanal angegeben"    
                mqtt_device_name = request.args.get("set_mqtt_device_name") 
            else:
                mqtt_device_name = request.args.get("set_mqtt_device_name") 
                mqtt_device_channel_path = request.args.get("set_mqtt_device_channel_path") 
                
                if mqtt_device_name is not None or mqtt_device_channel_path is not None:
                    error_message = ADD_MQTT_DEVICE(mqtt_device_name, mqtt_device_channel_path)
                    mqtt_device_channel_path = ""
                    mqtt_device_name = ""                       

        if request.method == 'POST':
            if request.form.get("update_mqtt_devices") is not None:         
                UPDATE_MQTT_DEVICES(GET_ALL_MQTT_DEVICES())  
                time.sleep(2)

    mqtt_device_list = GET_ALL_MQTT_DEVICES()

    return render_template('dashboard_settings_mqtt.html',                    
                            error_message=error_message,
                            mqtt_device_channel_path=mqtt_device_channel_path,
                            mqtt_device_name=mqtt_device_name,
                            mqtt_setting=mqtt_setting,
                            check_value_mqtt=check_value_mqtt,
                            mqtt_device_list=mqtt_device_list,
                            active01="active",
                            )
     
# remove mqtt device
@app.route('/dashboard/settings/mqtt/delete/<int:id>')
@login_required
@superuser_required
def remove_mqtt_device(id):
    DELETE_MQTT_DEVICE(id)
    return redirect(url_for('dashboard_settings_mqtt'))
     

""" ############### """
""" zigbee settings """
""" ############### """

@app.route('/dashboard/settings/zigbee', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_zigbee():
    error_message = ""
    check_value_zigbee = ["", ""]

    if request.method == "GET":     
        # change mqtt settings   
        if request.args.get("radio_zigbee") is not None:
            setting_zigbee = str(request.args.get("radio_zigbee"))
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


""" ########## """
""" sensordata """
""" ########## """

@app.route('/dashboard/settings/sensordata', methods=['GET'])
@login_required
@superuser_required
def dashboard_settings_sensordata():
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

    return render_template('dashboard_settings_sensordata.html',
                            name=name,
                            filename=filename,
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            error_message=error_message,
                            error_message_file=error_message_file,
                            sensordata_list=sensordata_list,
                            file_list=file_list,
                            active03="active",
                            )


# remove sensordata
@app.route('/dashboard/settings/sensordata/delete/<int:id>')
@login_required
@superuser_required
def remove_sensordata(id):
    DELETE_SENSORDATA_JOB(id)
    return redirect(url_for('dashboard_settings_sensordata'))


# delete sensordata file
@app.route('/dashboard/settings/sensordata/delete/<string:filename>')
@login_required
@superuser_required
def delete_sensordata_file(filename):
    DELETE_SENSORDATA_FILE(filename)
    return redirect(url_for('dashboard_settings_sensordata'))


""" ################ """
""" snowboy settings """
""" ################ """

@app.route('/dashboard/settings/snowboy', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_snowboy():
    error_message = ""
    error_message_fileupload = ""
    sensitivity = ""
    check_value_snowboy = ["", ""]
    set_name = ""
    set_task = ""

    if request.method == "GET":     
        # change snowboy settings   
        if request.args.get("radio_snowboy") is not None:
            setting_snowboy = str(request.args.get("radio_snowboy"))
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

        # change sensitivity
        if request.method == "GET":
            sensitivity = request.args.get("set_sensitivity") 
            if sensitivity is not None:
                SET_SNOWBOY_SENSITIVITY(sensitivity)    

        # add new task
        if request.args.get("set_name") is not None:

            # controll name and task input
            if request.args.get("set_name") == "":
                error_message_table = "Kein Name angegeben"
                set_task = request.args.get("set_task")

            elif request.args.get("set_task") == "":
                error_message_table = "Keine Aufgabe angegeben"  
                set_name = request.args.get("set_name")  
                          
            else:         
                # get database informations
                name   = request.args.get("set_name")
                task   = request.args.get("set_task")
                error_message = ADD_SNOWBOY_TASK(name, task)

        # file upload
        if request.method == 'POST':
            if 'file' not in request.files:
                error_message_fileupload = "Keine Datei angegeben"
            else:
                file = request.files['file']
                error_message_fileupload = UPLOAD_HOTWORD_FILE(file)

    snowboy_setting = GET_SETTING_VALUE("snowboy")
    sensitivity = GET_SNOWBOY_SENSITIVITY()
    snowboy_list = GET_ALL_SNOWBOY_TASKS()
    file_list = GET_ALL_HOTWORD_FILES()

    return render_template('dashboard_settings_snowboy.html',
                            sensitivity=sensitivity,
                            error_message=error_message,                  
                            error_message_fileupload=error_message_fileupload,
                            snowboy_setting=snowboy_setting,
                            check_value_snowboy=check_value_snowboy,
                            snowboy_list=snowboy_list,
                            file_list=file_list,
                            set_name=set_name,
                            set_task=set_task,
                            active04="active",
                            )


# delete snowboy tasks
@app.route('/dashboard/settings/snowboy/delete/task/<int:id>')
@login_required
@superuser_required
def delete_snowboy_task(id):
    DELETE_SNOWBOY_TASK(id)
    return redirect(url_for('dashboard_settings_snowboy'))


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
                            active05="active",
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
@app.route('/dashboard/settings/system/', methods=['GET'])
@login_required
@superuser_required
def dashboard_settings_system():
    error_message = ""
                              
    def GET_CPU_TEMPERATURE():
        res = os.popen('vcgencmd measure_temp').readline()
        return(res.replace("temp=","").replace("'C\n"," C"))

    if request.method == "GET":     
        # restart raspi 
        if request.args.get("restart") is not None:
            os.system("sudo shutdown -r now")
            sys.exit()
        # shutdown raspi 
        if request.args.get("shutdown") is not None:
            os.system("sudo shutdown -h now")
            sys.exit()
        # save database   
        if request.args.get("database_save") is not None:
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
