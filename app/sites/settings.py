from flask import render_template, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from functools import wraps
import os
import datetime
import json
import sys

from app import app
from app.components.control_led import *
from app.database.database import *
from app.components.file_management import *
from app.components.email import SEND_EMAIL
from app.components.mqtt_functions import *
from app.components.checks import *


# create role "superuser"
def superuser_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "superuser":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
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
    error_message_change_settings = ""
    mqtt_device_name = ""   
    check_value_mqtt   = ["", ""]

    if GET_ERROR_LIST() is not "":
        error_message_change_settings = GET_ERROR_LIST()
        SET_ERROR_LIST("")

    if request.method == "POST":     
        # change mqtt settings   
        if request.form.get("set_setting_mqtt") is not None:
            setting_mqtt = str(request.form.get("radio_mqtt"))
            SET_GLOBAL_SETTING_VALUE("mqtt", setting_mqtt)

    # change radio check  
    mqtt_setting = GET_GLOBAL_SETTING_VALUE("mqtt")    
    if mqtt_setting == "True":
        check_value_mqtt[0] = "checked = 'on'"
        check_value_mqtt[1] = ""
    else:
        check_value_mqtt[0] = ""
        check_value_mqtt[1] = "checked = 'on'"

    if mqtt_setting == "True":

        # check mqtt
        try:
            MQTT_CHECK()
        except Exception as e:
            error_message_mqtt = "Fehler in MQTT: " + str(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | " + str(e)) 

        # change settings
        if request.form.get("change_settings") != None:    
            for i in range (1,26):
                if request.form.get("set_name_" + str(i)) != "" and request.form.get("set_name_" + str(i)) != None:
                                
                    # rename devices                   
                    new_name = request.form.get("set_name_" + str(i))
                    old_name = GET_MQTT_DEVICE_BY_ID(i).name

                    if new_name != old_name:          
                        if not GET_MQTT_DEVICE_BY_NAME(new_name):  
                            ieeeAddr = GET_MQTT_DEVICE_BY_ID(i).ieeeAddr                  
                            SET_MQTT_DEVICE_NAME(ieeeAddr, new_name)                         
                        else: 
                            error_message_change_settings = "Name bereits vergeben >>> " + new_name

        # update device list
        if request.form.get("mqtt_update_devices") != None:
            error_message_change_settings = MQTT_UPDATE_DEVICES("mqtt")
            
        # reset logfile
        if request.form.get("reset_logfile") != None: 
            print("OK")
            RESET_LOGFILE("log_mqtt")   
            

    mqtt_device_list = GET_ALL_MQTT_DEVICES("mqtt")
    
    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 

    return render_template('dashboard_settings_mqtt.html',                    
                            error_message=error_message,
                            error_message_mqtt=error_message_mqtt,
                            error_message_change_settings=error_message_change_settings,
                            mqtt_device_name=mqtt_device_name,
                            mqtt_setting=mqtt_setting,
                            check_value_mqtt=check_value_mqtt,
                            mqtt_device_list=mqtt_device_list,
                            active01="active",
                            timestamp=timestamp,
                            )
     

# change mqtt device position 
@app.route('/dashboard/settings/mqtt/position/<string:direction>/<string:device_type>/<int:id>')
@login_required
@superuser_required
def change_mqtt_device_position(id, direction, device_type):
    CHANGE_MQTT_DEVICE_POSITION(id, device_type, direction)
    return redirect(url_for('dashboard_settings_mqtt'))


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
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /logs/" + filepath + " | downloaded")
        return send_from_directory(path, filepath)
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/" + filepath + " | " + str(e))
             

""" #################### """
""" zigbee2mqtt settings """
""" #################### """

@app.route('/dashboard/settings/zigbee2mqtt', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_zigbee2mqtt():
    error_message = ""
    error_message_zigbee2mqtt = ""
    error_message_change_settings = ""
    check_value_zigbee2mqtt = ["", ""]
    check_value_pairing = ["", ""]
    zigbee_topology_show = False

    if request.method == "POST":     
        # change mqtt settings   
        if request.form.get("set_setting_zigbee2mqtt") is not None:
            setting_zigbee2mqtt = str(request.form.get("radio_zigbee2mqtt"))
            SET_GLOBAL_SETTING_VALUE("zigbee2mqtt", setting_zigbee2mqtt)

    # change radio check  
    zigbee2mqtt_setting = GET_GLOBAL_SETTING_VALUE("zigbee2mqtt")    
    if zigbee2mqtt_setting == "True":
        check_value_zigbee2mqtt[0] = "checked = 'on'"
        check_value_zigbee2mqtt[1] = ""
    else:
        check_value_zigbee2mqtt[0] = ""
        check_value_zigbee2mqtt[1] = "checked = 'on'"


    if zigbee2mqtt_setting == "True":

        if GET_ERROR_LIST() is not "":
            error_message_change_settings = GET_ERROR_LIST()
            SET_ERROR_LIST("")
        
        error_message_zigbee2mqtt = MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/", "")
        
        if request.method == 'POST':

            # change name
            if request.form.get("change_settings") != None:
                
                for i in range (1,26):

                    if (request.form.get("set_name_" + str(i)) != "" and request.form.get("set_name_" + str(i)) != None):
                            
                        new_name = request.form.get("set_name_" + str(i))
                        old_name = GET_MQTT_DEVICE_BY_ID(i).name 
                        
                        if new_name != old_name:
                        
                            # name already exist
                            if not GET_MQTT_DEVICE_BY_NAME(new_name):

                                # no connection to mqtt
                                if MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/rename", 
                                                '{"old": "' + old_name + '", "new": "' + new_name + '"}') != "Keine Verbindung zu MQTT":

                                    time.sleep(3)

                                    # error in zigbee2mqtt
                                    if MQTT_CHECK_NAME_CHANGED():       
                                        ieeeAddr = GET_MQTT_DEVICE_BY_ID(i).ieeeAddr                  
                                        SET_MQTT_DEVICE_NAME(ieeeAddr, new_name)  

                                    else:
                                        error_message_change_settings = "Name konnte in ZigBee2MQTT nicht verändert werden"
                                        MQTT_UPDATE_DEVICES("zigbee2mqtt")

                                else:
                                    error_message_change_settings = "Ohne eine Verbindung zu MQTT können die Namen der Geräte nicht verändert werden !"
                                
                            else:
                                error_message_change_settings = "Name bereits vergeben >>> " + new_name

            # update device list
            if request.form.get("update_zigbee2mqtt_devices") is not None:
                error_message_change_settings = MQTT_UPDATE_DEVICES("zigbee2mqtt")

            # request zigbee topology
            if request.form.get("request_zigbee_topology") is not None: 
                MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/networkmap", "graphviz")
                zigbee_topology_show = True
                time.sleep(1)

            # change pairing setting
            if request.form.get("set_pairing") is not None: 
                setting_pairing = str(request.form.get("radio_pairing"))
                SET_ZIGBEE2MQTT_PAIRING(setting_pairing)

            # reset logfile
            if request.form.get("reset_logfile") is not None: 
                RESET_LOGFILE("log_zigbee2mqtt")
     
        # set pairing checkbox  
        pairing_setting = GET_ZIGBEE2MQTT_PAIRING()    
        if pairing_setting == "True":
            check_value_pairing[0] = "checked = 'on'"
            check_value_pairing[1] = ""        
            MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/permit_join", "true")  
        else:
            check_value_pairing[0] = ""
            check_value_pairing[1] = "checked = 'on'"        
            MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/permit_join", "false")

        if READ_LOGFILE_MQTT("zigbee2mqtt", "",5) != "Message nicht gefunden":
            error_message_zigbee2mqtt = READ_LOGFILE_MQTT("zigbee2mqtt", "",5) 
            WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | No connection")

    zigbee2mqtt_device_list = GET_ALL_MQTT_DEVICES("zigbee2mqtt")

    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return render_template('dashboard_settings_zigbee2mqtt.html',
                            error_message=error_message,
                            error_message_zigbee2mqtt=error_message_zigbee2mqtt,
                            error_message_change_settings=error_message_change_settings,
                            check_value_zigbee2mqtt=check_value_zigbee2mqtt,  
                            check_value_pairing=check_value_pairing,
                            zigbee2mqtt_device_list=zigbee2mqtt_device_list, 
                            zigbee2mqtt_setting=zigbee2mqtt_setting, 
                            zigbee_topology_show=zigbee_topology_show,                 
                            active02="active",
                            timestamp=timestamp,
                            )


# change zigbee2mqtt device position 
@app.route('/dashboard/settings/zigbee2mqtt/position/<string:direction>/<string:device_type>/<int:id>')
@login_required
@superuser_required
def change_zigbee2mqtt_device_position(id, direction, device_type):
    CHANGE_MQTT_DEVICE_POSITION(id, device_type, direction)

    return redirect(url_for('dashboard_settings_zigbee2mqtt'))


# remove zigbee2mqtt device
@app.route('/dashboard/settings/zigbee2mqtt/delete/<int:id>')
@login_required
@superuser_required
def remove_zigbee2mqtt_device(id):
    MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/remove", GET_MQTT_DEVICE_BY_ID(id).name) 
    DELETE_MQTT_DEVICE(id)
    return redirect(url_for('dashboard_settings_zigbee2mqtt'))


# download zigbee2mqtt logfile
@app.route('/dashboard/settings/zigbee2mqtt/download/<path:filepath>')
@login_required
@superuser_required
def download_zigbee2mqtt_logfile(filepath): 
    try:
        path = GET_PATH() + "/logs/"     
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /logs/" + filepath + " | downloaded")
        return send_from_directory(path, filepath)
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/" + filepath + " | " + str(e))             


""" ############ """
"""  controller  """
""" ############ """

@app.route('/dashboard/settings/controller', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_controller():
    error_message_add_controller = ""
    error_message_controller_tasks = ""

    UPDATE_CONTROLLER_COMMANDS()

    for i in range (1,21):
        try:
            RESET_CONTROLLER_ERRORS(i)
        except:
            pass

    if request.method == "POST": 

        if request.form.get("add_controller") != None: 
            
            if request.form.get("set_mqtt_device_ieeeAddr") != None:
                mqtt_device_ieeeAddr         = request.form.get("set_mqtt_device_ieeeAddr")
                error_message_add_controller = ADD_CONTROLLER(mqtt_device_ieeeAddr)

            else:
                error_message_add_controller = "Keinen Controller angegeben"  
   
        if request.form.get("save_task_settings") != None: 

            for i in range (1,21):

                if request.form.get("set_task_1_" + str(i)) != None:

                    ### set tasks
                    if request.form.get("set_task_1_" + str(i)) != "":
                        task_1 = request.form.get("set_task_1_" + str(i))
                    else:
                        task_1 = "None"                   
                    if request.form.get("set_task_2_" + str(i)) != "":
                        task_2 = request.form.get("set_task_2_" + str(i))
                    else:
                        task_2 = "None"  
                    if request.form.get("set_task_3_" + str(i)) != "":
                        task_3 = request.form.get("set_task_3_" + str(i))
                    else:
                        task_3 = "None"  
                    if request.form.get("set_task_4_" + str(i)) != "":
                        task_4 = request.form.get("set_task_4_" + str(i))
                    else:
                        task_4 = "None"                   
                    if request.form.get("set_task_5_" + str(i)) != "":
                        task_5 = request.form.get("set_task_5_" + str(i))
                    else:
                        task_5 = "None"  
                    if request.form.get("set_task_6_" + str(i)) != "":
                        task_6 = request.form.get("set_task_6_" + str(i))
                    else:
                        task_6 = "None"  
                    if request.form.get("set_task_7_" + str(i)) != "":
                        task_7 = request.form.get("set_task_7_" + str(i))
                    else:
                        task_7 = "None"                   
                    if request.form.get("set_task_8_" + str(i)) != "":
                        task_8 = request.form.get("set_task_8_" + str(i))
                    else:
                        task_8 = "None"  
                    if request.form.get("set_task_9_" + str(i)) != "":
                        task_9 = request.form.get("set_task_9_" + str(i))
                    else:
                        task_9 = "None"  

                    SET_CONTROLLER_TASKS(i, task_1, task_2, task_3, task_4, task_5, task_6, task_7, task_8, task_9)

                                                        
    error_message_controller_tasks = CHECK_TASKS(GET_ALL_CONTROLLER(), "controller")

    data_controller = GET_ALL_CONTROLLER()
    dropdown_list_controller = GET_ALL_MQTT_DEVICES("controller")
   
    return render_template('dashboard_settings_controller.html',
                            error_message_add_controller=error_message_add_controller,
                            error_message_controller_tasks=error_message_controller_tasks, 
                            data_controller=data_controller,
                            dropdown_list_controller=dropdown_list_controller,                                   
                            active03="active",
                            )


# change controller position 
@app.route('/dashboard/settings/controller/position/<string:direction>/<int:id>')
@login_required
@superuser_required
def change_controller_position(id, direction):
    CHANGE_CONTROLLER_POSITION(id, direction)
    return redirect(url_for('dashboard_settings_controller'))


# delete controller
@app.route('/dashboard/settings/controller/delete/<int:id>')
@login_required
@superuser_required
def delete_controller(id):
    DELETE_CONTROLLER(id)
    return redirect(url_for('dashboard_settings_controller'))



""" ############### """
"""  speechcontrol  """
""" ############### """

@app.route('/dashboard/settings/speechcontrol', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_speechcontrol():
    error_message_snowboy = ""
    error_message_change_snowboy_settings = ""
    error_message_fileupload = ""
    error_message_hotword = ""
    error_message_speech_recognition_provider_keywords = ""
    error_message_speech_recognition_provider_settings = ""
    sensitivity = ""
    timeout = ""
    microphone = ""
    check_value_speechcontrol = ["", ""]
    snowboy_name = ""
    snowboy_task = ""   
    

    if request.method == "POST":     
        # change speech_control settings   
        if request.form.get("radio_speechcontrol") is not None:
            setting_speechcontrol = str(request.form.get("radio_speechcontrol"))
            SET_GLOBAL_SETTING_VALUE("speechcontrol", setting_speechcontrol) 

    # change radio check    
    if GET_GLOBAL_SETTING_VALUE("speechcontrol") == "speech_recognition_provider":
        check_value_speechcontrol[0] = "checked = 'on'"
        check_value_speechcontrol[1] = ""
    else:
        check_value_speechcontrol[0] = ""
        check_value_speechcontrol[1] = "checked = 'on'"

    ##################
    # snowboy settings
    ##################

    if GET_GLOBAL_SETTING_VALUE("speechcontrol") == "speech_recognition_provider":

        # check snowboy
        def START_SNOWBOY():
            from app.speechcontrol.snowboy.snowboy import SNOWBOY_START
            SNOWBOY_START()
          
        try:
            START_SNOWBOY()
        except Exception as e:  
            if "signal only works in main thread" not in str(e):      
                error_message_snowboy = "Fehler in SnowBoy: " + str(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Snowboy | " + str(e)) 
                
        if request.method == 'POST':

            # change snowboy settings
            if request.form.get("change_snowboy_settings") is not None: 
                
                # check sensitivity
                sensitivity = request.form.get("set_sensitivity")
                if sensitivity != "":     
                    sensitivity = request.form.get("set_sensitivity") 
                else:
                    sensitivity = GET_SNOWBOY_SETTINGS().sensitivity
                    
                # check timeout
                timeout = request.form.get("set_timeout")     
                if timeout != "":     
                    timeout = request.form.get("set_timeout") 
                else:
                    timeout = GET_SNOWBOY_SETTINGS().timeout  

                # set microphone
                microphone = request.form.get("set_microphone")                                            
             
                SET_SNOWBOY_SETTINGS(sensitivity, timeout, microphone)  


            #############################
            # speech recognition provider
            #############################

            # change speech_recognition_provider tasks
            if request.form.get("change_speech_recognition_provider_tasks") != None: 
                for i in range (1,26):
                    
                    if request.form.get("set_speech_recognition_provider_keywords_" + str(i)) != None:  
                        
                        keywords = request.form.get("set_speech_recognition_provider_keywords_" + str(i)) 
              
                        SET_SPEECH_RECOGNITION_PROVIDER_TASK_KEYWORDS(i, keywords)   
                        

            # change speech_recognition_provider settings
            if request.form.get("set_speech_recognition_provider_settings") != None: 
                
                snowboy_hotword                      = request.form.get("set_snowboy_hotword")        
                speech_recognition_provider          = request.form.get("set_speech_recognition_provider")
                speech_recognition_provider_username = request.form.get("set_speech_recognition_provider_username")
                speech_recognition_provider_key      = request.form.get("set_speech_recognition_provider_key")

                SET_SPEECH_RECOGNITION_PROVIDER_SETTINGS(snowboy_hotword, speech_recognition_provider, 
                                                  speech_recognition_provider_username, speech_recognition_provider_key)


            #########################################
            # snowboy and speech recognition provider
            #########################################
                    
            if request.form.get("file_upload") is not None:
                # file upload
                if 'file' not in request.files:
                    error_message_fileupload = "Keine Datei angegeben"
                else:
                    file = request.files['file']
                    error_message_fileupload = UPLOAD_HOTWORD_FILE(file)


    # snowboy settings
    speechcontrol_setting = GET_GLOBAL_SETTING_VALUE("speechcontrol")
    sensitivity           = GET_SNOWBOY_SETTINGS().sensitivity
    timeout               = GET_SNOWBOY_SETTINGS().timeout
    microphone            = GET_SNOWBOY_SETTINGS().microphone

    dropdown_list_microphone_options = ["ReSpeaker 2-Mics Pi HAT", "ReSpeaker Mic 4 Array v2.0", "Other"]   

    hotword_file_list = GET_ALL_HOTWORD_FILES()

    # speech_recognition_provider only
    snowboy_hotword                                    = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().snowboy_hotword
    speech_recognition_provider                        = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider
    speech_recognition_provider_username               = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_username
    speech_recognition_provider_key                    = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_key
    error_message_speech_recognition_provider_keywords = CHECK_SPEECH_RECOGNITION_PROVIDER_KEYWORDS(GET_ALL_SPEECH_RECOGNITION_PROVIDER_TASKS())

    speech_recognition_provider_task_list = GET_ALL_SPEECH_RECOGNITION_PROVIDER_TASKS()

    dropdown_list_speech_recognition_provider = ["Google Cloud Speech", "Google Speech Recognition",
                                                 "Houndify", "IBM Speech", "Microsoft Azure Speech", 
                                                 "Microsoft Bing Voice Recognition", "Wit.ai"]
    
    error_message_speech_recognition_provider_tasks = ""
    error_message_speech_recognition_provider_settings = CHECK_SPEECH_RECOGNITION_PROVIDER_SETTINGS(GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS())

    return render_template('dashboard_settings_speechcontrol.html',
                            error_message_snowboy=error_message_snowboy,   
                            error_message_change_snowboy_settings=error_message_change_snowboy_settings,                                   
                            error_message_fileupload=error_message_fileupload,
                            error_message_hotword=error_message_hotword,
                            error_message_speech_recognition_provider_keywords=error_message_speech_recognition_provider_keywords,                             
                            error_message_speech_recognition_provider_settings=error_message_speech_recognition_provider_settings,
                            
                            speechcontrol_setting=speechcontrol_setting,
                            check_value_speechcontrol=check_value_speechcontrol,
                            sensitivity=sensitivity,
                            timeout=timeout,
                            microphone=microphone,
                            dropdown_list_microphone_options=dropdown_list_microphone_options,

                            hotword_file_list=hotword_file_list,
                            snowboy_hotword=snowboy_hotword,
                            dropdown_list_speech_recognition_provider=dropdown_list_speech_recognition_provider,
                            speech_recognition_provider_task_list=speech_recognition_provider_task_list,
                            speech_recognition_provider=speech_recognition_provider,
                            speech_recognition_provider_username=speech_recognition_provider_username,
                            speech_recognition_provider_key=speech_recognition_provider_key,
                            active04="active",
                            )


# download hotword file
@app.route('/dashboard/settings/speechcontrol/snowboy/download/hotword/<path:filepath>')
@login_required
@superuser_required
def download_hotword_file(filepath):
    if filepath is None:
        print("Ungültiger Pfad angegeben")     
    try:
        path = GET_PATH() + "/app/snowboy/resources/"     
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /app/snowboy/resources/" + filepath + " | downloaded")
        return send_from_directory(path, filepath)
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /app/snowboy/resources/" + filepath + " | " + str(e)) 


# delete snowboy hotwords
@app.route('/dashboard/settings/speechcontrol/snowboy/delete/hotword/<string:filename>')
@login_required
@superuser_required
def delete_snowboy_hotword(filename):
    DELETE_HOTWORD_FILE(filename)
    return redirect(url_for('dashboard_settings_speechcontrol'))


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
            for i in range (1,51): 
                
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
                            active05="active",
                            )


# change users position 
@app.route('/dashboard/settings/user/position/<string:direction>/<int:id>')
@login_required
@superuser_required
def change_user_position(id, direction):
    CHANGE_USER_POSITION(id, direction)
    return redirect(url_for('dashboard_settings_user'))


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
                            active06="active",
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
                            active07="active",
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
                            active08="active",
                            )


# download system logfile
@app.route('/dashboard/settings/system_log/download/<path:filepath>')
@login_required
@superuser_required
def download_system_logfile(filepath): 
    try:
        path = GET_PATH() + "/logs/"    
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /logs/" + filepath + " | downloaded")
        return send_from_directory(path, filepath)
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/" + filepath + " | " + str(e))
