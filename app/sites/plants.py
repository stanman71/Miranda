from flask import Flask, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps

from app import app
from app.components.sensors_control import *
from app.components.plants_control import *
from app.database.database_operations import *


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
    error_massage = ""
    water_volume = ""
    moisture = ""

    if request.method == "GET": 
        if request.args.get("name") is not None:
            # controll name 
            if request.args.get("name") == "":
                error_massage = "Kein Name angegeben"     
            else:         
                # get informations
                name         = request.args.get("name")
                sensor_id    = request.args.get("set_sensor")
                pump_id      = request.args.get("set_pump")
                water_volume = request.args.get("set_water_volume")
                error_massage = ADD_PLANT(name, sensor_id, pump_id, water_volume)

        for i in range (1,25):
            # change moisture
            if request.args.get("moisture_" + str(i)):
                moisture = request.args.get("moisture_" + str(i))    
                CHANGE_MOISTURE(i, moisture)

            # change water_volume
            if request.args.get("water_" + str(i)):
                water_volume = request.args.get("water_" + str(i))           
                CHANGE_WATER_VOLUME(i, water_volume)
                
    dropdown_list_sensor       = GET_ALL_SENSORS()
    dropdown_list_pump         = [0, 1, 2, 3]
    dropdown_list_water_volume = [200, 150, 100, 50]
    plants_list = GET_ALL_PLANTS()

    return render_template('dashboard_plants.html',
                            dropdown_list_sensor=dropdown_list_sensor,
                            dropdown_list_pump=dropdown_list_pump,
                            dropdown_list_water_volume=dropdown_list_water_volume,
                            plants_list=plants_list,
                            moisture=moisture,
                            water_volume=water_volume,
                            error_massage=error_massage)


# Delete plant
@app.route('/dashboard/plants/delete/<int:id>')
@login_required
@superuser_required
def delete_plant(id):
    DELETE_PLANT(id)
    return redirect(url_for('dashboard_plants'))