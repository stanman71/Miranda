from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps

from app import app
from app.database.database import *
from app.components.checks import CHECK_WATERING_SETTINGS


# access rights
def permission_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.permission_watering == "checked":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


""" ############# """
""" site watering """
""" ############# """

@app.route('/dashboard/watering', methods=['GET', 'POST'])
@login_required
@permission_required
def dashboard_watering():
    error_message_add_plant = ""
    error_message_change_name = ""
    pumptime = ""
    moisture = ""
    mqtt_device_ieeeAddr = ""
    mqtt_device_name = ""
    control_sensor_moisture = ""
    control_sensor_watertank = ""

    if request.method == "POST": 
        
        # add plant
        if request.form.get("add_plant") != None: 
            
            if request.form.get("set_name") != None:
                # missing name
                if request.form.get("set_name") == "":
                    error_message_add_plant = "Keinen Namen angegeben"  
                                        
                else:         
                    name                    = request.form.get("set_name")
                    mqtt_device_ieeeAddr    = request.form.get("set_mqtt_device_ieeeAddr") 
                    error_message_add_plant = ADD_PLANT(name, mqtt_device_ieeeAddr)
        
        
        # change settings
        if request.form.get("change_settings") != None: 
             
            for i in range (1,26):

                if request.form.get("set_name_" + str(i)) != None:
                    
                    # check name
                    if (request.form.get("set_name_" + str(i)) != "" and 
                        GET_PLANT_BY_NAME(request.form.get("set_name_" + str(i))) == None):
                        name = request.form.get("set_name_" + str(i)) 
                        
                    elif request.form.get("set_name_" + str(i)) == GET_PLANT_BY_ID(i).name:
                        name = GET_PLANT_BY_ID(i).name                        
                        
                    else:
                        name = GET_PLANT_BY_ID(i).name 
                        error_message_change_name = "Ungültige Eingabe (leeres Feld / Name schon vergeben)"                        
    
                    mqtt_device = request.form.get("set_mqtt_device_" + str(i))

                    if GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device):
                        mqtt_device_ieeeAddr = mqtt_device
                    elif GET_MQTT_DEVICE_BY_ID(mqtt_device):
                        mqtt_device_ieeeAddr = GET_MQTT_DEVICE_BY_ID(mqtt_device).ieeeAddr
                    else:
                        mqtt_device_ieeeAddr == ""
                    
                    group    = request.form.get("set_group_" + str(i))                                                                       
                    pumptime = request.form.get("set_pumptime_" + str(i))
                
                    if request.form.get("set_control_sensor_watertank_" + str(i)):
                        control_sensor_watertank = "checked" 
                    else:
                        control_sensor_watertank = ""                
                    
                    if request.form.get("set_control_sensor_moisture_" + str(i)):
                        control_sensor_moisture = "checked" 
                    else:
                        control_sensor_moisture = ""
                        
                    if request.form.get("set_moisture_" + str(i)) != None:
                        moisture = request.form.get("set_moisture_" + str(i))  
                    else:
                        moisture = "None"                                   

                    SET_PLANT_SETTINGS(i, name, mqtt_device_ieeeAddr, group, pumptime, control_sensor_watertank, control_sensor_moisture, moisture)                       


    error_message_settings = CHECK_WATERING_SETTINGS()

    if mqtt_device_ieeeAddr != "":
        mqtt_device_name = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr).name  

    dropdown_list_mqtt_devices = GET_ALL_MQTT_DEVICES("watering_control")  
    dropdown_list_groups   = [1, 2, 3, 4, 5]
    dropdown_list_pumptime = [30, 60, 90, 120, 150, 180, 210, 240, 270, 300]
    dropdown_list_moisture = ["less", "normal", "much"]
    
    plants_list = GET_ALL_PLANTS()

    return render_template('dashboard_watering.html',
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            dropdown_list_groups=dropdown_list_groups,
                            dropdown_list_pumptime=dropdown_list_pumptime,
                            dropdown_list_moisture=dropdown_list_moisture,
                            plants_list=plants_list,
                            moisture=moisture,
                            mqtt_device_ieeeAddr=mqtt_device_ieeeAddr,
                            mqtt_device_name=mqtt_device_name,
                            error_message_add_plant=error_message_add_plant,   
                            error_message_change_name=error_message_change_name,   
                            error_message_settings=error_message_settings,                                                                                                                                                                                    
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


# change plants position 
@app.route('/dashboard/watering/position/<string:direction>/<int:id>')
@login_required
@permission_required
def change_plants_position(id, direction):
    CHANGE_PLANTS_POSITION(id, direction)
    return redirect(url_for('dashboard_watering'))


# Delete plant
@app.route('/dashboard/watering/delete/<int:id>')
@login_required
@permission_required
def delete_plant(id):
    DELETE_PLANT(id)
    return redirect(url_for('dashboard_watering'))
