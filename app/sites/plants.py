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
    pumptime = ""
    moisture = ""
    set_mqtt_device_id = ""
    set_mqtt_device_name = ""
    set_pumptime = ""
    set_control_sensor = ""

    if request.method == "POST": 
        if request.form.get("add_plant") != None: 
            
            if request.form.get("set_name") != None:
                # missing name
                if request.form.get("set_name") == "":
                    set_mqtt_device_id = request.form.get("set_mqtt_device_id")    
                    set_pumptime    = request.form.get("set_pumptime")  

                    if request.form.get("set_control_sensor"):
                        set_control_sensor = "checked" 
                    
                    error_message = "Keinen Namen angegeben"  
                                        
                else:         
                    # add plant
                    name           = request.form.get("set_name")
                    mqtt_device_id = request.form.get("set_mqtt_device_id")    
                    pumptime    = request.form.get("set_pumptime") 

                    if request.form.get("set_control_sensor"):
                        control_sensor = "checked" 
                    else:
                        control_sensor = ""

                    error_message  = ADD_PLANT(name, mqtt_device_id, pumptime, control_sensor)
        
        
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
                        error_message_form = "Ungültige Eingabe (leeres Feld / Name schon vergeben"                        

                    # other values       
                    mqtt_device_id = request.form.get("set_mqtt_device_id_" + str(i))
                    pump_key       = request.form.get("set_pump_" + str(i))                  
                    sensor_key     = request.form.get("set_sensor_" + str(i))                                
                    pumptime       = request.form.get("set_pumptime_" + str(i))

                    if request.form.get("set_control_sensor_" + str(i)):
                        control_sensor = "checked" 
                    else:
                        control_sensor = ""

                    try:
                        pump_key = pump_key.replace(" ", "") 

                        if pump_key.isdigit():
                            pump_list = GET_MQTT_DEVICE_BY_ID(mqtt_device_id).outputs
                            pump_list = pump_list.split(",")
                            pump_key  = pump_list[int(pump_key)]
                    except:
                        pass

                    try:      
                        sensor_key = sensor_key.replace(" ", "") 
                        
                        if sensor_key.isdigit():
                            sensor_list = GET_MQTT_DEVICE_BY_ID(mqtt_device_id).inputs
                            sensor_list = sensor_list.split(",")
                            sensor_key  = sensor_list[int(sensor_key)]
                    except:
                        pass

                    SET_PLANT_SETTINGS(i, name, mqtt_device_id, pump_key, sensor_key, pumptime, control_sensor)                       

    # get pump list
    try:
        mqtt_device_1_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(1).outputs
        mqtt_device_1_outputs = mqtt_device_1_outputs.replace(" ", "")
    except:
        mqtt_device_1_outputs = ""
    try:
        mqtt_device_2_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(2).outputs
        mqtt_device_2_outputs = mqtt_device_2_outputs.replace(" ", "")
    except:
        mqtt_device_2_outputs = ""
    try:        
        mqtt_device_3_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(3).outputs
        mqtt_device_3_outputs = mqtt_device_3_outputs.replace(" ", "")
    except:
        mqtt_device_3_outputs = ""
    try:        
        mqtt_device_4_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(4).outputs
        mqtt_device_4_outputs = mqtt_device_4_outputs.replace(" ", "")
    except:
        mqtt_device_4_outputs = ""
    try:        
        mqtt_device_5_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(5).outputs
        mqtt_device_5_outputs = mqtt_device_5_outputs.replace(" ", "")
    except:
        mqtt_device_5_outputs = ""
    try:        
        mqtt_device_6_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(6).outputs
        mqtt_device_6_outputs = mqtt_device_6_outputs.replace(" ", "")
    except:
        mqtt_device_6_outputs = ""
    try:        
        mqtt_device_7_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(7).outputs
        mqtt_device_7_outputs = mqtt_device_7_outputs.replace(" ", "")
    except:
        mqtt_device_7_outputs = ""
    try:        
        mqtt_device_8_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(8).outputs
        mqtt_device_8_outputs = mqtt_device_8_outputs.replace(" ", "")
    except:
        mqtt_device_8_outputs = ""
    try:        
        mqtt_device_9_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(9).outputs
        mqtt_device_9_outputs = mqtt_device_9_outputs.replace(" ", "")
    except:
        mqtt_device_9_outputs = ""
    try:        
        mqtt_device_10_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(10).outputs
        mqtt_device_10_outputs = mqtt_device_10_outputs.replace(" ", "")
    except:
        mqtt_device_10_outputs = ""
    try:        
        mqtt_device_11_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(11).outputs
        mqtt_device_11_outputs = mqtt_device_11_outputs.replace(" ", "")
    except:
        mqtt_device_11_outputs = ""
    try:        
        mqtt_device_12_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(12).outputs
        mqtt_device_12_outputs = mqtt_device_12_outputs.replace(" ", "")
    except:
        mqtt_device_12_outputs = ""
    try:        
        mqtt_device_13_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(13).outputs
        mqtt_device_13_outputs = mqtt_device_13_outputs.replace(" ", "")
    except:
        mqtt_device_13_outputs = ""
    try:        
        mqtt_device_14_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(14).outputs
        mqtt_device_14_outputs = mqtt_device_14_outputs.replace(" ", "")
    except:
        mqtt_device_14_outputs = ""
    try:        
        mqtt_device_15_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(15).outputs
        mqtt_device_15_outputs = mqtt_device_15_outputs.replace(" ", "")
    except:
        mqtt_device_15_outputs = ""    
    try:        
        mqtt_device_16_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(16).outputs
        mqtt_device_16_outputs = mqtt_device_16_outputs.replace(" ", "")
    except:
        mqtt_device_16_outputs = ""
    try:        
        mqtt_device_17_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(17).outputs
        mqtt_device_17_outputs = mqtt_device_17_outputs.replace(" ", "")
    except:
        mqtt_device_17_outputs = ""
    try:        
        mqtt_device_18_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(18).outputs
        mqtt_device_18_outputs = mqtt_device_18_outputs.replace(" ", "")
    except:
        mqtt_device_18_outputs = ""
    try:        
        mqtt_device_19_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(19).outputs
        mqtt_device_19_outputs = mqtt_device_19_outputs.replace(" ", "")
    except:
        mqtt_device_19_outputs = ""
    try:        
        mqtt_device_20_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(20).outputs
        mqtt_device_20_outputs = mqtt_device_20_outputs.replace(" ", "")
    except:
        mqtt_device_20_outputs = ""   
    try:        
        mqtt_device_21_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(21).outputs
        mqtt_device_21_outputs = mqtt_device_21_outputs.replace(" ", "")
    except:
        mqtt_device_21_outputs = ""   
    try:        
        mqtt_device_22_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(22).outputs
        mqtt_device_22_outputs = mqtt_device_22_outputs.replace(" ", "")
    except:
        mqtt_device_22_outputs = ""   
    try:        
        mqtt_device_23_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(23).outputs
        mqtt_device_23_outputs = mqtt_device_23_outputs.replace(" ", "")
    except:
        mqtt_device_23_outputs = ""   
    try:        
        mqtt_device_24_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(24).outputs
        mqtt_device_24_outputs = mqtt_device_24_outputs.replace(" ", "")
    except:
        mqtt_device_24_outputs = ""   
    try:        
        mqtt_device_25_outputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(25).outputs
        mqtt_device_25_outputs = mqtt_device_25_outputs.replace(" ", "")
    except:
        mqtt_device_25_outputs = ""    

    # get sensor list
    try:
        mqtt_device_1_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(1).inputs
        mqtt_device_1_inputs = mqtt_device_1_inputs.replace(" ", "")
    except:
        mqtt_device_1_inputs = ""
    try:
        mqtt_device_2_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(2).inputs
        mqtt_device_2_inputs = mqtt_device_2_inputs.replace(" ", "")
    except:
        mqtt_device_2_inputs = ""
    try:        
        mqtt_device_3_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(3).inputs
        mqtt_device_3_inputs = mqtt_device_3_inputs.replace(" ", "")
    except:
        mqtt_device_3_inputs = ""
    try:        
        mqtt_device_4_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(4).inputs
        mqtt_device_4_inputs = mqtt_device_4_inputs.replace(" ", "")
    except:
        mqtt_device_4_inputs = ""
    try:        
        mqtt_device_5_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(5).inputs
        mqtt_device_5_inputs = mqtt_device_5_inputs.replace(" ", "")
    except:
        mqtt_device_5_inputs = ""
    try:        
        mqtt_device_6_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(6).inputs
        mqtt_device_6_inputs = mqtt_device_6_inputs.replace(" ", "")
    except:
        mqtt_device_6_inputs = ""
    try:        
        mqtt_device_7_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(7).inputs
        mqtt_device_7_inputs = mqtt_device_7_inputs.replace(" ", "")
    except:
        mqtt_device_7_inputs = ""
    try:        
        mqtt_device_8_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(8).inputs
        mqtt_device_8_inputs = mqtt_device_8_inputs.replace(" ", "")
    except:
        mqtt_device_8_inputs = ""
    try:        
        mqtt_device_9_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(9).inputs
        mqtt_device_9_inputs = mqtt_device_9_inputs.replace(" ", "")
    except:
        mqtt_device_9_inputs = ""
    try:        
        mqtt_device_10_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(10).inputs
        mqtt_device_10_inputs = mqtt_device_10_inputs.replace(" ", "")
    except:
        mqtt_device_10_inputs = ""
    try:        
        mqtt_device_11_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(11).inputs
        mqtt_device_11_inputs = mqtt_device_11_inputs.replace(" ", "")
    except:
        mqtt_device_11_inputs = ""
    try:        
        mqtt_device_12_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(12).inputs
        mqtt_device_12_inputs = mqtt_device_12_inputs.replace(" ", "")
    except:
        mqtt_device_12_inputs = ""
    try:        
        mqtt_device_13_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(13).inputs
        mqtt_device_13_inputs = mqtt_device_13_inputs.replace(" ", "")
    except:
        mqtt_device_13_inputs = ""
    try:        
        mqtt_device_14_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(14).inputs
        mqtt_device_14_inputs = mqtt_device_14_inputs.replace(" ", "")
    except:
        mqtt_device_14_inputs = ""
    try:        
        mqtt_device_15_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(15).inputs
        mqtt_device_15_inputs = mqtt_device_15_inputs.replace(" ", "")
    except:
        mqtt_device_15_inputs = ""    
    try:        
        mqtt_device_16_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(16).inputs
        mqtt_device_16_inputs = mqtt_device_16_inputs.replace(" ", "")
    except:
        mqtt_device_16_inputs = ""
    try:        
        mqtt_device_17_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(17).inputs
        mqtt_device_17_inputs = mqtt_device_17_inputs.replace(" ", "")
    except:
        mqtt_device_17_inputs = ""
    try:        
        mqtt_device_18_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(18).inputs
        mqtt_device_18_inputs = mqtt_device_18_inputs.replace(" ", "")
    except:
        mqtt_device_18_inputs = ""
    try:        
        mqtt_device_19_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(19).inputs
        mqtt_device_19_inputs = mqtt_device_19_inputs.replace(" ", "")
    except:
        mqtt_device_19_inputs = ""
    try:        
        mqtt_device_20_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(20).inputs
        mqtt_device_20_inputs = mqtt_device_20_inputs.replace(" ", "")
    except:
        mqtt_device_20_inputs = ""   
    try:        
        mqtt_device_21_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(21).inputs
        mqtt_device_21_inputs = mqtt_device_21_inputs.replace(" ", "")
    except:
        mqtt_device_21_inputs = ""   
    try:        
        mqtt_device_22_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(22).inputs
        mqtt_device_22_inputs = mqtt_device_22_inputs.replace(" ", "")
    except:
        mqtt_device_22_inputs = ""   
    try:        
        mqtt_device_23_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(23).inputs
        mqtt_device_23_inputs = mqtt_device_23_inputs.replace(" ", "")
    except:
        mqtt_device_23_inputs = ""   
    try:        
        mqtt_device_24_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(24).inputs
        mqtt_device_24_inputs = mqtt_device_24_inputs.replace(" ", "")
    except:
        mqtt_device_24_inputs = ""   
    try:        
        mqtt_device_25_inputs = "None,--------------------," + GET_MQTT_DEVICE_BY_ID(25).inputs
        mqtt_device_25_inputs = mqtt_device_25_inputs.replace(" ", "")
    except:
        mqtt_device_25_inputs = ""    


    error_message_table = CHECK_PLANTS()

    if set_mqtt_device_id != "":
        set_mqtt_device_name = GET_MQTT_DEVICE_BY_ID(int(set_mqtt_device_id)).name  
     
    dropdown_list_mqtt_devices = GET_ALL_MQTT_DEVICES("watering")  
    dropdown_list_pumptime = [30, 60, 90, 120, 150, 180, 210, 240, 270, 300]
    plants_list = GET_ALL_PLANTS()

    return render_template('dashboard_plants.html',
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            dropdown_list_pumptime=dropdown_list_pumptime,
                            plants_list=plants_list,
                            moisture=moisture,
                            pumptime=pumptime,
                            set_mqtt_device_id=set_mqtt_device_id,
                            set_mqtt_device_name=set_mqtt_device_name,
                            set_pumptime=set_pumptime,
                            error_message=error_message,
                            error_message_table=error_message_table,
                            error_message_form=error_message_form,
                            mqtt_device_1_outputs=mqtt_device_1_outputs,
                            mqtt_device_2_outputs=mqtt_device_2_outputs,
                            mqtt_device_3_outputs=mqtt_device_3_outputs,
                            mqtt_device_4_outputs=mqtt_device_4_outputs,
                            mqtt_device_5_outputs=mqtt_device_5_outputs,
                            mqtt_device_6_outputs=mqtt_device_6_outputs,
                            mqtt_device_7_outputs=mqtt_device_7_outputs,
                            mqtt_device_8_outputs=mqtt_device_8_outputs,
                            mqtt_device_9_outputs=mqtt_device_9_outputs,
                            mqtt_device_10_outputs=mqtt_device_10_outputs,
                            mqtt_device_11_outputs=mqtt_device_11_outputs,
                            mqtt_device_12_outputs=mqtt_device_12_outputs,
                            mqtt_device_13_outputs=mqtt_device_13_outputs,
                            mqtt_device_14_outputs=mqtt_device_14_outputs,
                            mqtt_device_15_outputs=mqtt_device_15_outputs,
                            mqtt_device_16_outputs=mqtt_device_16_outputs,
                            mqtt_device_17_outputs=mqtt_device_17_outputs,
                            mqtt_device_18_outputs=mqtt_device_18_outputs,
                            mqtt_device_19_outputs=mqtt_device_19_outputs,
                            mqtt_device_20_outputs=mqtt_device_20_outputs,  
                            mqtt_device_21_outputs=mqtt_device_21_outputs, 
                            mqtt_device_22_outputs=mqtt_device_22_outputs, 
                            mqtt_device_23_outputs=mqtt_device_23_outputs, 
                            mqtt_device_24_outputs=mqtt_device_24_outputs, 
                            mqtt_device_25_outputs=mqtt_device_25_outputs,                                
                            mqtt_device_1_inputs=mqtt_device_1_inputs,
                            mqtt_device_2_inputs=mqtt_device_2_inputs,
                            mqtt_device_3_inputs=mqtt_device_3_inputs,
                            mqtt_device_4_inputs=mqtt_device_4_inputs,
                            mqtt_device_5_inputs=mqtt_device_5_inputs,
                            mqtt_device_6_inputs=mqtt_device_6_inputs,
                            mqtt_device_7_inputs=mqtt_device_7_inputs,
                            mqtt_device_8_inputs=mqtt_device_8_inputs,
                            mqtt_device_9_inputs=mqtt_device_9_inputs,
                            mqtt_device_10_inputs=mqtt_device_10_inputs,
                            mqtt_device_11_inputs=mqtt_device_11_inputs,
                            mqtt_device_12_inputs=mqtt_device_12_inputs,
                            mqtt_device_13_inputs=mqtt_device_13_inputs,
                            mqtt_device_14_inputs=mqtt_device_14_inputs,
                            mqtt_device_15_inputs=mqtt_device_15_inputs,
                            mqtt_device_16_inputs=mqtt_device_16_inputs,
                            mqtt_device_17_inputs=mqtt_device_17_inputs,
                            mqtt_device_18_inputs=mqtt_device_18_inputs,
                            mqtt_device_19_inputs=mqtt_device_19_inputs,
                            mqtt_device_20_inputs=mqtt_device_20_inputs,   
                            mqtt_device_21_inputs=mqtt_device_21_inputs,    
                            mqtt_device_22_inputs=mqtt_device_22_inputs,    
                            mqtt_device_23_inputs=mqtt_device_23_inputs,    
                            mqtt_device_24_inputs=mqtt_device_24_inputs,    
                            mqtt_device_25_inputs=mqtt_device_25_inputs,                                                                                                                                                                                                
                            role=current_user.role,                     
                            )


# Delete plant
@app.route('/dashboard/plants/delete/<int:id>')
@login_required
@user_required
def delete_plant(id):
    DELETE_PLANT(id)
    return redirect(url_for('dashboard_plants'))
