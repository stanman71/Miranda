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
from app.components.mqtt_functions import MQTT_SET_DEVICE_SETTING
from app.components.checks import CHECK_DASHBOARD_CHECKS


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
        
    # sensor name changed ?
    UPDATE_DASHBOARD_SENSOR_OPTION_NAMES()
    
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
                
                try:
                    
                    device = GET_MQTT_DEVICE_BY_ID(i)
                    
                    if "device" in device.device_type:
               
                        # set option check
                        option_check = request.form.get("set_option_check_" + str(i))
                        
                        if option_check == "" or option_check == None:
                            option_check = "None"  


                        if option_check != "None":
                            
                            # sensor choosen ?
                            try:
                                option_check_ieeeAddr = GET_MQTT_DEVICE_BY_NAME(option_check).ieeeAddr
                            except:
                                option_check_ieeeAddr = "None"
                            
                            # set option check value 1
                            option_check_value_1 = request.form.get("set_option_check_value_1_" + str(i))
                           
                            if option_check_value_1 == "" or option_check_value_1 == None:
                                option_check_value_1 = "None"                       
                            
                            
                            # value changed ?
                            if option_check_value_1 != device.option_check_value_1:
                                option_check_value_2 = "None" 
                                
                            else:
                                # set option check value 2
                                option_check_value_2 = request.form.get("set_option_check_value_2_" + str(i))
                                
                                if option_check_value_2 == ""  or option_check_value_2 == None:
                                    option_check_value_2 = "None"    
                                  
           
                        else:
                            option_sensor_ieeeAddr = "None"
                            option_check_value_1   = "None"
                            option_check_value_2   = "None"                        
                            
                                   
                        # set option command
                        option_command = request.form.get("set_option_command_" + str(i))
                        
                        if option_command == "" or option_command == None:
                            option_command = "None" 
                        
                        option_command = option_command.replace(" ", "")
                                 
                                 
                        SET_MQTT_DEVICE_OPTIONS(device.ieeeAddr, option_check, option_check_ieeeAddr, 
                                                option_check_value_1, option_check_value_2, option_command)
                        
                            
                        # ##############
                        #    Commands
                        # ##############

                        # device_switch
                        
                        if device.device_type == "device_switch":
                                
                            # setting changed ?
                            if device.option_command != device.previous_option_command:
                                
                                change_powerstate = True
                                
                                # check ip_address 
                                if device.option_check == "IP-Address" and device.option_command == "OFF":
       
                                    if os.system("ping -c 1 " + option_check_value_1) == 0:
                                        error_message_device = device.name + " >>> Gerät ist noch eingeschaltet"
                                        change_powerstate = False
                        
                   
                                if change_powerstate:                         
                                    error_message_device = MQTT_SET_DEVICE_SETTING(device.name, device.gateway, device.ieeeAddr, device.option_command)
                            
                                    UPDATE_MQTT_DEVICE_PREVIOUS_OPTION_COMMAND(device.ieeeAddr)
                             
                                    
                        RESET_MQTT_DEVICE_OPTION_COMMAND(device.ieeeAddr)
                                        
                                
                except:
                    pass
                              

    data_led = GET_ALL_ACTIVE_LED_GROUPS()
    dropdown_list_led_scenes   = GET_ALL_LED_SCENES()
    dropdown_list_led_programs = GET_ALL_LED_PROGRAMS()
    
    list_mqtt_devices = GET_ALL_MQTT_DEVICES("sensor")
    
    dropdown_list_checks    = ["IP-Address"] 
    dropdown_list_operators = ["=", ">", "<"]
    
    data_device = GET_ALL_MQTT_DEVICES("device")
    data_sensor = GET_ALL_MQTT_DEVICES("sensor")
    
    error_message_device_checks = CHECK_DASHBOARD_CHECKS(GET_ALL_MQTT_DEVICES("device"))

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
                            dropdown_list_checks=dropdown_list_checks,
                            dropdown_list_operators=dropdown_list_operators,
                            list_mqtt_devices=list_mqtt_devices,
                            data_device=data_device,
                            checkbox=checkbox,
                            data_log_system=data_log_system, 
                            data_sensor=data_sensor,
                            version=version,  
                            error_message_led=error_message_led,
                            error_message_log=error_message_log,  
                            error_message_device=error_message_device,   
                            error_message_device_checks=error_message_device_checks,
                            role=current_user.role,
                            )
