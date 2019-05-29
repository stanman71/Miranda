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
                            if GET_MQTT_DEVICE_BY_NAME(option_check) or option_check.isdigit(): 
                            
                                if option_check.isdigit():        
                                    option_check_ieeeAddr = GET_MQTT_DEVICE_BY_ID(option_check).ieeeAddr
                                    option_check_inputs   = GET_MQTT_DEVICE_BY_ID(option_check).inputs       
                                    option_check          = GET_MQTT_DEVICE_BY_ID(option_check).name
                                    
                                else:
                                    option_check_ieeeAddr = device.option_check_ieeeAddr
                                    option_check_inputs   = device.option_check_inputs
                                 
                                    
                                # set option check value 1
                                option_check_value_1 = request.form.get("set_option_check_value_1_" + str(i))

                                if option_check_value_1 != None:                  
                                    option_check_value_1 = option_check_value_1.replace(" ", "")

                                    # replace array_position to sensor name 
                                    if option_check_value_1.isdigit():
                                        
                                        # first two array elements are no sensors
                                        if option_check_value_1 == "0" or option_check_value_1 == "1":
                                            option_check_value_1 = "None"
                                            
                                        else:           
                                            sensor_list          = GET_MQTT_DEVICE_BY_IEEEADDR(option_check_ieeeAddr).inputs
                                            sensor_list          = sensor_list.split(",")
                                            option_check_value_1 = sensor_list[int(option_check_value_1)-2]


                                # set option check value 2
                                option_check_value_2 = request.form.get("set_option_check_value_2_" + str(i))
                                
                                if option_check_value_2 == ""  or option_check_value_2 == None:
                                    option_check_value_2 = "None"       
                                
                                    
                            else:
                                option_check_ieeeAddr = "None"
                                option_check_inputs   = "None"                                    

     
                                if option_check == "IP-Address":
                                
                                    # set option check value 1
                                    option_check_value_1 = request.form.get("set_option_check_value_1_" + str(i))
                                   
                                    if option_check_value_1 == "" or option_check_value_1 == None:
                                        option_check_value_1 = "None" 
                                          
                                    # set option check value 2  
                                    option_check_value_2   = "None"      
                                    
                                           
                        else:
                            option_sensor_ieeeAddr = "None"
                            option_check_inputs    = "None"
                            option_check_value_1   = "None"
                            option_check_value_2   = "None"                        
                            
                                   
                        # set option command
                        option_command = request.form.get("set_option_command_" + str(i))
                        
                        if option_command == "" or option_command == None:
                            option_command = "None" 
                        
                        option_command = option_command.replace(" ", "")
                                 
                                 
                        SET_MQTT_DEVICE_OPTIONS(device.ieeeAddr, option_check, option_check_ieeeAddr, option_check_inputs,
                                                option_check_value_1, option_check_value_2, option_command)
                        
                            
                        # ##############
                        #    Commands
                        # ##############

                        # setting changed ?
                        if device.option_command != device.previous_option_command and option_command != "None":
                            
                            change_state = True
                            
                            # check ip_address 
                            if device.option_check == "IP-Address" and device.option_command == "OFF":
   
                                if os.system("ping -c 1 " + option_check_value_1) == 0:
                                    error_message_device = device.name + " >>> Gerät ist noch eingeschaltet"
                                    change_state = False
                    
                    
                            # check sensor
                            if GET_MQTT_DEVICE_BY_NAME(option_check):

                                sensor_ieeeAddr    = device.option_check_ieeeAddr
                                sensor_key         = device.option_check_value_1
                                
                                input_setting = device.option_check_value_2
                                
                                if input_setting[:1] == "<":
                                    operator = "<"
                                    value    = input_setting[1:]
                                    value    = value.replace(" ","")
                                    
                                if input_setting[:1] == ">":
                                    operator = ">"
                                    value    = input_setting[1:]
                                    value    = value.replace(" ","")  
                                                                  
                                if input_setting[:1] == "=":
                                    operator = "="
                                    value    = input_setting[1:]
                                    value    = value.replace(" ","")                                


                                # get sensordata 
                                data         = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(sensor_ieeeAddr).last_values)
                                sensor_value = data[sensor_key]


                                # compare conditions

                                if operator == "=" and not value.isdigit():
                                    if str(sensor_value) == str(value):
                                        change_state = True
                                    else:
                                        change_state = False
                                    
                                if operator == "=" and value.isdigit():
                                    if int(sensor_value) == int(value):
                                        change_state = True    
                                    else:
                                        change_state = False
                                        
                                if operator == "<" and value.isdigit():
                                    if int(sensor_value) < int(value):
                                        change_state = True
                                    else:
                                        change_state = False
                                        
                                if operator == ">" and value.isdigit():
                                    if int(sensor_value) > int(value):
                                        change_state = True 
                                    else:
                                        change_state = False
                                        
                                error_message_device = device.name + " >>> Sensor erteilt keine Freigabe"
       
       
                            if change_state:                         
                                error_message_device = MQTT_SET_DEVICE_SETTING(device.name, device.gateway, device.ieeeAddr, device.option_command)
                        
                                UPDATE_MQTT_DEVICE_PREVIOUS_OPTION_COMMAND(device.ieeeAddr)
                             
                                    
                        RESET_MQTT_DEVICE_OPTION_COMMAND(device.ieeeAddr)
                                        
                                
                except Exception as e:
                    print(e)
                              

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

    # get sensor list
    try:
        mqtt_device_1_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(1).inputs
        mqtt_device_1_inputs = mqtt_device_1_inputs.replace(" ", "")
    except:
        mqtt_device_1_inputs = ""
    try:
        mqtt_device_2_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(2).inputs
        mqtt_device_2_inputs = mqtt_device_2_inputs.replace(" ", "")
    except:
        mqtt_device_2_inputs = ""
    try:        
        mqtt_device_3_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(3).inputs
        mqtt_device_3_inputs = mqtt_device_3_inputs.replace(" ", "")
    except:
        mqtt_device_3_inputs = ""
    try:        
        mqtt_device_4_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(4).inputs
        mqtt_device_4_inputs = mqtt_device_4_inputs.replace(" ", "")
    except:
        mqtt_device_4_inputs = ""
    try:        
        mqtt_device_5_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(5).inputs
        mqtt_device_5_inputs = mqtt_device_5_inputs.replace(" ", "")
    except:
        mqtt_device_5_inputs = ""
    try:        
        mqtt_device_6_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(6).inputs
        mqtt_device_6_inputs = mqtt_device_6_inputs.replace(" ", "")
    except:
        mqtt_device_6_inputs = ""
    try:        
        mqtt_device_7_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(7).inputs
        mqtt_device_7_inputs = mqtt_device_7_inputs.replace(" ", "")
    except:
        mqtt_device_7_inputs = ""
    try:        
        mqtt_device_8_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(8).inputs
        mqtt_device_8_inputs = mqtt_device_8_inputs.replace(" ", "")
    except:
        mqtt_device_8_inputs = ""
    try:        
        mqtt_device_9_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(9).inputs
        mqtt_device_9_inputs = mqtt_device_9_inputs.replace(" ", "")
    except:
        mqtt_device_9_inputs = ""
    try:        
        mqtt_device_10_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(10).inputs
        mqtt_device_10_inputs = mqtt_device_10_inputs.replace(" ", "")
    except:
        mqtt_device_10_inputs = ""
    try:        
        mqtt_device_11_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(11).inputs
        mqtt_device_11_inputs = mqtt_device_11_inputs.replace(" ", "")
    except:
        mqtt_device_11_inputs = ""
    try:        
        mqtt_device_12_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(12).inputs
        mqtt_device_12_inputs = mqtt_device_12_inputs.replace(" ", "")
    except:
        mqtt_device_12_inputs = ""
    try:        
        mqtt_device_13_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(13).inputs
        mqtt_device_13_inputs = mqtt_device_13_inputs.replace(" ", "")
    except:
        mqtt_device_13_inputs = ""
    try:        
        mqtt_device_14_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(14).inputs
        mqtt_device_14_inputs = mqtt_device_14_inputs.replace(" ", "")
    except:
        mqtt_device_14_inputs = ""
    try:        
        mqtt_device_15_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(15).inputs
        mqtt_device_15_inputs = mqtt_device_15_inputs.replace(" ", "")
    except:
        mqtt_device_15_inputs = ""    
    try:        
        mqtt_device_16_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(16).inputs
        mqtt_device_16_inputs = mqtt_device_16_inputs.replace(" ", "")
    except:
        mqtt_device_16_inputs = ""
    try:        
        mqtt_device_17_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(17).inputs
        mqtt_device_17_inputs = mqtt_device_17_inputs.replace(" ", "")
    except:
        mqtt_device_17_inputs = ""
    try:        
        mqtt_device_18_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(18).inputs
        mqtt_device_18_inputs = mqtt_device_18_inputs.replace(" ", "")
    except:
        mqtt_device_18_inputs = ""
    try:        
        mqtt_device_19_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(19).inputs
        mqtt_device_19_inputs = mqtt_device_19_inputs.replace(" ", "")
    except:
        mqtt_device_19_inputs = ""
    try:        
        mqtt_device_20_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(20).inputs
        mqtt_device_20_inputs = mqtt_device_20_inputs.replace(" ", "")
    except:
        mqtt_device_20_inputs = ""   
    try:        
        mqtt_device_21_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(21).inputs
        mqtt_device_21_inputs = mqtt_device_21_inputs.replace(" ", "")
    except:
        mqtt_device_21_inputs = ""   
    try:        
        mqtt_device_22_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(22).inputs
        mqtt_device_22_inputs = mqtt_device_22_inputs.replace(" ", "")
    except:
        mqtt_device_22_inputs = ""   
    try:        
        mqtt_device_23_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(23).inputs
        mqtt_device_23_inputs = mqtt_device_23_inputs.replace(" ", "")
    except:
        mqtt_device_23_inputs = ""   
    try:        
        mqtt_device_24_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(24).inputs
        mqtt_device_24_inputs = mqtt_device_24_inputs.replace(" ", "")
    except:
        mqtt_device_24_inputs = ""   
    try:        
        mqtt_device_25_inputs = "None,-------------------------," + GET_MQTT_DEVICE_BY_ID(25).inputs
        mqtt_device_25_inputs = mqtt_device_25_inputs.replace(" ", "")
    except:
        mqtt_device_25_inputs = ""           


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
