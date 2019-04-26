from flask import render_template, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from functools import wraps
import os
import re

from app import app
from app.components.led_control import *
from app.database.database import *
from app.components.file_management import GET_PATH
from app.components.checks import CHECK_LED_GROUP_SETTINGS

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
    error_message_turn_off = ""

    if request.method == "POST":
        for i in range (1,21):

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

                if GET_LED_SCENE_BY_ID(i).active_setting_2 == "on":
 
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
                    red_2 = 0
                    green_2 = 0
                    blue_2 = 0
                    brightness_2 = 254

                #######
                ## 3 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_3 == "on":
 
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

                    # check brightness
                    brightness_3 = request.form.get("set_brightness_3_" + str(i))   

                else:
                    red_3 = 0
                    green_3 = 0
                    blue_3 = 0
                    brightness_3 = 254

                #######
                ## 4 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_4 == "on":
 
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

                    # check brightness
                    brightness_4 = request.form.get("set_brightness_4_" + str(i))   

                else:
                    red_4 = 0
                    green_4 = 0
                    blue_4 = 0
                    brightness_4 = 254

                #######
                ## 5 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_5 == "on":
 
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

                    # check brightness
                    brightness_5 = request.form.get("set_brightness_5_" + str(i))   

                else:
                    red_5 = 0
                    green_5 = 0
                    blue_5 = 0
                    brightness_5 = 254

                #######
                ## 6 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_6 == "on":
 
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

                    # check brightness
                    brightness_6 = request.form.get("set_brightness_6_" + str(i))   

                else:
                    red_6 = 0
                    green_6 = 0
                    blue_6 = 0
                    brightness_6 = 254

                #######
                ## 7 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_7 == "on":
 
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

                    # check brightness
                    brightness_7 = request.form.get("set_brightness_7_" + str(i))   

                else:
                    red_7 = 0
                    green_7 = 0
                    blue_7 = 0
                    brightness_7 = 254

                #######
                ## 8 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_8 == "on":
 
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

                    # check brightness
                    brightness_8 = request.form.get("set_brightness_8_" + str(i))   

                else:
                    red_8 = 0
                    green_8 = 0
                    blue_8 = 0
                    brightness_8 = 254

                #######
                ## 9 ##
                #######

                if GET_LED_SCENE_BY_ID(i).active_setting_9 == "on":
 
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

                    # check brightness
                    brightness_9 = request.form.get("set_brightness_9_" + str(i))   

                else:
                    red_9 = 0
                    green_9 = 0
                    blue_9 = 0
                    brightness_9 = 254                                                                                                    


                SET_LED_SCENE(i, name, red_1, green_1, blue_1, brightness_1,
                                       red_2, green_2, blue_2, brightness_2,
                                       red_3, green_3, blue_3, brightness_3,
                                       red_4, green_4, blue_4, brightness_4,
                                       red_5, green_5, blue_5, brightness_5,
                                       red_6, green_6, blue_6, brightness_6,
                                       red_7, green_7, blue_7, brightness_7,
                                       red_8, green_8, blue_8, brightness_8,
                                       red_9, green_9, blue_9, brightness_9)

            # start scene
            if request.form.get("start_scene_" + str(i)) != None: 
                group = request.form.get("group_" + str(i))
                if group != "":
                    error_message = LED_START_SCENE(int(group), i)   
                else:
                    error_message = ["Keine Gruppe ausgewählt"]  

        # turn off group
        if request.form.get("turn_off_group") != None:
            if request.form.get("get_group") != "":
                group = request.form.get("get_group") 
                error_message_turn_off = LED_TURN_OFF_GROUP(int(group)) 
            else:
                error_message_turn_off = ["Keine Gruppe ausgewählt"]   

        # turn off all led
        if request.form.get("turn_off_all") != None:
            error_message_turn_off = LED_TURN_OFF_ALL()                   

        # add scene
        if request.form.get("add_led_scene") != None:
            name = request.form.get("set_name") 
            error_message = ADD_LED_SCENE(name)     


    scenes_list          = GET_ALL_LED_SCENES()
    dropdown_list_groups = GET_ALL_LED_GROUPS()

    return render_template('dashboard_led_scenes.html', 
                            scenes_list=scenes_list,
                            error_message=error_message,
                            error_message_table=error_message_table,
                            error_message_turn_off=error_message_turn_off,
                            dropdown_list_groups=dropdown_list_groups,
                            scenes="active",
                            role=current_user.role,
                            )


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


""" ############ """
""" led programs """
""" ############ """

