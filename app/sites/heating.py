from flask import render_template, redirect, url_for, request, Response
from flask_login import login_required, current_user
from functools import wraps

from app import app
from app.database.database import *
from app.components.checks import CHECK_HEATING_SETTINGS


# access rights
def permission_required(f):
    @wraps(f)
    def wrap(*args, **kwargs): 
        try:
            if current_user.permission_heating == "checked":
                return f(*args, **kwargs)
            else:
                return redirect(url_for('logout'))
        except Exception as e:
            print(e)
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
    error_message_change_settings = ""
    error_message_settings = []
    name = ""
    mqtt_device_ieeeAddr = ""
    mqtt_device_name     = ""
    
    RESET_HEATERS_COLLAPSE()
    UPDATE_MQTT_DEVICE_NAMES()    
    

    if request.method == "POST": 
        
        # add heater
        if request.form.get("add_heater") != None: 
            
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
                mqtt_device_name     = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr).name
               
            if name != "" and mqtt_device_ieeeAddr != "":
                
                error = ADD_HEATER(name, mqtt_device_ieeeAddr)   
                if error != None: 
                    error_message_add_heater.append(error)
                    
                name = ""
                mqtt_device_ieeeAddr = ""
                mqtt_device_name     = ""
         
         
        # change settings
        for i in range (1,26):
            
            if request.form.get("set_name_" + str(i)) != None:             

                # check name
                if (request.form.get("set_name_" + str(i)) != "" and 
                    GET_HEATER_BY_NAME(request.form.get("set_name_" + str(i))) == None):
                    name = request.form.get("set_name_" + str(i)) 
                    
                elif request.form.get("set_name_" + str(i)) == GET_HEATER_BY_ID(i).name:
                    name = GET_HEATER_BY_ID(i).name                        
                    
                else:
                    name = GET_HEATER_BY_ID(i).name 
                    error_message_change_settings = "Ungültige Eingabe (leeres Feld / Name schon vergeben)"          

                mqtt_device_ieeeAddr = request.form.get("set_mqtt_device_" + str(i))
                
                window_1_ieeeAddr    = request.form.get("set_window_1_ieeeAddr_" + str(i))
                
                if window_1_ieeeAddr != "None":
                    window_1_name = GET_MQTT_DEVICE_BY_IEEEADDR(window_1_ieeeAddr).name
                else:
                    window_1_name = "None"
                
                window_2_ieeeAddr    = request.form.get("set_window_2_ieeeAddr_" + str(i))
                
                if window_2_ieeeAddr != "None":
                    window_2_name = GET_MQTT_DEVICE_BY_IEEEADDR(window_2_ieeeAddr).name
                else:
                    window_2_name = "None"

                if request.form.get("checkbox_heater_pause_" + str(i)):
                    heater_pause = "checked"
                else:
                    heater_pause = "None"
                    
                try:
                    monday_time_1 = datetime.datetime.strptime(request.form.get("set_monday_time_1_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    monday_time_1 = request.form.get("set_monday_time_1_" + str(i))
                try:                
                    monday_time_2 = datetime.datetime.strptime(request.form.get("set_monday_time_2_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    monday_time_2 = request.form.get("set_monday_time_2_" + str(i))                  
                try:
                    monday_time_3 = datetime.datetime.strptime(request.form.get("set_monday_time_3_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    monday_time_3 = request.form.get("set_monday_time_3_" + str(i))   
                try:                
                    monday_time_4 = datetime.datetime.strptime(request.form.get("set_monday_time_4_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    monday_time_4 = request.form.get("set_monday_time_4_" + str(i))                   
                    
                monday_temperature_1 = request.form.get("set_monday_temperature_1_" + str(i))
                monday_temperature_2 = request.form.get("set_monday_temperature_2_" + str(i))
                monday_temperature_3 = request.form.get("set_monday_temperature_3_" + str(i))
                monday_temperature_4 = request.form.get("set_monday_temperature_4_" + str(i))
                
                try:
                    tuesday_time_1 = datetime.datetime.strptime(request.form.get("set_tuesday_time_1_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    tuesday_time_1 = request.form.get("set_tuesday_time_1_" + str(i))
                try:                
                    tuesday_time_2 = datetime.datetime.strptime(request.form.get("set_tuesday_time_2_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    tuesday_time_2 = request.form.get("set_tuesday_time_2_" + str(i))                  
                try:
                    tuesday_time_3 = datetime.datetime.strptime(request.form.get("set_tuesday_time_3_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    tuesday_time_3 = request.form.get("set_tuesday_time_3_" + str(i))   
                try:                
                    tuesday_time_4 = datetime.datetime.strptime(request.form.get("set_tuesday_time_4_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    tuesday_time_4 = request.form.get("set_tuesday_time_4_" + str(i))                   
                    
                tuesday_temperature_1 = request.form.get("set_tuesday_temperature_1_" + str(i))
                tuesday_temperature_2 = request.form.get("set_tuesday_temperature_2_" + str(i))
                tuesday_temperature_3 = request.form.get("set_tuesday_temperature_3_" + str(i))
                tuesday_temperature_4 = request.form.get("set_tuesday_temperature_4_" + str(i))
                
                try:
                    wednesday_time_1 = datetime.datetime.strptime(request.form.get("set_wednesday_time_1_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    wednesday_time_1 = request.form.get("set_wednesday_time_1_" + str(i))
                try:                
                    wednesday_time_2 = datetime.datetime.strptime(request.form.get("set_wednesday_time_2_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    wednesday_time_2 = request.form.get("set_wednesday_time_2_" + str(i))                  
                try:
                    wednesday_time_3 = datetime.datetime.strptime(request.form.get("set_wednesday_time_3_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    wednesday_time_3 = request.form.get("set_wednesday_time_3_" + str(i))   
                try:                
                    wednesday_time_4 = datetime.datetime.strptime(request.form.get("set_wednesday_time_4_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    wednesday_time_4 = request.form.get("set_wednesday_time_4_" + str(i))                   
                    
                wednesday_temperature_1 = request.form.get("set_wednesday_temperature_1_" + str(i))
                wednesday_temperature_2 = request.form.get("set_wednesday_temperature_2_" + str(i))
                wednesday_temperature_3 = request.form.get("set_wednesday_temperature_3_" + str(i))
                wednesday_temperature_4 = request.form.get("set_wednesday_temperature_4_" + str(i))                
                
                try:
                    thursday_time_1 = datetime.datetime.strptime(request.form.get("set_thursday_time_1_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    thursday_time_1 = request.form.get("set_thursday_time_1_" + str(i))
                try:                
                    thursday_time_2 = datetime.datetime.strptime(request.form.get("set_thursday_time_2_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    thursday_time_2 = request.form.get("set_thursday_time_2_" + str(i))                  
                try:
                    thursday_time_3 = datetime.datetime.strptime(request.form.get("set_thursday_time_3_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    thursday_time_3 = request.form.get("set_thursday_time_3_" + str(i))   
                try:                
                    thursday_time_4 = datetime.datetime.strptime(request.form.get("set_thursday_time_4_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    thursday_time_4 = request.form.get("set_thursday_time_4_" + str(i))                   
                    
                thursday_temperature_1 = request.form.get("set_thursday_temperature_1_" + str(i))
                thursday_temperature_2 = request.form.get("set_thursday_temperature_2_" + str(i))
                thursday_temperature_3 = request.form.get("set_thursday_temperature_3_" + str(i))
                thursday_temperature_4 = request.form.get("set_thursday_temperature_4_" + str(i))    
    
                try:
                    friday_time_1 = datetime.datetime.strptime(request.form.get("set_friday_time_1_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    friday_time_1 = request.form.get("set_friday_time_1_" + str(i))
                try:                
                    friday_time_2 = datetime.datetime.strptime(request.form.get("set_friday_time_2_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    friday_time_2 = request.form.get("set_friday_time_2_" + str(i))                  
                try:
                    friday_time_3 = datetime.datetime.strptime(request.form.get("set_friday_time_3_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    friday_time_3 = request.form.get("set_friday_time_3_" + str(i))   
                try:                
                    friday_time_4 = datetime.datetime.strptime(request.form.get("set_friday_time_4_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    friday_time_4 = request.form.get("set_friday_time_4_" + str(i))                   
                    
                friday_temperature_1 = request.form.get("set_friday_temperature_1_" + str(i))
                friday_temperature_2 = request.form.get("set_friday_temperature_2_" + str(i))
                friday_temperature_3 = request.form.get("set_friday_temperature_3_" + str(i))
                friday_temperature_4 = request.form.get("set_friday_temperature_4_" + str(i))    
    
                try:
                    saturday_time_1 = datetime.datetime.strptime(request.form.get("set_saturday_time_1_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    saturday_time_1 = request.form.get("set_saturday_time_1_" + str(i))
                try:                
                    saturday_time_2 = datetime.datetime.strptime(request.form.get("set_saturday_time_2_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    saturday_time_2 = request.form.get("set_saturday_time_2_" + str(i))                  
                try:
                    saturday_time_3 = datetime.datetime.strptime(request.form.get("set_saturday_time_3_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    saturday_time_3 = request.form.get("set_saturday_time_3_" + str(i))   
                try:                
                    saturday_time_4 = datetime.datetime.strptime(request.form.get("set_saturday_time_4_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    saturday_time_4 = request.form.get("set_saturday_time_4_" + str(i))                   
                    
                saturday_temperature_1 = request.form.get("set_saturday_temperature_1_" + str(i))
                saturday_temperature_2 = request.form.get("set_saturday_temperature_2_" + str(i))
                saturday_temperature_3 = request.form.get("set_saturday_temperature_3_" + str(i))
                saturday_temperature_4 = request.form.get("set_saturday_temperature_4_" + str(i))
                
                try:
                    sunday_time_1 = datetime.datetime.strptime(request.form.get("set_sunday_time_1_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    sunday_time_1 = request.form.get("set_sunday_time_1_" + str(i))
                try:                
                    sunday_time_2 = datetime.datetime.strptime(request.form.get("set_sunday_time_2_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    sunday_time_2 = request.form.get("set_sunday_time_2_" + str(i))                  
                try:
                    sunday_time_3 = datetime.datetime.strptime(request.form.get("set_sunday_time_3_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    sunday_time_3 = request.form.get("set_sunday_time_3_" + str(i))   
                try:                
                    sunday_time_4 = datetime.datetime.strptime(request.form.get("set_sunday_time_4_" + str(i)), "%H:%M").strftime("%H:%M")
                except:
                    sunday_time_4 = request.form.get("set_sunday_time_4_" + str(i))                   
                    
                sunday_temperature_1 = request.form.get("set_sunday_temperature_1_" + str(i))
                sunday_temperature_2 = request.form.get("set_sunday_temperature_2_" + str(i))
                sunday_temperature_3 = request.form.get("set_sunday_temperature_3_" + str(i))
                sunday_temperature_4 = request.form.get("set_sunday_temperature_4_" + str(i))
                
                
                SET_HEATER_SETTINGS(i, name, mqtt_device_ieeeAddr, window_1_ieeeAddr, window_1_name,
                                    window_2_ieeeAddr, window_2_name, heater_pause,
                                    monday_time_1, monday_temperature_1, monday_time_2, monday_temperature_2,
                                    monday_time_3, monday_temperature_3, monday_time_4, monday_temperature_4,
                                    tuesday_time_1, tuesday_temperature_1, tuesday_time_2, tuesday_temperature_2,
                                    tuesday_time_3, tuesday_temperature_3, tuesday_time_4, tuesday_temperature_4,                                    
                                    wednesday_time_1, wednesday_temperature_1, wednesday_time_2, wednesday_temperature_2,
                                    wednesday_time_3, wednesday_temperature_3, wednesday_time_4, wednesday_temperature_4,                                    
                                    thursday_time_1, thursday_temperature_1, thursday_time_2, thursday_temperature_2,
                                    thursday_time_3, thursday_temperature_3, thursday_time_4, thursday_temperature_4,                                    
                                    friday_time_1, friday_temperature_1, friday_time_2, friday_temperature_2,
                                    friday_time_3, friday_temperature_3, friday_time_4, friday_temperature_4,
                                    saturday_time_1, saturday_temperature_1, saturday_time_2, saturday_temperature_2,
                                    saturday_time_3, saturday_temperature_3, saturday_time_4, saturday_temperature_4,                                    
                                    sunday_time_1, sunday_temperature_1, sunday_time_2, sunday_temperature_2,
                                    sunday_time_3, sunday_temperature_3, sunday_time_4, sunday_temperature_4)  


                name = ""
                mqtt_device_ieeeAddr = ""

                SET_HEATER_COLLAPSE(i)
                
                # change option 
                if request.form.get("add_option_monday_" + str(i)) != None:
                    ADD_HEATER_OPTION(i, "monday")
                if request.form.get("remove_option_monday_" + str(i)) != None:
                    REMOVE_HEATER_OPTION(i, "monday")                
                if request.form.get("add_option_tuesday_" + str(i)) != None:
                    ADD_HEATER_OPTION(i, "tuesday")
                if request.form.get("remove_option_tuesday_" + str(i)) != None:
                    REMOVE_HEATER_OPTION(i, "tuesday")         
                if request.form.get("add_option_wednesday_" + str(i)) != None:
                    ADD_HEATER_OPTION(i, "wednesday")
                if request.form.get("remove_option_wednesday_" + str(i)) != None:
                    REMOVE_HEATER_OPTION(i, "wednesday")
                if request.form.get("add_option_thursday_" + str(i)) != None:
                    ADD_HEATER_OPTION(i, "thursday")
                if request.form.get("remove_option_thursday_" + str(i)) != None:
                    REMOVE_HEATER_OPTION(i, "thursday")
                if request.form.get("add_option_friday_" + str(i)) != None:
                    ADD_HEATER_OPTION(i, "friday")
                if request.form.get("remove_option_friday_" + str(i)) != None:
                    REMOVE_HEATER_OPTION(i, "friday")                    
                if request.form.get("add_option_saturday_" + str(i)) != None:
                    ADD_HEATER_OPTION(i, "saturday")
                if request.form.get("remove_option_saturday_" + str(i)) != None:
                    REMOVE_HEATER_OPTION(i, "saturday")
                if request.form.get("add_option_sunday_" + str(i)) != None:
                    ADD_HEATER_OPTION(i, "sunday")
                if request.form.get("remove_option_sunday_" + str(i)) != None:
                    REMOVE_HEATER_OPTION(i, "sunday")    


    dropdown_list_heaters         = GET_ALL_MQTT_DEVICES("heaters")
    dropdown_list_contact_sensors = []

    for sensor in GET_ALL_MQTT_DEVICES("sensors"):
        if sensor.device_type == "sensor_contact":
            sensor.append(dropdown_list_contact_sensors)
    
    list_heaters = GET_ALL_HEATERS()
    
    error_message_settings = CHECK_HEATING_SETTINGS(GET_ALL_HEATERS())

    return render_template('heating.html',
                            error_message_add_heater=error_message_add_heater,
                            error_message_change_settings=error_message_change_settings,
                            error_message_settings=error_message_settings,
                            name=name,
                            mqtt_device_ieeeAddr=mqtt_device_ieeeAddr,
                            mqtt_device_name=mqtt_device_name,                           
                            dropdown_list_heaters=dropdown_list_heaters,
                            dropdown_list_contact_sensors=dropdown_list_contact_sensors,
                            list_heaters=list_heaters,
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
     
     
# change heaters position 
@app.route('/heating/position/<string:direction>/<int:id>')
@login_required
@permission_required
def change_heaters_position(id, direction):
    CHANGE_HEATERS_POSITION(id, direction)
    return redirect(url_for('heating'))


# Delete heater
@app.route('/heating/delete/<int:id>')
@login_required
@permission_required
def delete_heater(id):
    DELETE_HEATER(id)
    return redirect(url_for('heating'))
