from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from functools import wraps

import sys


""" ############## """
""" module imports """
""" ############## """

sys.path.insert(0, "./app/components")
sys.path.insert(0, "./app/database")


from app import app

from sensors_control import *
from database_control import *
from plants_control import *


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
                name      = request.args.get("name")
                sensor_id = request.args.get("set_sensor")
                pump_id   = request.args.get("set_pump")
                error_massage = ADD_PLANT(name, sensor_id, pump_id)

        for i in range (1,25):
            # change moisture
            if request.args.get("moisture_" + str(i)):
                moisture = request.args.get("moisture_" + str(i))    
                CHANGE_MOISTURE(i, moisture)

            # change water_volume
            if request.args.get("water_" + str(i)):
                water_volume = request.args.get("water_" + str(i))           
                CHANGE_WATER_VOLUME(i, water_volume)

    dropdown_list_sensor = GET_ALL_SENSORS()
    dropdown_list_pump = [0, 1, 2, 3]
    plants_list = GET_ALL_PLANTS()

    return render_template('dashboard_plants.html',
                            dropdown_list_sensor=dropdown_list_sensor,
                            dropdown_list_pump=dropdown_list_pump,
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