# led programs
@app.route('/dashboard/led/programs', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_programs():
    program = ""
    rgb = "rgb(0, 0, 0)"
    led_update = ""
    error_message = ""
    program_delete = ""
    
    if request.method == 'POST':
        if request.form.get("add_program") is not None:    
            # create a new program
            new_program = request.form.get("new_program") 
            if new_program is not None and new_program is not "":
                error_message = ADD_LED_PROGRAM(new_program) 
            else:
                error_message = "Kein Name angegeben" 
    
        if request.form.get("get_program_name") is not None: 
            # get the selected program, remove SUNRISE delete option
            get_Program = request.form.get("get_program_name") 
            if get_Program is not None:
                program = GET_LED_PROGRAM_BY_NAME(get_Program)
                if "SUNRISE" in program.name:
                    program_delete = ""
                else:
                    program_delete = program
                    
        # i = program ID
        for i in range(1,21):  
            
            if (request.form.get("color_" + str(i)) is not None or
                request.form.get("update_" + str(i)) is not None or
                request.form.get("start_" + str(i)) is not None or
                request.form.get("change_name_" + str(i)) is not None):
                    
                # update programs
                update_Program = request.form.get("update_" + str(i))
                if update_Program is not None:
                    UPDATE_LED_PROGRAM(i, update_Program)
                # start program
                start_Program = request.form.get("start_" + str(i))
                if start_Program is not None:   
                    if request.form.get("get_group") != "":   
                        group = request.form.get("get_group")
                        LED_START_PROGRAM_THREAD(int(group), i)  

                # get rgb values
                get_rgb = request.form.get("get_rgb_" + str(i)) 
                if get_rgb is not None:
                    rgb = get_rgb               
                    program = GET_LED_PROGRAM_BY_ID(i)   
                # change program name                    
                program_name = request.form.get("program_name_" + str(i)) 
                if program_name is not None:
                    SET_LED_PROGRAM_NAME(i, program_name)              
                    program = GET_LED_PROGRAM_BY_ID(i)  
                
                program = GET_LED_PROGRAM_BY_ID(i)
                if "SUNRISE" in program.name:
                    program_delete = ""
                else:
                    program_delete = program
                
                
        if request.form.get("delete_program") is not None:     
            # delete the selected program
            delete_Program = request.form.get("delete_program") 
            delete_Program = delete_Program.split(" ")[0]
            DELETE_LED_PROGRAM(delete_Program)     

    dropdown_list_programs = GET_ALL_LED_PROGRAMS()
    dropdown_list_groups   = GET_ALL_LED_GROUPS()

    return render_template('dashboard_led_programs.html',
                            led_update=led_update,
                            dropdown_list_programs=dropdown_list_programs,
                            dropdown_list_groups=dropdown_list_groups,
                            program=program,
                            program_delete=program_delete,
                            rgb=rgb,
                            programs="active",
                            error_message=error_message,
                            role=current_user.role,
                            )


""" ############### """
""" sites file host """
""" ############### """

# Host files for colorpicker_local
@app.route('/get_media/<path:filename>', methods=['GET'])
def get_media(filename):
    if filename is None:
        print(Error(400))
    try:
        PATH_CSS = GET_PATH() + '/app/static/CDNJS/'
        return send_from_directory(PATH_CSS, filename)
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "LED: " + str(e))


""" ########## """
""" led groups """
""" ########## """

