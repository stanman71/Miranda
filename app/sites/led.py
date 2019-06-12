from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps
import os
import re

from app import app
from app.components.control_led import *
from app.database.database import *
from app.components.checks import CHECK_LED_GROUP_SETTINGS

# access rights
def user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "user" or current_user.role == "superuser":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


""" ########## """
""" led scenes """
""" ########## """

# led scenes
@app.route('/dashboard/led/scenes', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scenes():
    error_message_add_scene = ""
    error_change_settings = ""
    error_led_control = ""

    for i in range (1,21):
        try:
            RESET_LED_SCENE_ERRORS(i)
        except:
            pass

    if request.method == "POST":

        # add scene
        if request.form.get("add_scene") != None:
            name = request.form.get("set_scene_name") 
            error_message_add_scene = ADD_LED_SCENE(name)     

        for i in range (1,21):

            # change scene
            if request.form.get("set_name_" + str(i)) != None:  


                # ############
                # name setting
                # ############

                led_scene_data = GET_LED_SCENE_BY_ID(i)
                new_name       = request.form.get("set_name_" + str(i))                    

                # add new name
                if ((new_name != "") and (GET_LED_SCENE_BY_NAME(new_name) == None)):
                    name = request.form.get("set_name_" + str(i)) 
                    
                # nothing changed 
                elif new_name == led_scene_data.name:
                    name = led_scene_data.name                        
                    
                # name already exist
                elif ((GET_LED_SCENE_BY_NAME(new_name) != None) and (led_scene_data.name != new_name)):
                    name = led_scene_data.name 
                    error_change_settings = "Name schon vergeben"

                # no input commited
                else:                          
                    name = GET_LED_SCENE_BY_ID(i).name 
                    error_change_settings = "Keinen Namen angegeben"


                #######
                ## 1 ##
                #######

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
                                   
                # check color_temp
                color_temp_1 = request.form.get("set_color_temp_1_" + str(i))  

                # check brightness
                brightness_1 = request.form.get("set_brightness_1_" + str(i))   

                #######
                ## 2 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_2 == "True":
 
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

                    # check color_temp
                    color_temp_2 = request.form.get("set_color_temp_2_" + str(i))  

                    # check brightness
                    brightness_2 = request.form.get("set_brightness_2_" + str(i))   

                else:
                    red_2 = 0
                    green_2 = 0
                    blue_2 = 0
                    color_temp_2 = 0                    
                    brightness_2 = 254

                #######
                ## 3 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_3 == "True":
 
                    # check rgb
                    rgb_3 = request.form.get("set_rgb_3_" + str(i))

                    try:
                        rgb_3   = re.findall(r'\d+', rgb_3)
                        red_3   = rgb_3[0]
                        green_3 = rgb_3[1]           
                        blue_3  = rgb_3[2]      
                    except:
                        red_3   = 0
                        green_3 = 0
                        blue_3  = 0 

                    # check color_temp
                    color_temp_3 = request.form.get("set_color_temp_3_" + str(i))  

                    # check brightness
                    brightness_3 = request.form.get("set_brightness_3_" + str(i))   

                else:
                    red_3 = 0
                    green_3 = 0
                    blue_3 = 0
                    color_temp_3 = 0                    
                    brightness_3 = 254

                #######
                ## 4 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_4 == "True":
 
                    # check rgb
                    rgb_4 = request.form.get("set_rgb_4_" + str(i))

                    try:
                        rgb_4   = re.findall(r'\d+', rgb_4)
                        red_4   = rgb_4[0]
                        green_4 = rgb_4[1]           
                        blue_4  = rgb_4[2]      
                    except:
                        red_4   = 0
                        green_4 = 0
                        blue_4  = 0 

                    # check color_temp
                    color_temp_4 = request.form.get("set_color_temp_4_" + str(i))  

                    # check brightness
                    brightness_4 = request.form.get("set_brightness_4_" + str(i))   

                else:
                    red_4 = 0
                    green_4 = 0
                    blue_4 = 0
                    color_temp_4 = 0                   
                    brightness_4 = 254

                #######
                ## 5 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_5 == "True":
 
                    # check rgb
                    rgb_5 = request.form.get("set_rgb_5_" + str(i))

                    try:
                        rgb_5   = re.findall(r'\d+', rgb_5)
                        red_5   = rgb_5[0]
                        green_5 = rgb_5[1]           
                        blue_5  = rgb_5[2]      
                    except:
                        red_5   = 0
                        green_5 = 0
                        blue_5  = 0 

                    # check color_temp
                    color_temp_5 = request.form.get("set_color_temp_5_" + str(i))  

                    # check brightness
                    brightness_5 = request.form.get("set_brightness_5_" + str(i))   

                else:
                    red_5 = 0
                    green_5 = 0
                    blue_5 = 0
                    color_temp_5 = 0                    
                    brightness_5 = 254

                #######
                ## 6 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_6 == "True":
 
                    # check rgb
                    rgb_6 = request.form.get("set_rgb_6_" + str(i))

                    try:
                        rgb_6   = re.findall(r'\d+', rgb_6)
                        red_6   = rgb_6[0]
                        green_6 = rgb_6[1]           
                        blue_6  = rgb_6[2]      
                    except:
                        red_6   = 0
                        green_6 = 0
                        blue_6  = 0 

                    # check color_temp
                    color_temp_6 = request.form.get("set_color_temp_6_" + str(i))  

                    # check brightness
                    brightness_6 = request.form.get("set_brightness_6_" + str(i))   

                else:
                    red_6 = 0
                    green_6 = 0
                    blue_6 = 0
                    color_temp_6 = 0                   
                    brightness_6 = 254

                #######
                ## 7 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_7 == "True":
 
                    # check rgb
                    rgb_7 = request.form.get("set_rgb_7_" + str(i))

                    try:
                        rgb_7   = re.findall(r'\d+', rgb_7)
                        red_7   = rgb_7[0]
                        green_7 = rgb_7[1]           
                        blue_7  = rgb_7[2]      
                    except:
                        red_7   = 0
                        green_7 = 0
                        blue_7  = 0 

                    # check color_temp
                    color_temp_7 = request.form.get("set_color_temp_7_" + str(i))  

                    # check brightness
                    brightness_7 = request.form.get("set_brightness_7_" + str(i))   

                else:
                    red_7 = 0
                    green_7 = 0
                    blue_7 = 0
                    color_temp_7 = 0                    
                    brightness_7 = 254

                #######
                ## 8 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_8 == "True":
 
                    # check rgb
                    rgb_8 = request.form.get("set_rgb_8_" + str(i))

                    try:
                        rgb_8   = re.findall(r'\d+', rgb_8)
                        red_8   = rgb_8[0]
                        green_8 = rgb_8[1]           
                        blue_8  = rgb_8[2]      
                    except:
                        red_8   = 0
                        green_8 = 0
                        blue_8  = 0 

                    # check color_temp
                    color_temp_8 = request.form.get("set_color_temp_8_" + str(i))  

                    # check brightness
                    brightness_8 = request.form.get("set_brightness_8_" + str(i))   

                else:
                    red_8 = 0
                    green_8 = 0
                    blue_8 = 0
                    color_temp_8 = 0                    
                    brightness_8 = 254

                #######
                ## 9 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_9 == "True":
 
                    # check rgb
                    rgb_9 = request.form.get("set_rgb_9_" + str(i))

                    try:
                        rgb_9   = re.findall(r'\d+', rgb_9)
                        red_9   = rgb_9[0]
                        green_9 = rgb_9[1]           
                        blue_9  = rgb_9[2]      
                    except:
                        red_9   = 0
                        green_9 = 0
                        blue_9  = 0 

                    # check color_temp
                    color_temp_9 = request.form.get("set_color_temp_9_" + str(i))  

                    # check brightness
                    brightness_9 = request.form.get("set_brightness_9_" + str(i))   

                else:
                    red_9 = 0
                    green_9 = 0
                    blue_9 = 0
                    color_temp_9 = 0
                    brightness_9 = 254                                                                                                    

                SET_LED_SCENE_CHANGE_ERRORS(i, error_change_settings)

                SET_LED_SCENE(i, name, red_1, green_1, blue_1, color_temp_1, brightness_1,
                                       red_2, green_2, blue_2, color_temp_2, brightness_2,
                                       red_3, green_3, blue_3, color_temp_3, brightness_3,
                                       red_4, green_4, blue_4, color_temp_4, brightness_4,
                                       red_5, green_5, blue_5, color_temp_5, brightness_5,
                                       red_6, green_6, blue_6, color_temp_6, brightness_6,
                                       red_7, green_7, blue_7, color_temp_7, brightness_7,
                                       red_8, green_8, blue_8, color_temp_8, brightness_8,
                                       red_9, green_9, blue_9, color_temp_9, brightness_9)

            # start scene
            if request.form.get("start_scene_" + str(i)) != None: 
                group = request.form.get("group_" + str(i))
                if group != "" and group != None:
                    error_start_scene = LED_START_SCENE(int(group), i)   
                else:
                    error_led_control = "Keine LED Gruppe ausgewählt" 
                    SET_LED_SCENE_CONTROL_ERRORS(i, error_led_control)


            # turn off group
            if request.form.get("turn_off_group_" + str(i)) != None:
                group = request.form.get("group_" + str(i)) 
                if group != "" and group != None:
                    error_turn_off_scene = LED_TURN_OFF_GROUP(int(group)) 
                else:
                    error_led_control = "Keine LED Gruppe ausgewählt"  
                    SET_LED_SCENE_CONTROL_ERRORS(i, error_led_control)


    scenes_list          = GET_ALL_LED_SCENES()
    dropdown_list_groups = GET_ALL_LED_GROUPS()

    return render_template('dashboard_led_scenes.html', 
                            scenes_list=scenes_list,
                            error_message_add_scene=error_message_add_scene,
                            dropdown_list_groups=dropdown_list_groups,
                            scenes="active",
                            role=current_user.role,
                            )


# change led scene position 
@app.route('/dashboard/led/scenes/position/<string:direction>/<int:id>')
@login_required
@user_required
def change_scene_position(id, direction):
    CHANGE_LED_SCENE_POSITION(id, direction)
    return redirect(url_for('dashboard_led_scenes'))


# add setting
@app.route('/dashboard/led/scenes/setting/add/<int:scene_id>')
@login_required
@user_required
def add_scene_led(scene_id):
    ADD_LED_SCENE_SETTING(scene_id)
    return redirect(url_for('dashboard_led_scenes'))


# remove setting
@app.route('/dashboard/led/scenes/setting/remove/<int:scene_id>/<int:setting>')
@login_required
@user_required
def remove_scene_led(scene_id, setting):
    REMOVE_LED_SCENE_SETTING(scene_id, setting)
    return redirect(url_for('dashboard_led_scenes'))


# delete scene
@app.route('/dashboard/led/scenes/delete/<int:id>')
@login_required
@user_required
def delete_led_scene(id):
    DELETE_LED_SCENE(id)
    return redirect(url_for('dashboard_led_scenes'))


""" ########## """
""" led groups """
""" ########## """

# led groups
@app.route('/dashboard/led/groups', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_groups():
    error_message_add_group = ""

    for i in range (1,21):
        try:
            RESET_LED_GROUP_ERRORS(i)
        except:
            pass

    UPDATE_LED_GROUP_LED_NAMES()

    if request.method == "POST":

        # add group
        if request.form.get("add_group") != None:
            name = request.form.get("set_group_name") 
            error_message_add_group = ADD_LED_GROUP(name)    

        for i in range (1,21):

            # change group
            if request.form.get("set_name_" + str(i)) != None:  

                error_change_settings = ""


                # ############
                # name setting
                # ############

                led_group_data = GET_LED_GROUP_BY_ID(i)
                new_name       = request.form.get("set_name_" + str(i))                    

                # add new name
                if ((new_name != "") and (GET_LED_GROUP_BY_NAME(new_name) == None)):
                    name = request.form.get("set_name_" + str(i)) 
                    
                # nothing changed 
                elif new_name == led_group_data.name:
                    name = led_group_data.name                        
                    
                # name already exist
                elif ((GET_LED_GROUP_BY_NAME(new_name) != None) and (led_group_data.name != new_name)):
                    name = led_group_data.name 
                    error_change_settings = error_change_settings + "Name schon vergeben,"

                # no input commited
                else:                          
                    name = GET_LED_GROUP_BY_ID(i).name 
                    error_change_settings = error_change_settings + "Keinen Namen angegeben,"


                # ###########
                # led setting
                # ###########

                # led exist multiple times ?

                led_list = []

                try: 
                    led_list.append(request.form.get("set_led_ieeeAddr_1_" + str(i)))
                except:
                    pass
                try: 
                    led_list.append(request.form.get("set_led_ieeeAddr_2_" + str(i)))
                except:
                    pass
                try: 
                    led_list.append(request.form.get("set_led_ieeeAddr_3_" + str(i)))
                except:
                    pass
                try: 
                    led_list.append(request.form.get("set_led_ieeeAddr_4_" + str(i)))
                except:
                    pass
                try: 
                    led_list.append(request.form.get("set_led_ieeeAddr_5_" + str(i)))
                except:
                    pass
                try: 
                    led_list.append(request.form.get("set_led_ieeeAddr_6_" + str(i)))
                except:
                    pass
                try: 
                    led_list.append(request.form.get("set_led_ieeeAddr_7_" + str(i)))
                except:
                    pass
                try: 
                    led_list.append(request.form.get("set_led_ieeeAddr_8_" + str(i)))
                except:
                    pass
                try: 
                    led_list.append(request.form.get("set_led_ieeeAddr_9_" + str(i)))
                except:
                    pass

                for led_ieeeAddr in led_list:
                    num = led_list.count(led_ieeeAddr)
                
                    # led exist multiple times
                    if num > 1:

                        if led_ieeeAddr != "None" and led_ieeeAddr != None:

                            if GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr).name not in error_change_settings:
                                error_change_settings = error_change_settings + "LED mehrmals eingetragen >>> " + GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr).name + ","

                            SET_LED_GROUP_CHANGE_ERRORS(i, error_change_settings[:-1])
                            SET_LED_GROUP_NAME(i, name)

                    else:

                        #######
                        ## 1 ##
                        #######

                        try: 
                            led_ieeeAddr_1    = request.form.get("set_led_ieeeAddr_1_" + str(i))
                            led_name_1        = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_1).name   
                            led_device_type_1 = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_1).device_type         

                        except:
                            led_ieeeAddr_1    = "None"
                            led_name_1        = "None"
                            led_device_type_1 = "None"

                        #######
                        ## 2 ##
                        #######

                        try: 
                            led_ieeeAddr_2    = request.form.get("set_led_ieeeAddr_2_" + str(i))
                            led_name_2        = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_2).name   
                            led_device_type_2 = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_2).device_type         

                        except:
                            led_ieeeAddr_2    = "None"
                            led_name_2        = "None"
                            led_device_type_2 = "None"

                        #######
                        ## 3 ##
                        #######

                        try: 
                            led_ieeeAddr_3    = request.form.get("set_led_ieeeAddr_3_" + str(i))
                            led_name_3        = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_3).name   
                            led_device_type_3 = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_3).device_type         

                        except:
                            led_ieeeAddr_3    = "None"
                            led_name_3        = "None"
                            led_device_type_3 = "None"

                        #######
                        ## 4 ##
                        #######

                        try: 
                            led_ieeeAddr_4    = request.form.get("set_led_ieeeAddr_4_" + str(i))
                            led_name_4        = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_4).name   
                            led_device_type_4 = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_4).device_type         

                        except:
                            led_ieeeAddr_4    = "None"
                            led_name_4        = "None"
                            led_device_type_4 = "None"

                        #######
                        ## 5 ##
                        #######

                        try: 
                            led_ieeeAddr_5    = request.form.get("set_led_ieeeAddr_5_" + str(i))
                            led_name_5        = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_5).name   
                            led_device_type_5 = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_5).device_type         

                        except:
                            led_ieeeAddr_5    = "None"
                            led_name_5        = "None"
                            led_device_type_5 = "None"

                        #######
                        ## 6 ##
                        #######

                        try: 
                            led_ieeeAddr_6    = request.form.get("set_led_ieeeAddr_6_" + str(i))
                            led_name_6        = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_6).name   
                            led_device_type_6 = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_6).device_type         

                        except:
                            led_ieeeAddr_6    = "None"
                            led_name_6        = "None"
                            led_device_type_6 = "None"

                        #######
                        ## 7 ##
                        #######

                        try: 
                            led_ieeeAddr_7    = request.form.get("set_led_ieeeAddr_7_" + str(i))
                            led_name_7        = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_7).name   
                            led_device_type_7 = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_7).device_type         

                        except:
                            led_ieeeAddr_7    = "None"
                            led_name_7        = "None"
                            led_device_type_7 = "None"

                        #######
                        ## 8 ##
                        #######

                        try: 
                            led_ieeeAddr_8    = request.form.get("set_led_ieeeAddr_8_" + str(i))
                            led_name_8        = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_8).name   
                            led_device_type_8 = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_8).device_type         

                        except:
                            led_ieeeAddr_8    = "None"
                            led_name_8        = "None"
                            led_device_type_8 = "None"

                        #######
                        ## 9 ##
                        #######

                        try: 
                            led_ieeeAddr_9    = request.form.get("set_led_ieeeAddr_9_" + str(i))
                            led_name_9        = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_9).name   
                            led_device_type_9 = GET_MQTT_DEVICE_BY_IEEEADDR(led_ieeeAddr_9).device_type         

                        except:
                            led_ieeeAddr_9    = "None"
                            led_name_9        = "None"
                            led_device_type_9 = "None"


                        SET_LED_GROUP_CHANGE_ERRORS(i, error_change_settings[:-1])

                        SET_LED_GROUP(i, name, led_ieeeAddr_1, led_name_1, led_device_type_1,
                                               led_ieeeAddr_2, led_name_2, led_device_type_2,
                                               led_ieeeAddr_3, led_name_3, led_device_type_3,
                                               led_ieeeAddr_4, led_name_4, led_device_type_4,
                                               led_ieeeAddr_5, led_name_5, led_device_type_5,
                                               led_ieeeAddr_6, led_name_6, led_device_type_6,
                                               led_ieeeAddr_7, led_name_7, led_device_type_7,
                                               led_ieeeAddr_8, led_name_8, led_device_type_8,
                                               led_ieeeAddr_9, led_name_9, led_device_type_9)
 

    error_message_settings = CHECK_LED_GROUP_SETTINGS(GET_ALL_LED_GROUPS())

    dropdown_list_leds = GET_ALL_MQTT_DEVICES("led")
    list_groups        = GET_ALL_LED_GROUPS()

    return render_template('dashboard_led_groups.html', 
                            error_message_add_group=error_message_add_group,
                            list_groups=list_groups,
                            dropdown_list_leds=dropdown_list_leds,
                            groups="active",
                            role=current_user.role,
                            )


# change led group position 
@app.route('/dashboard/led/groups/position/<string:direction>/<int:id>')
@login_required
@user_required
def change_group_position(id, direction):
    CHANGE_LED_GROUP_POSITION(id, direction)
    return redirect(url_for('dashboard_led_groups'))


# add led
@app.route('/dashboard/led/groups/led/add/<int:group_id>')
@login_required
@user_required
def add_group_led(group_id):
    ADD_LED_GROUP_LED(group_id)
    return redirect(url_for('dashboard_led_groups'))


# remove led
@app.route('/dashboard/led/groups/led/remove/<int:group_id>/<int:led>')
@login_required
@user_required
def remove_group_led(group_id, led):
    REMOVE_LED_GROUP_LED(group_id, led)
    return redirect(url_for('dashboard_led_groups'))


# delete group
@app.route('/dashboard/led/groups/delete/<int:group_id>')
@login_required
@user_required
def delete_led_group(group_id):
    DELETE_LED_GROUP(group_id)
    return redirect(url_for('dashboard_led_groups'))
