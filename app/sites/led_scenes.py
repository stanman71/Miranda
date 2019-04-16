from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps
import os
import re

from app import app
from app.components.led_control import *
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


""" ########## """
""" led scenes """
""" ########## """

# led scenes
@app.route('/dashboard/led/scenes', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scenes():
    error_message = ""
    error_message_table = ""

    if request.method == "POST":
        for i in range (1,25):

            # change scene
            if request.form.get("set_name_" + str(i)) != None:  

                # check name
                if (request.form.get("set_name_" + str(i)) != "" and 
                    GET_LED_SCENE_BY_NAME(request.form.get("set_name_" + str(i))) == None):
                    name = request.form.get("set_name_" + str(i))                    
                elif request.form.get("set_name_" + str(i)) == GET_LED_SCENE_BY_ID(i).name:
                    name = GET_LED_SCENE_BY_ID(i).name                                           
                else:
                    name = GET_LED_SCENE_BY_ID(i).name 
                    error_message_table = "Ungültige Eingabe (leeres Feld / Name schon vergeben"   

                #######
                ## 1 ##
                #######

                # check led 
                try: 
                    led_id_1 = int(request.form.get("set_led_id_1_" + str(i)))

                    if led_id_1 == GET_LED_SCENE_BY_ID(i).led_id_1: 
                        led_name_1 = GET_MQTT_DEVICE_NAME(led_id_1)            
                    elif led_id_1 not in LED_SCENE_LED_EXIST(i):
                        led_name_1 = GET_MQTT_DEVICE_NAME(led_id_1)
                    else:
                        led_id_1   = "None"
                        led_name_1 = "None"
                        error_message_table = "LED bereits verwendet"
                except:
                    led_id_1   = "None"
                    led_name_1 = "None"

                # check rgb
                rgb_1 = request.form.get("set_rgb_1_" + str(i))

                try:
                    rgb_1   = re.findall(r'\d+', rgb_1)
                    red_1   = rgb_1[0]
                    green_1 = rgb_1[1]           
                    blue_1  = rgb_1[2]      
                except:
                    red_1   = 0
                    green_1 = 0
                    blue_1  = 0                      

                # check brightness
                brightness_1 = request.form.get("set_brightness_1_" + str(i))   

                #######
                ## 2 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_led_2 == "on":
 
                    # check led
                    try: 
                        led_id_2 = int(request.form.get("set_led_id_2_" + str(i)))

                        if led_id_2 == GET_LED_SCENE_BY_ID(i).led_id_2: 
                            led_name_2 = GET_MQTT_DEVICE_NAME(led_id_2)            
                        elif led_id_2 not in LED_SCENE_LED_EXIST(i):
                            led_name_2 = GET_MQTT_DEVICE_NAME(led_id_2)
                        else:
                            led_id_2   = "None"
                            led_name_2 = "None"
                            error_message_table = "LED bereits verwendet"
                    except:
                        led_id_2   = "None"
                        led_name_2 = "None"

                    # check rgb
                    rgb_2 = request.form.get("set_rgb_2_" + str(i))

                    try:
                        rgb_2   = re.findall(r'\d+', rgb_2)
                        red_2   = rgb_2[0]
                        green_2 = rgb_2[1]           
                        blue_2  = rgb_2[2]      
                    except:
                        red_2   = 0
                        green_2 = 0
                        blue_2  = 0 

                    # check brightness
                    brightness_2 = request.form.get("set_brightness_2_" + str(i))   

                else:
                    led_id_2 = ""
                    led_name_2 = "None"
                    red_2 = 0
                    green_2 = 0
                    blue_2 = 0
                    brightness_2 = 254

                SET_LED_SCENE(i, name, led_id_1, led_name_1, red_1, green_1, blue_1, brightness_1,
                                       led_id_2, led_name_2, red_2, green_2, blue_2, brightness_2)

            # start scene
            if request.form.get("start_led_scene_" + str(i)) != None: 
                print("Starte: " + str(i))

        # add scene
        if request.form.get("add_led_scene") != None:
            name = request.form.get("set_name") 
            error_message = ADD_LED_SCENE(name)     

    scenes_list = GET_ALL_LED_SCENES()

    dropdown_list_leds = GET_ALL_MQTT_DEVICES("led")

    return render_template('dashboard_led_scenes.html', 
                            scenes_list=scenes_list,
                            error_message=error_message,
                            error_message_table=error_message_table,
                            dropdown_list_leds=dropdown_list_leds,
                            scenes="active",
                            role=current_user.role,
                            )


# add led
@app.route('/dashboard/led/scenes/led/add/<int:scene_id>')
@login_required
@user_required
def add_scene_led(scene_id):
    ADD_LED_SCENE_LED(scene_id)
    return redirect(url_for('dashboard_led_scenes'))


# remove led
@app.route('/dashboard/led/scenes/led/remove/<int:scene_id>/<int:led_id>')
@login_required
@user_required
def remove_scene_led(scene_id, led_id):
    REMOVE_LED_SCENE_LED(scene_id, led_id)
    return redirect(url_for('dashboard_led_scenes'))


# delete scene
@app.route('/dashboard/led/scenes/delete/<int:id>')
@login_required
@user_required
def delete_led_scene(id):
    DELETE_LED_SCENE(id)
    return redirect(url_for('dashboard_led_scenes'))