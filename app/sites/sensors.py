from flask import Flask, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps

from app import app
from app.components.sensors_control import *
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
""" site sensors """
""" ############ """

@app.route('/dashboard/sensors', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_sensors():
    sensor_values = None
    sensor_name = ""
    sensor_id = ""
    error_massage = ""

    if request.method == "GET": 

        # get sensor values
        if request.args.get("get_sensor") is not None:               
            sensor_id = request.args.get("get_sensor")
            sensor_values = GET_SENSOR_VALUES(sensor_id)
            sensor_name = GET_SENSOR_NAME(sensor_id)

            if sensor_values == None:
                error_massage = "Keine Daten vorhanden"    

        # delete the values of a selected sensor
        if request.args.get("delete_values") is not None:
            delete_values = request.args.get("delete_values") 
            error_massage = DELETE_SENSOR_VALUES(delete_values)
            sensor_name = GET_SENSOR_NAME(delete_values)

    dropdown_list_sensor = GET_ALL_SENSORS()

    return render_template('dashboard_sensors.html',
                            dropdown_list_sensor=dropdown_list_sensor,
                            sensor_values=sensor_values,
                            sensor_name=sensor_name,
                            sensor_id=sensor_id,
                            error_massage=error_massage)


""" #### """
""" MQTT """
""" #### """

# URL for MQTT sensor values
@app.route('/mqtt/<int:id>/sensor/<string:value>', methods=['GET'])
def mqtt_sensor(id, value):   
    SAVE_SENSOR_MQTT(id, value)   
    return ("Daten empfangen")


# URL for MQTT control
@app.route('/mqtt/<int:id>/button/<int:button_id>/<int:value>', methods=['GET'])
def mqtt_button(id, button_id, value):
    pass