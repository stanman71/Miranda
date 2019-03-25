from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps

from app import app
from app.database.database import *


# create role "superuser"
def superuser_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "superuser":
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
@superuser_required
def dashboard_plants():
    error_message = ""
    watervolume = ""
    moisture = ""

    if request.method == "GET": 
        if request.args.get("name") is not None:
            # controll name 
            if request.args.get("name") == "":
                error_message = "Kein Name angegeben"    
            elif request.args.get("set_mqtt_device") == None:
                error_message = "Kein MQTT Device vorhanden"                     
            else:         
                # get informations
                name          = request.args.get("name")
                mqtt_device   = request.args.get("set_mqtt_device")    
                watervolume   = request.args.get("set_water_volume") 
                error_message = ADD_PLANT(name, mqtt_device, watervolume)

        for i in range (1,25):
            # change sensor
            if request.args.get("sensor_" + str(i)):
                sensor_id = request.args.get("sensor_" + str(i))    
                SET_PLANT_SENSOR(i, sensor_id)
            # change pump
            if request.args.get("pump_" + str(i)):
                pump_id = request.args.get("pump_" + str(i))    
                SET_PLANT_PUMP(i, pump_id)                
            # change moisture target
            if request.args.get("moisture_" + str(i)):
                moisture_percent = request.args.get("moisture_" + str(i))    
                SET_PLANT_MOISTURE_TARGET(i, moisture_percent)

                
    dropdown_list_mqtt_devices = GET_ALL_MQTT_DEVICES()
    dropdown_list_values       = [0, 1, 2, 3, 4, 5, 6, 7]    
    dropdown_list_watervolume = [50, 100, 150, 200, 250]
    plants_list = GET_ALL_PLANTS()

    return render_template('dashboard_plants.html',
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            dropdown_list_values=dropdown_list_values,
                            dropdown_list_watervolume=dropdown_list_watervolume,
                            plants_list=plants_list,
                            moisture=moisture,
                            watervolume=watervolume,
                            error_message=error_message)


# Delete plant
@app.route('/dashboard/plants/delete/<int:id>')
@login_required
@superuser_required
def delete_plant(id):
    DELETE_PLANT(id)
    return redirect(url_for('dashboard_plants'))
