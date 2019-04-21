from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps

from app import app
from app.database.database import *
from app.components.checks import CHECK_PLANTS


# access rights
def user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "user" or current_user.role == "superuser":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


""" ############ """
""" sites plants """
""" ############ """

@app.route('/dashboard/plants', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_plants():
    error_message = ""
    error_message_table = ""
    error_message_form = ""
    watervolume = ""
    moisture = ""
    set_mqtt_device_id = ""
    set_mqtt_device_name = ""
    set_watervolume = ""
    set_control_sensor = ""

    if request.method == "POST": 
        if request.form.get("add_plant") != None: 
            
            if request.form.get("set_name") != None:
                # missing name
                if request.form.get("set_name") == "":
                    set_mqtt_device_id = request.form.get("set_mqtt_device_id")    
                    set_watervolume    = request.form.get("set_watervolume")  

                    if request.form.get("set_control_sensor"):
                        set_control_sensor = "checked" 
                    
                    error_message = "Keinen Namen angegeben"  
                                        
                else:         
                    # add plant
                    name           = request.form.get("set_name")
                    mqtt_device_id = request.form.get("set_mqtt_device_id")    
                    watervolume    = request.form.get("set_watervolume") 

                    if request.form.get("set_control_sensor"):
                        control_sensor = "checked" 
                    else:
                        control_sensor = ""

                    error_message  = ADD_PLANT(name, mqtt_device_id, watervolume, control_sensor)
        
        
        # change settings
        if request.form.get("change_settings") != None: 
             
            for i in range (1,25):
                
                if request.form.get("set_sensor_" + str(i)) != None:  

                    # check name
                    if (request.form.get("set_name_" + str(i)) != "" and 
                        GET_PLANT_BY_NAME(request.form.get("set_name_" + str(i))) == None):
                        name = request.form.get("set_name_" + str(i)) 
                        
                    elif request.form.get("set_name_" + str(i)) == GET_PLANT_BY_ID(i).name:
                        name = GET_PLANT_BY_ID(i).name                        
                        
                    else:
                        name = GET_PLANT_BY_ID(i).name 
                        error_message_form = "Ungültige Eingabe (leeres Feld / Name schon vergeben"                        
                                              
                    mqtt_device_id = request.form.get("set_mqtt_device_id_" + str(i))                           

                    if int(mqtt_device_id) == GET_PLANT_BY_ID(i).mqtt_device_id:
 
                        sensor_key = request.form.get("set_sensor_" + str(i))         
                        pump_key = request.form.get("set_pump_" + str(i))                          
                        watervolume = request.form.get("set_watervolume_" + str(i))

                        if request.form.get("set_control_sensor_" + str(i)):
                            control_sensor = "checked" 
                        else:
                            control_sensor = ""
                            
                        SET_PLANT_SETTINGS(i, name, sensor_key, pump_key, watervolume, control_sensor)                       
                        
                    else:                        
                        # reset sensor_key and pump_key if device changes
                        watervolume = GET_PLANT_BY_ID(i).watervolume
                        control_sensor = GET_PLANT_BY_ID(i).control_sensor

                        DELETE_PLANT(i, "No_Log")
                        ADD_PLANT(name, mqtt_device_id, watervolume, control_sensor, "No_Log")

                   
    error_message_table = CHECK_PLANTS()

    if set_mqtt_device_id != "":
        set_mqtt_device_name = GET_MQTT_DEVICE_BY_ID(int(set_mqtt_device_id)).name  
     
    dropdown_list_mqtt_devices = GET_ALL_MQTT_DEVICES("watering")  
    dropdown_list_watervolume = [50, 100, 150, 200, 250, 300]
    plants_list = GET_ALL_PLANTS()

    return render_template('dashboard_plants.html',
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            dropdown_list_watervolume=dropdown_list_watervolume,
                            plants_list=plants_list,
                            moisture=moisture,
                            watervolume=watervolume,
                            set_mqtt_device_id=set_mqtt_device_id,
                            set_mqtt_device_name=set_mqtt_device_name,
                            set_watervolume=set_watervolume,
                            error_message=error_message,
                            error_message_table=error_message_table,
                            error_message_form=error_message_form,
                            role=current_user.role,
                            )


# Delete plant
@app.route('/dashboard/plants/delete/<int:id>')
@login_required
@user_required
def delete_plant(id):
    DELETE_PLANT(id)
    return redirect(url_for('dashboard_plants'))
