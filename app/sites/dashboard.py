from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from functools import wraps

from app import app
from app.components.file_management import GET_LOGFILE_SYSTEM, GET_CONFIG_VERSION
from app.database.database import *
from app.components.control_led import *
from app.components.mqtt_functions import MQTT_SET_DEVICE


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    error_message_led = ""
    error_message_device = ""
    error_message_log = ""
    checkbox = ""
        
    
    if request.method == "POST":
        
        if request.form.get("change_led_settings") != None:
            
            for i in range (1,21):

                # set led group
                if request.form.get("set_group_" + str(i)) != None:  

                    setting = request.form.get("set_group_" + str(i))
                            
                    setting_type = setting.split("_")[0]
                    
                    # start another scene / program
                    if setting_type == "scene" or setting_type == "program":

                        if setting_type == "scene":
                            brightness = request.form.get("set_brightness_" + str(i))
                            error_message_led = LED_START_SCENE(i, int(setting.split("_")[1]), int(brightness))                         
                            continue
                        
                        if setting_type == "program":
                            error_message_led = LED_START_PROGRAM_THREAD(i, int(setting.split("_")[1])) 
                            continue  
                            
                    else:

                        # turn led group off
                        if setting == "turn_off":
                            error_message_led = LED_TURN_OFF_GROUP(i)  
                            continue                     

                        # change brightness
                        if request.form.get("set_brightness_" + str(i)) != None:
                            
                            brightness = request.form.get("set_brightness_" + str(i))

                            # brightness changed ?
                            if int(brightness) != GET_LED_GROUP_BY_ID(i).current_brightness:

                                error_message_led = LED_SET_BRIGHTNESS(i, int(brightness)) 
                                continue              
    
    
        if request.form.get("change_device_settings") != None:
            
            for i in range (1,21):

                # set device  
                if request.form.get("set_device_power_" + str(i)) != None:
                    power_setting = request.form.get("set_device_power_" + str(i))
                else:
                    power_setting = ""
                
                devices = GET_ALL_MQTT_DEVICES("device")
                
                for device in devices:
                    if device.id == i:
                        
                        name     = device.name
                        gateway  = device.gateway
                        ieeeAddr = device.ieeeAddr
                        
                        # setting changed ?
                        if device.power_setting != power_setting:
                        
                            SET_MQTT_DEVICE_SETTINGS(ieeeAddr, power_setting)
                            error_message_device = MQTT_SET_DEVICE(name, gateway, ieeeAddr, power_setting)
                            break 
                          

    data_led = GET_ALL_ACTIVE_LED_GROUPS()
    dropdown_list_led_scenes   = GET_ALL_LED_SCENES()
    dropdown_list_led_programs = GET_ALL_LED_PROGRAMS()
    
    data_device = GET_ALL_MQTT_DEVICES("device")

    data_sensor = GET_ALL_MQTT_DEVICES("sensor")

    if GET_LOGFILE_SYSTEM(10) is not None:
        data_log_system = GET_LOGFILE_SYSTEM(10)
    else:
        data_log_system = ""
        error_message_log = "Keine Einträge gefunden"

    version = GET_CONFIG_VERSION()        

    return render_template('dashboard.html',
                            data_led=data_led,
                            dropdown_list_led_scenes=dropdown_list_led_scenes,
                            dropdown_list_led_programs=dropdown_list_led_programs,
                            data_device=data_device,
                            checkbox=checkbox,
                            data_log_system=data_log_system, 
                            data_sensor=data_sensor,
                            version=version,  
                            error_message_led=error_message_led,
                            error_message_log=error_message_log,  
                            error_message_device=error_message_device,   
                            role=current_user.role,
                            )
