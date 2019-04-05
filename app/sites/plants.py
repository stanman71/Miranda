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
    watervolume = ""
    moisture = ""

    if request.method == "POST": 
        # add plant
        if request.form.get("add_plant") is not None: 
            if request.form.get("set_name") is not None:
                # controll name 
                if request.form.get("set_name") == "":
                    error_message = "Kein Name angegeben"    
                elif request.form.get("set_mqtt_device") == None:
                    error_message = "Kein MQTT Device vorhanden"                     
                else:         
                    # get informations
                    name          = request.form.get("set_name")
                    mqtt_device   = request.form.get("set_mqtt_device")    
                    watervolume   = request.form.get("set_water_volume") 
                    error_message = ADD_PLANT(name, mqtt_device, watervolume)
        
        # change settings
        if request.form.get("change_settings") is not None: 
            for i in range (1,25):
                # change sensor
                if request.form.get("set_sensor_" + str(i)):
                    sensor_id = request.form.get("set_sensor_" + str(i))    
                    SET_PLANT_SENSOR(i, sensor_id)
                # change pump
                if request.form.get("set_pump_" + str(i)):
                    pump_id = request.form.get("set_pump_" + str(i))    
                    SET_PLANT_PUMP(i, pump_id)                
                # change moisture target
                if request.form.get("set_moisture_" + str(i)):
                    moisture_percent = request.form.get("set_moisture_" + str(i))    
                    SET_PLANT_MOISTURE_TARGET(i, moisture_percent)
                
    dropdown_list_mqtt_devices = GET_ALL_MQTT_DEVICES_SENSOR()  
    dropdown_list_watervolume = [50, 100, 150, 200, 250]
    plants_list = GET_ALL_PLANTS()

    return render_template('dashboard_plants.html',
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            dropdown_list_watervolume=dropdown_list_watervolume,
                            plants_list=plants_list,
                            moisture=moisture,
                            watervolume=watervolume,
                            error_message=error_message,
                            role=current_user.role,
                            )


# Delete plant
@app.route('/dashboard/plants/delete/<int:id>')
@login_required
@user_required
def delete_plant(id):
    DELETE_PLANT(id)
    return redirect(url_for('dashboard_plants'))
