from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps

from app import app
from app.database.database import *


# access rights
def user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "user" or current_user.role == "superuser":
            return f(*args, **kwargs)
        else:
            form = LoginForm()
            return render_template('login.html', form=form, role_check=False)
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
    watervolume = ""
    moisture = ""
    set_mqtt_device_id = ""
    set_mqtt_device_name = ""
    set_watervolume = ""

    if request.method == "POST": 
        if request.form.get("add_plant") != None: 
            
            if request.form.get("set_name") != None:
                # missing name
                if request.form.get("set_name") == "":
                    set_mqtt_device_id = request.form.get("set_mqtt_device_id")    
                    set_watervolume    = request.form.get("set_watervolume")                    
                    
                    error_message = "Keinen Namen angegeben"  
                                        
                else:         
                    # add plant
                    name           = request.form.get("set_name")
                    mqtt_device_id = request.form.get("set_mqtt_device_id")    
                    watervolume    = request.form.get("set_watervolume") 
                    error_message  = ADD_PLANT(name, mqtt_device_id, watervolume)
        
        
        # change settings
        if request.form.get("change_settings") != None:  
            for i in range (1,25):
                if request.form.get("set_sensor_" + str(i)) != None:  

                    mqtt_device_id = request.form.get("set_mqtt_device_id_" + str(i)) 

                    # reset sensor_id and pump_id if device changes
                    if int(mqtt_device_id) != GET_PLANT(i).mqtt_device_id:
     
                        name = GET_PLANT(i).name
                        watervolume = GET_PLANT(i).watervolume
                        moisture_percent = GET_PLANT(i).moisture_percent
                        DELETE_PLANT(i, "No_Log")
                        ADD_PLANT(name, mqtt_device_id, watervolume, "No_Log")

                        plant_id = GET_PLANT_ID(name).id
                        SET_MOISTURE_TARGET(plant_id, moisture_percent)
                    
                    else:
                        # set sensor + pump + watervolume + moisture
                        if request.form.get("set_sensor_" + str(i)) != "None" and request.form.get("set_pump_" + str(i)) != "None":

                            sensor_id = request.form.get("set_sensor_" + str(i))            
                            pump_id = request.form.get("set_pump_" + str(i))    
                            watervolume = request.form.get("set_watervolume_" + str(i))
                            moisture_percent = request.form.get("set_moisture_" + str(i))
                                
                            SET_PLANT_SETTINGS(i, sensor_id, pump_id, watervolume, moisture_percent)

                        # set sensor + watervolume + moisture
                        elif request.form.get("set_sensor_" + str(i)) != "None" and request.form.get("set_pump_" + str(i)) == "None":       

                            sensor_id = request.form.get("set_sensor_" + str(i))
                            watervolume = request.form.get("set_watervolume_" + str(i))
                            moisture_percent = request.form.get("set_moisture_" + str(i))                       
                            SET_PLANT_SETTINGS_WITHOUT_PUMP(i, sensor_id, watervolume, moisture_percent)                    

                        # set pump + watervolume + moisture
                        elif request.form.get("set_sensor_" + str(i)) == "None" and request.form.get("set_pump_" + str(i)) != "None":                 
                
                            pump_id = request.form.get("set_pump_" + str(i)) 
                            watervolume = request.form.get("set_watervolume_" + str(i))
                            moisture_percent = request.form.get("set_moisture_" + str(i))                         
                            SET_PLANT_SETTINGS_WITHOUT_SENSOR(i, pump_id, watervolume, moisture_percent)                
               
                        # set watervolume + moisture    
                        else:
                
                            watervolume = request.form.get("set_watervolume_" + str(i))
                            moisture_percent = request.form.get("set_moisture_" + str(i))                         
                            SET_PLANT_SETTINGS_WITHOUT_SENSOR_AND_PUMP(i, watervolume, moisture_percent) 
                   
    error_message_table = CHECK_PLANTS()

    if set_mqtt_device_id != "":
        set_mqtt_device_name = GET_MQTT_DEVICE_NAME(int(set_mqtt_device_id))   
     
    dropdown_list_mqtt_devices = GET_ALL_MQTT_DEVICES("sensor")  
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
                            role=current_user.role,
                            )


# Delete plant
@app.route('/dashboard/plants/delete/<int:id>')
@login_required
@user_required
def delete_plant(id):
    DELETE_PLANT(id)
    return redirect(url_for('dashboard_plants'))
