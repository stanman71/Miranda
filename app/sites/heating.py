from flask import render_template, redirect, url_for, request, Response
from flask_login import login_required, current_user
from functools import wraps

from app import app
from app.database.database import *


# access rights
def permission_required(f):
    @wraps(f)
    def wrap(*args, **kwargs): 
        try:
            if current_user.permission_dashboard == "checked":
                return f(*args, **kwargs)
            else:
                return redirect(url_for('logout'))
        except:
            return redirect(url_for('logout'))
        
    return wrap


""" ############ """
""" site heating """
""" ############ """

@app.route('/heating', methods=['GET', 'POST'])
@login_required
@permission_required
def heating():
    error_message_add_heater = []
    name = ""
    mqtt_device_ieeeAddr = ""

    if request.method == "POST": 
        
        # add heater
        if request.form.get("add_heater") != None: 
            
            if request.form.get("set_name") != None:
                
                # check name
                if request.form.get("set_name") == "":
                    error_message_add_heater.append("Keinen Namen angegeben")
                else:
                    name = request.form.get("set_name")

                # check device
                if request.form.get("set_mqtt_device_ieeeAddr") == "None":
                    error_message_add_heater.append("Kein Gerät angegeben")
                else:
                    mqtt_device_ieeeAddr = request.form.get("set_mqtt_device_ieeeAddr")
                   
                if name != "" and mqtt_device_ieeeAddr != "":
                    
                    error = ADD_HEATER(name, mqtt_device_ieeeAddr)   
                    if error != None: 
                        error_message_add_heater.append(error)
                        
                    name = ""
        
        
    dropdown_list_heater = GET_ALL_MQTT_DEVICES("heater")

    return render_template('heating.html',
                            error_message_add_heater=error_message_add_heater,
                            name=name,
                            dropdown_list_heater=dropdown_list_heater,
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
     