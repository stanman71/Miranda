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
        try:
            if current_user.permission_watering == "checked":
                return f(*args, **kwargs)
            else:
                return redirect(url_for('logout'))
        except Exception as e:
            print(e)
            return redirect(url_for('logout'))
        
    return wrap


""" ############# """
""" site watering """
""" ############# """

@app.route('/watering', methods=['GET', 'POST'])
@login_required
@permission_required
def watering():
    error_message_add_plant = []
    name = ""
    error_message_change_settings = ""
    pumptime = ""
    moisture_level = ""
    mqtt_device_ieeeAddr = ""
    mqtt_device_name     = ""
    control_sensor_moisture = ""
    control_sensor_watertank = ""

    if request.method == "POST": 
        
        # add plant
        if request.form.get("add_plant") != None: 

            # check name
            if request.form.get("set_name") == "":
                error_message_add_plant.append("Keinen Namen angegeben")
            else:
                name = request.form.get("set_name")

            # check device
            if request.form.get("set_mqtt_device_ieeeAddr") == "None":
                error_message_add_plant.append("Kein Gerät angegeben")
            else:
                mqtt_device_ieeeAddr = request.form.get("set_mqtt_device_ieeeAddr")
                mqtt_device_name     = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr).name
               
            if name != "" and mqtt_device_ieeeAddr != "":
                          
                error = ADD_PLANT(name, mqtt_device_ieeeAddr)   
                if error != None: 
                    error_message_add_plant.append(error)                

                name                 = ""
                mqtt_device_ieeeAddr = ""
                mqtt_device_name     = ""
        
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
                        error_message_change_settings = "Ungültige Eingabe (leeres Feld / Name schon vergeben)"                        
    
    
                    mqtt_device = request.form.get("set_mqtt_device_" + str(i))

                    if GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device):
                        mqtt_device_ieeeAddr = mqtt_device
                    elif GET_MQTT_DEVICE_BY_ID(mqtt_device):
                        mqtt_device_ieeeAddr = GET_MQTT_DEVICE_BY_ID(mqtt_device).ieeeAddr
                    else:
                        mqtt_device_ieeeAddr == ""
                    
                    group    = request.form.get("set_group_" + str(i))                                                                       
                    pumptime = request.form.get("set_pumptime_" + str(i))
                    
                    if request.form.get("set_control_sensor_moisture_" + str(i)):
                        control_sensor_moisture = "checked" 
                    else:
                        control_sensor_moisture = ""
                        
                    if request.form.get("set_moisture_level_" + str(i)) != None:
                        moisture_level = request.form.get("set_moisture_level_" + str(i))  
                    else:
                        moisture_level = "None"    
                            
                    if request.form.get("set_control_sensor_watertank_" + str(i)):
                        control_sensor_watertank = "checked" 
                    else:
                        control_sensor_watertank = ""       
                      
                        
                    # set default pumptime_auto value
                    if pumptime == "auto" and (GET_PLANT_PUMPTIME_AUTO(i) == None or GET_PLANT_PUMPTIME_AUTO(i) == "None"):
                        
                        if moisture_level == "less":
                            SET_PLANT_PUMPTIME_AUTO(i, 15)   
                                       
                        elif moisture_level == "normal":
                            SET_PLANT_PUMPTIME_AUTO(i, 30)  
                              
                        elif moisture_level == "much":
                            SET_PLANT_PUMPTIME_AUTO(i, 45)    
                            
                        else:
                            error_message_change_settings = "Auto-Mode nur in Verbindung mit einem Feuchtigkeitssensor"    
                            pumptime = "None"         
                       
                    elif pumptime == "auto":
                        pass
                            
                    else:
                        SET_PLANT_PUMPTIME_AUTO(i, "None") 
                        
                        
                    SET_PLANT_SETTINGS(i, name, mqtt_device_ieeeAddr, group, pumptime, control_sensor_moisture, moisture_level, control_sensor_watertank) 
                    
                    
                    
    error_message_settings = CHECK_WATERING_SETTINGS()

    dropdown_list_watering_controller = GET_ALL_MQTT_DEVICES("watering_controller")  
    dropdown_list_groups              = [1, 2, 3, 4, 5]
    dropdown_list_pumptime            = ["15", "30", "60", "90", "120"]
    dropdown_list_moisture_level      = ["less", "normal", "much"]
    
    list_plants = GET_ALL_PLANTS()

    return render_template('watering.html',
                            dropdown_list_watering_controller=dropdown_list_watering_controller,
                            dropdown_list_groups=dropdown_list_groups,
                            dropdown_list_pumptime=dropdown_list_pumptime,
                            dropdown_list_moisture_level=dropdown_list_moisture_level,
                            name=name,
                            mqtt_device_ieeeAddr=mqtt_device_ieeeAddr,
                            mqtt_device_name=mqtt_device_name,
                            list_plants=list_plants,
                            error_message_add_plant=error_message_add_plant,   
                            error_message_change_settings=error_message_change_settings,   
                            error_message_settings=error_message_settings,                                                                                                                                                                                    
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,
                            permission_heating=current_user.permission_heating,                           
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system,                      
                            )


# change plants position 
@app.route('/watering/position/<string:direction>/<int:id>')
@login_required
@permission_required
def change_plants_position(id, direction):
    CHANGE_PLANTS_POSITION(id, direction)
    return redirect(url_for('watering'))


# Delete plant
@app.route('/watering/delete/<int:id>')
@login_required
@permission_required
def delete_plant(id):
    DELETE_PLANT(id)
    return redirect(url_for('watering'))
