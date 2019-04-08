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
        if request.form.get("add_plant") is not None: 
            
            if request.form.get("set_name") is not None:
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
        for i in range (1,25):
            if request.form.get("change_settings_" + str(i)) is not None:            
               
               
                if request.form.get("set_sensor") != "None" and request.form.get("set_pump") != "None":
                    # all sensor + pump + watervolume + moisture
                    sensor_id = request.form.get("set_sensor")            
                    pump_id = request.form.get("set_pump")    
                    watervolume = request.form.get("set_watervolume")
                    moisture_percent = request.form.get("set_moisture")
                        
                    SET_PLANT_SETTINGS(i, sensor_id, pump_id, watervolume, moisture_percent)
                 
                elif request.form.get("set_sensor") != "None" and request.form.get("set_pump") == "None":       
                    # set sensor + watervolume + moisture
                    sensor_id = request.form.get("set_sensor")
                    watervolume = request.form.get("set_watervolume")
                    moisture_percent = request.form.get("set_moisture")                       
                    SET_PLANT_SETTINGS_WITHOUT_PUMP(i, sensor_id, watervolume, moisture_percent)                    

                    error_message_table = "Keine Pumpe angegeben"

                elif request.form.get("set_sensor") == "None" and request.form.get("set_pump") != "None":                 
                    # set pump + watervolume + moisture
                    pump_id = request.form.get("set_pump") 
                    watervolume = request.form.get("set_watervolume")
                    moisture_percent = request.form.get("set_moisture")                         
                    SET_PLANT_SETTINGS_WITHOUT_SENSOR(i, pump_id, watervolume, moisture_percent)                

                    error_message_table = "Keinen Sensor angegeben"
                    
                else:
                    # set watervolume + moisture
                    watervolume = request.form.get("set_watervolume")
                    moisture_percent = request.form.get("set_moisture")                         
                    SET_PLANT_SETTINGS_WITHOUT_SENSOR_PUMP(i, watervolume, moisture_percent) 
                    
                    error_message_table = "Keinen Sensor und keine Pumpe angegeben"                 
         
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
