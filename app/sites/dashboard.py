from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from functools import wraps

from app import app
from app.components.file_management import GET_LOGFILE_SYSTEM, GET_CONFIG_VERSION
from app.database.database import *
from app.components.checks import CHECK_DASHBOARD_CHECK_SETTINGS
from app.components.process_management import ADD_TASK_TO_PROCESS_MANAGEMENT


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
        
    # check sensor name changed ?
    UPDATE_DASHBOARD_CHECK_SENSOR_NAMES()
    
    if request.method == "POST":
        
        if request.form.get("change_led_settings") != None:
            
            for i in range (1,21):

                # set led group
                if request.form.get("set_group_" + str(i)) != None:  

                    setting      = request.form.get("set_group_" + str(i))    
                    setting_type = setting.split("_")[0]
                    
                    # start scene
                    if setting_type == "scene":

                        brightness = request.form.get("set_brightness_" + str(i))
                        ADD_TASK_TO_PROCESS_MANAGEMENT(1, ("dasboard_command", "led_scene", i, int(setting.split("_")[1]), int(brightness)))  
                        time.sleep(3)                    
                        continue

    
                    else:

                        # turn led group off
                        if setting == "turn_off":
                            ADD_TASK_TO_PROCESS_MANAGEMENT(1, ("dasboard_command", "led_off", i))  
                            time.sleep(3)                               
                            continue                     

                        # change brightness
                        if request.form.get("set_brightness_" + str(i)) != None:
                            
                            brightness = request.form.get("set_brightness_" + str(i))

                            # brightness changed ?
                            if int(brightness) != GET_LED_GROUP_BY_ID(i).current_brightness:
                                ADD_TASK_TO_PROCESS_MANAGEMENT(1, ("dasboard_command", "led_brightness", i, int(brightness)))  
                                time.sleep(3)     
                                continue              
    
    
        if request.form.get("change_device_settings") != None:
            
            for i in range (1,21):
                
                try:
                    
                    device = GET_MQTT_DEVICE_BY_ID(i)
                    
                    if "device" in device.device_type:
                        
                        # set dashboard check option
                        dashboard_check_option = request.form.get("set_dashboard_check_option_" + str(i))
                        dashboard_check_option = dashboard_check_option.replace(" ","")
                        
                        if dashboard_check_option == "" or dashboard_check_option == None:
                            dashboard_check_option = "None"  

                        if dashboard_check_option != "None":

                            # set dashboard check command option
                            dashboard_check_command = request.form.get("set_dashboard_check_command_" + str(i))
                            
                            if dashboard_check_command == "" or dashboard_check_command == None:
                                dashboard_check_command = "None"  
          
          
                            # check_option not changed
                            if GET_MQTT_DEVICE_BY_IEEEADDR(device.ieeeAddr).dashboard_check_option == dashboard_check_option:
                                
                                dashboard_check_sensor_ieeeAddr = device.dashboard_check_sensor_ieeeAddr
                            
 
                                # ###### #
                                # SENSOR # 
                                # ###### #                              
                                 
                                if dashboard_check_sensor_ieeeAddr != "None":
                                
                                    # set dashboard check value 1
                                    dashboard_check_value_1 = request.form.get("set_dashboard_check_value_1_" + str(i))

                                    if dashboard_check_value_1 != None:                  
                                        dashboard_check_value_1 = dashboard_check_value_1.replace(" ", "")

                                        # replace array_position to sensor name 
                                        if dashboard_check_value_1.isdigit():
                                            
                                            # first two array elements are no sensors
                                            if dashboard_check_value_1 == "0" or dashboard_check_value_1 == "1":
                                                dashboard_check_value_1 = "None"
                                                
                                            else:           
                                                sensor_list             = GET_MQTT_DEVICE_BY_IEEEADDR(dashboard_check_sensor_ieeeAddr).inputs
                                                sensor_list             = sensor_list.split(",")
                                                dashboard_check_value_1 = sensor_list[int(dashboard_check_value_1)-2]


                                    # set dashboard check value 2
                                    dashboard_check_value_2 = request.form.get("set_dashboard_check_value_2_" + str(i))
                                    
                                    if dashboard_check_value_2 == ""  or dashboard_check_value_2 == None:
                                        dashboard_check_value_2 = "None"       
                                    
                                    # set dashboard check value 3
                                    dashboard_check_value_3 = request.form.get("set_dashboard_check_value_3_" + str(i))
                                    
                                    if dashboard_check_value_3 == ""  or dashboard_check_value_3 == None:
                                        dashboard_check_value_3 = "None"        
                

                                # ########## #
                                # IP ADDRESS # 
                                # ########## #
     
                                if dashboard_check_option == "IP-Address":
                                
                                    # set dashboard check value 1
                                    dashboard_check_value_1 = request.form.get("set_dashboard_check_value_1_" + str(i))
                                   
                                    if dashboard_check_value_1 == "" or dashboard_check_value_1 == None:
                                        dashboard_check_value_1 = "None" 
                                          
                                    dashboard_check_sensor_ieeeAddr = "None"
                                    dashboard_check_sensor_inputs   = "None"
                                    dashboard_check_value_2         = "None"                        
                                    dashboard_check_value_3         = "None"   
                               

                            # #################### #
                            # CHECK OPTION CHANGED # 
                            # #################### #
                                
                            else:
                                    
                                # sensor choosen ?
                                if GET_MQTT_DEVICE_BY_NAME(dashboard_check_option) or dashboard_check_option.isdigit(): 

                                    if dashboard_check_option.isdigit():        
                                        dashboard_check_sensor_ieeeAddr = GET_MQTT_DEVICE_BY_ID(dashboard_check_option).ieeeAddr
                                        dashboard_check_sensor_inputs   = GET_MQTT_DEVICE_BY_ID(dashboard_check_option).inputs       
                                        dashboard_check_option          = GET_MQTT_DEVICE_BY_ID(dashboard_check_option).name
                                        
                                    else:
                                        dashboard_check_sensor_ieeeAddr = GET_MQTT_DEVICE_BY_NAME(dashboard_check_option).ieeeAddr
                                        dashboard_check_sensor_inputs   = GET_MQTT_DEVICE_BY_NAME(dashboard_check_option).inputs                                  
                                

                                    # previous option was "IP-Address" ?
                                    if device.dashboard_check_option != "IP-Address":

                                        dashboard_check_value_1 = request.form.get("set_dashboard_check_value_1_" + str(i))
                                        
                                        if dashboard_check_value_1 != None:                  
                                            dashboard_check_value_1 = dashboard_check_value_1.replace(" ", "")

                                            # replace array_position to sensor name 
                                            if dashboard_check_value_1.isdigit():
                                                
                                                # first two array elements are no sensors
                                                if dashboard_check_value_1 == "0" or dashboard_check_value_1 == "1":
                                                    dashboard_check_value_1 = "None"
                                                    
                                                else:           
                                                    sensor_list             = GET_MQTT_DEVICE_BY_IEEEADDR(dashboard_check_sensor_ieeeAddr).inputs
                                                    sensor_list             = sensor_list.split(",")
                                                    dashboard_check_value_1 = sensor_list[int(dashboard_check_value_1)-2]   
                                                    
                                        dashboard_check_value_2 = request.form.get("set_dashboard_check_value_2_" + str(i))  
                                        dashboard_check_value_3 = request.form.get("set_dashboard_check_value_3_" + str(i))  
                                                    
          
                                    else:
                                        dashboard_check_value_1 = "None" 
                                        dashboard_check_value_2 = "None"  
                                        dashboard_check_value_3 = "None"                                          
                                            
                                else:
                                    dashboard_check_value_1 = "None" 
                                    dashboard_check_value_2 = "None"  
                                    dashboard_check_value_3 = "None"  
                                                                                            
                                                                
                        SET_MQTT_DEVICE_DASHBOARD_CHECK(device.ieeeAddr, dashboard_check_option, dashboard_check_command,
                                                        dashboard_check_sensor_ieeeAddr, dashboard_check_sensor_inputs, dashboard_check_value_1, 
                                                        dashboard_check_value_2, dashboard_check_value_3)
                            
                            
                        # ##############
                        #    Commands
                        # ##############
                        
                        dashboard_command = request.form.get("set_dashboard_command_" + str(i))
                        dashboard_command = dashboard_command.replace(" ","")

                        # setting changed ?
                        if dashboard_command != device.previous_command and dashboard_command != "None":
                            
                            change_state = True
                            
                            # check ip_address 
                            if device.dashboard_check_option == "IP-Address" and dashboard_command == device.dashboard_check_command:
   
                                if os.system("ping -c 1 " + dashboard_check_value_1) == 0:
                                    error_message_device = device.name + " >>> Gerät ist noch eingeschaltet"
                                    change_state = False

                            # check sensor
                            if device.dashboard_check_sensor_ieeeAddr != "None" and dashboard_command == device.dashboard_check_command.replace(" ",""):
                                
                                sensor_ieeeAddr = device.dashboard_check_sensor_ieeeAddr
                                sensor_key      = device.dashboard_check_value_1
                                
                                operator = device.dashboard_check_value_2
                                value    = device.dashboard_check_value_3
                                
                                # get sensordata 
                                data         = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device.dashboard_check_sensor_ieeeAddr).last_values)
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
                                
                                ADD_TASK_TO_PROCESS_MANAGEMENT(1, ("dasboard_command", "device", device.name, device.gateway, device.ieeeAddr, dashboard_command))  
                                time.sleep(3)                            

                except Exception as e:
                    print(e)
                              

    data_led = GET_ALL_ACTIVE_LED_GROUPS()
    dropdown_list_led_scenes   = GET_ALL_LED_SCENES()

    list_mqtt_devices = GET_ALL_MQTT_DEVICES("sensor")
    
    dropdown_list_check_options = ["IP-Address"] 
    dropdown_list_operators     = ["=", ">", "<"]
    
    data_device = GET_ALL_MQTT_DEVICES("device")
    data_sensor = GET_ALL_MQTT_DEVICES("sensor")
    
    error_message_device_checks = CHECK_DASHBOARD_CHECK_SETTINGS(GET_ALL_MQTT_DEVICES("device"))


    if GET_LOGFILE_SYSTEM(10) is not None:
        data_log_system = GET_LOGFILE_SYSTEM(10)
    else:
        data_log_system = ""
        error_message_log = "Keine Einträge gefunden"

    version = GET_CONFIG_VERSION()        

    # get sensor list
    try:
        mqtt_device_1_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(1).inputs
        mqtt_device_1_inputs = mqtt_device_1_inputs.replace(" ", "")
    except:
        mqtt_device_1_inputs = ""
    try:
        mqtt_device_2_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(2).inputs
        mqtt_device_2_inputs = mqtt_device_2_inputs.replace(" ", "")
    except:
        mqtt_device_2_inputs = ""
    try:        
        mqtt_device_3_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(3).inputs
        mqtt_device_3_inputs = mqtt_device_3_inputs.replace(" ", "")
    except:
        mqtt_device_3_inputs = ""
    try:        
        mqtt_device_4_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(4).inputs
        mqtt_device_4_inputs = mqtt_device_4_inputs.replace(" ", "")
    except:
        mqtt_device_4_inputs = ""
    try:        
        mqtt_device_5_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(5).inputs
        mqtt_device_5_inputs = mqtt_device_5_inputs.replace(" ", "")
    except:
        mqtt_device_5_inputs = ""
    try:        
        mqtt_device_6_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(6).inputs
        mqtt_device_6_inputs = mqtt_device_6_inputs.replace(" ", "")
    except:
        mqtt_device_6_inputs = ""
    try:        
        mqtt_device_7_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(7).inputs
        mqtt_device_7_inputs = mqtt_device_7_inputs.replace(" ", "")
    except:
        mqtt_device_7_inputs = ""
    try:        
        mqtt_device_8_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(8).inputs
        mqtt_device_8_inputs = mqtt_device_8_inputs.replace(" ", "")
    except:
        mqtt_device_8_inputs = ""
    try:        
        mqtt_device_9_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(9).inputs
        mqtt_device_9_inputs = mqtt_device_9_inputs.replace(" ", "")
    except:
        mqtt_device_9_inputs = ""
    try:        
        mqtt_device_10_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(10).inputs
        mqtt_device_10_inputs = mqtt_device_10_inputs.replace(" ", "")
    except:
        mqtt_device_10_inputs = ""
    try:        
        mqtt_device_11_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(11).inputs
        mqtt_device_11_inputs = mqtt_device_11_inputs.replace(" ", "")
    except:
        mqtt_device_11_inputs = ""
    try:        
        mqtt_device_12_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(12).inputs
        mqtt_device_12_inputs = mqtt_device_12_inputs.replace(" ", "")
    except:
        mqtt_device_12_inputs = ""
    try:        
        mqtt_device_13_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(13).inputs
        mqtt_device_13_inputs = mqtt_device_13_inputs.replace(" ", "")
    except:
        mqtt_device_13_inputs = ""
    try:        
        mqtt_device_14_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(14).inputs
        mqtt_device_14_inputs = mqtt_device_14_inputs.replace(" ", "")
    except:
        mqtt_device_14_inputs = ""
    try:        
        mqtt_device_15_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(15).inputs
        mqtt_device_15_inputs = mqtt_device_15_inputs.replace(" ", "")
    except:
        mqtt_device_15_inputs = ""    
    try:        
        mqtt_device_16_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(16).inputs
        mqtt_device_16_inputs = mqtt_device_16_inputs.replace(" ", "")
    except:
        mqtt_device_16_inputs = ""
    try:        
        mqtt_device_17_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(17).inputs
        mqtt_device_17_inputs = mqtt_device_17_inputs.replace(" ", "")
    except:
        mqtt_device_17_inputs = ""
    try:        
        mqtt_device_18_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(18).inputs
        mqtt_device_18_inputs = mqtt_device_18_inputs.replace(" ", "")
    except:
        mqtt_device_18_inputs = ""
    try:        
        mqtt_device_19_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(19).inputs
        mqtt_device_19_inputs = mqtt_device_19_inputs.replace(" ", "")
    except:
        mqtt_device_19_inputs = ""
    try:        
        mqtt_device_20_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(20).inputs
        mqtt_device_20_inputs = mqtt_device_20_inputs.replace(" ", "")
    except:
        mqtt_device_20_inputs = ""   
    try:        
        mqtt_device_21_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(21).inputs
        mqtt_device_21_inputs = mqtt_device_21_inputs.replace(" ", "")
    except:
        mqtt_device_21_inputs = ""   
    try:        
        mqtt_device_22_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(22).inputs
        mqtt_device_22_inputs = mqtt_device_22_inputs.replace(" ", "")
    except:
        mqtt_device_22_inputs = ""   
    try:        
        mqtt_device_23_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(23).inputs
        mqtt_device_23_inputs = mqtt_device_23_inputs.replace(" ", "")
    except:
        mqtt_device_23_inputs = ""   
    try:        
        mqtt_device_24_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(24).inputs
        mqtt_device_24_inputs = mqtt_device_24_inputs.replace(" ", "")
    except:
        mqtt_device_24_inputs = ""   
    try:        
        mqtt_device_25_inputs = "None,--------------------------------," + GET_MQTT_DEVICE_BY_ID(25).inputs
        mqtt_device_25_inputs = mqtt_device_25_inputs.replace(" ", "")
    except:
        mqtt_device_25_inputs = ""           


    return render_template('dashboard.html',
                            data_led=data_led,
                            dropdown_list_led_scenes=dropdown_list_led_scenes,
                            dropdown_list_check_options=dropdown_list_check_options,
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