# led groups
@app.route('/dashboard/led/groups', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_groups():
    error_message = ""
    error_message_table = ""
    
    UPDATE_LED_GROUP_LED_NAMES()

    if request.method == "POST":
        for i in range (1,21):

            # change group
            if request.form.get("set_name_" + str(i)) != None:  

                # check name
                if (request.form.get("set_name_" + str(i)) != "" and 
                    GET_LED_GROUP_BY_NAME(request.form.get("set_name_" + str(i))) == None):
                    name = request.form.get("set_name_" + str(i))                    
                elif request.form.get("set_name_" + str(i)) == GET_LED_GROUP_BY_ID(i).name:
                    name = GET_LED_GROUP_BY_ID(i).name                                           
                else:
                    name = GET_LED_GROUP_BY_ID(i).name 
                    error_message_table = "Ungültige Eingabe (leeres Feld / Name schon vergeben"   

                #######
                ## 1 ##
                #######

                print(request.form.get("set_led_id_1_" + str(i)))

                # check led 
                try: 
                    led_id_1 = int(request.form.get("set_led_id_1_" + str(i)))

                    if led_id_1 == GET_LED_GROUP_BY_ID(i).led_id_1: 
                        led_name_1 = GET_MQTT_DEVICE_BY_ID(led_id_1).name            
                    elif led_id_1 not in LED_CHECK_EXIST(i):
                        led_name_1 = GET_MQTT_DEVICE_BY_ID(led_id_1).name
                    else:
                        error_message_table = "LED bereits verwendet >>> " + GET_MQTT_DEVICE_BY_ID(led_id_1).name 
                        led_id_1   = "None"
                        led_name_1 = "None"

                except:
                    led_id_1   = "None"
                    led_name_1 = "None"

                #######
                ## 2 ##
                #######

                if GET_LED_GROUP_BY_ID(i).active_led_2 == "on":
 
                    # check led
                    try: 
                        led_id_2 = int(request.form.get("set_led_id_2_" + str(i)))

                        if led_id_2 == GET_LED_GROUP_BY_ID(i).led_id_2: 
                            led_name_2 = GET_MQTT_DEVICE_BY_ID(led_id_2).name            
                        elif led_id_2 not in LED_CHECK_EXIST(i):
                            led_name_2 = GET_MQTT_DEVICE_BY_ID(led_id_2).name
                        else:
                            error_message_table = "LED bereits verwendet >>> " + GET_MQTT_DEVICE_BY_ID(led_id_2).name 
                            led_id_2   = "None"
                            led_name_2 = "None"

                    except:
                        led_id_2   = "None"
                        led_name_2 = "None"

                else:
                    led_id_2 = ""
                    led_name_2 = "None"

                #######
                ## 3 ##
                #######

                if GET_LED_GROUP_BY_ID(i).active_led_3 == "on":
 
                    # check led
                    try: 
                        led_id_3 = int(request.form.get("set_led_id_3_" + str(i)))

                        if led_id_3 == GET_LED_GROUP_BY_ID(i).led_id_3: 
                            led_name_3 = GET_MQTT_DEVICE_BY_ID(led_id_3).name            
                        elif led_id_3 not in LED_CHECK_EXIST(i):
                            led_name_3 = GET_MQTT_DEVICE_BY_ID(led_id_3).name
                        else:
                            error_message_table = "LED bereits verwendet >>> " + GET_MQTT_DEVICE_BY_ID(led_id_3).name 
                            led_id_3   = "None"
                            led_name_3 = "None"

                    except:
                        led_id_3   = "None"
                        led_name_3 = "None"

                else:
                    led_id_3 = ""
                    led_name_3 = "None"

                #######
                ## 4 ##
                #######

                if GET_LED_GROUP_BY_ID(i).active_led_4 == "on":
 
                    # check led
                    try: 
                        led_id_4 = int(request.form.get("set_led_id_4_" + str(i)))

                        if led_id_4 == GET_LED_GROUP_BY_ID(i).led_id_4: 
                            led_name_4 = GET_MQTT_DEVICE_BY_ID(led_id_4).name            
                        elif led_id_4 not in LED_CHECK_EXIST(i):
                            led_name_4 = GET_MQTT_DEVICE_BY_ID(led_id_4).name
                        else:
                            error_message_table = "LED bereits verwendet >>> " + GET_MQTT_DEVICE_BY_ID(led_id_4).name 
                            led_id_4   = "None"
                            led_name_4 = "None"

                    except:
                        led_id_4   = "None"
                        led_name_4 = "None"

                else:
                    led_id_4 = ""
                    led_name_4 = "None"

                #######
                ## 5 ##
                #######

                if GET_LED_GROUP_BY_ID(i).active_led_5 == "on":
 
                    # check led
                    try: 
                        led_id_5 = int(request.form.get("set_led_id_5_" + str(i)))

                        if led_id_5 == GET_LED_GROUP_BY_ID(i).led_id_5: 
                            led_name_5 = GET_MQTT_DEVICE_BY_ID(led_id_5).name            
                        elif led_id_5 not in LED_CHECK_EXIST(i):
                            led_name_5 = GET_MQTT_DEVICE_BY_ID(led_id_5).name
                        else:
                            error_message_table = "LED bereits verwendet >>> " + GET_MQTT_DEVICE_BY_ID(led_id_5).name 
                            led_id_5   = "None"
                            led_name_5 = "None"

                    except:
                        led_id_5   = "None"
                        led_name_5 = "None"

                else:
                    led_id_5 = ""
                    led_name_5 = "None"

                #######
                ## 6 ##
                #######

                if GET_LED_GROUP_BY_ID(i).active_led_6 == "on":
 
                    # check led
                    try: 
                        led_id_6 = int(request.form.get("set_led_id_6_" + str(i)))

                        if led_id_6 == GET_LED_GROUP_BY_ID(i).led_id_6: 
                            led_name_6 = GET_MQTT_DEVICE_BY_ID(led_id_6).name            
                        elif led_id_6 not in LED_CHECK_EXIST(i):
                            led_name_6 = GET_MQTT_DEVICE_BY_ID(led_id_6).name
                        else:
                            error_message_table = "LED bereits verwendet >>> " + GET_MQTT_DEVICE_BY_ID(led_id_6).name 
                            led_id_6   = "None"
                            led_name_6 = "None"

                    except:
                        led_id_6   = "None"
                        led_name_6 = "None"

                else:
                    led_id_6 = ""
                    led_name_6 = "None"

                #######
                ## 7 ##
                #######

                if GET_LED_GROUP_BY_ID(i).active_led_7 == "on":
 
                    # check led
                    try: 
                        led_id_7 = int(request.form.get("set_led_id_7_" + str(i)))

                        if led_id_7 == GET_LED_GROUP_BY_ID(i).led_id_7: 
                            led_name_7 = GET_MQTT_DEVICE_BY_ID(led_id_7).name            
                        elif led_id_7 not in LED_CHECK_EXIST(i):
                            led_name_7 = GET_MQTT_DEVICE_BY_ID(led_id_7).name
                        else:
                            error_message_table = "LED bereits verwendet >>> " + GET_MQTT_DEVICE_BY_ID(led_id_7).name 
                            led_id_7   = "None"
                            led_name_7 = "None"

                    except:
                        led_id_7   = "None"
                        led_name_7 = "None"

                else:
                    led_id_7 = ""
                    led_name_7 = "None"

                #######
                ## 8 ##
                #######

                if GET_LED_GROUP_BY_ID(i).active_led_8 == "on":
 
                    # check led
                    try: 
                        led_id_8 = int(request.form.get("set_led_id_8_" + str(i)))

                        if led_id_8 == GET_LED_GROUP_BY_ID(i).led_id_8: 
                            led_name_8 = GET_MQTT_DEVICE_BY_ID(led_id_8).name            
                        elif led_id_8 not in LED_CHECK_EXIST(i):
                            led_name_8 = GET_MQTT_DEVICE_BY_ID(led_id_8).name
                        else:
                            error_message_table = "LED bereits verwendet >>> " + GET_MQTT_DEVICE_BY_ID(led_id_8).name 
                            led_id_8   = "None"
                            led_name_8 = "None"

                    except:
                        led_id_8   = "None"
                        led_name_8 = "None"

                else:
                    led_id_8 = ""
                    led_name_8 = "None"

                #######
                ## 9 ##
                #######

                if GET_LED_GROUP_BY_ID(i).active_led_9 == "on":
 
                    # check led
                    try: 
                        led_id_9 = int(request.form.get("set_led_id_9_" + str(i)))

                        if led_id_9 == GET_LED_GROUP_BY_ID(i).led_id_9: 
                            led_name_9 = GET_MQTT_DEVICE_BY_ID(led_id_9).name            
                        elif led_id_9 not in LED_CHECK_EXIST(i):
                            led_name_9 = GET_MQTT_DEVICE_BY_ID(led_id_9).name
                        else:
                            error_message_table = "LED bereits verwendet >>> " + GET_MQTT_DEVICE_BY_ID(led_id_9).name 
                            led_id_9   = "None"
                            led_name_9 = "None"

                    except:
                        led_id_9   = "None"
                        led_name_9 = "None"

                else:
                    led_id_9 = ""
                    led_name_9 = "None"

                SET_LED_GROUP(i, name, led_id_1, led_name_1,
                                       led_id_2, led_name_2,
                                       led_id_3, led_name_3,
                                       led_id_4, led_name_4,
                                       led_id_5, led_name_5,
                                       led_id_6, led_name_6,
                                       led_id_7, led_name_7,
                                       led_id_8, led_name_8,
                                       led_id_9, led_name_9)

        # add group
        if request.form.get("add_group") != None:
            name = request.form.get("set_name") 
            error_message = ADD_LED_GROUP(name)     

    error_message_settings = CHECK_LED_GROUP_SETTINGS(GET_ALL_LED_GROUPS())

    dropdown_list_leds = GET_ALL_MQTT_DEVICES("led")
    list_groups = GET_ALL_LED_GROUPS()

    return render_template('dashboard_led_groups.html', 
                            error_message=error_message,
                            error_message_table=error_message_table,
                            error_message_settings=error_message_settings,
                            list_groups=list_groups,
                            dropdown_list_leds=dropdown_list_leds,
                            groups="active",
                            role=current_user.role,
                            )


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
