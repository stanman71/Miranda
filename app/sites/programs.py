from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps

import os
import re
import spotipy

from app import app
from app.components.process_program import START_PROGRAM_THREAD, STOP_PROGRAM_THREAD, GET_PROGRAM_RUNNING
from app.database.database import *
from app.components.checks import CHECK_PROGRAM
from app.components.backend_spotify import GET_SPOTIFY_TOKEN


# access rights
def permission_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.permission_programs == "checked":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('logout'))
    return wrap


""" ######## """
""" programs """
""" ######## """

# programs
@app.route('/dashboard/programs', methods=['GET', 'POST'])
@login_required
@permission_required
def dashboard_programs():
    error_message_add_program  = ""
    error_message_content      = []

    program          = ""
    rgb              = "0, 0, 0"
    led_update       = ""
    collapse_get_rgb = ""  
        
        
    if request.method == 'POST':

        if request.form.get("add_program") != None:  
              
            # add program
            new_program = request.form.get("set_program_name") 

            if new_program != None and new_program != "":
                error_message_add_program = ADD_PROGRAM(new_program) 
            else:
                error_message_add_program = "Kein Name angegeben" 
    
    
        if request.form.get("get_program_name") != None: 
            
            # get the selected program
            get_Program = request.form.get("get_program_name") 
            
            if get_Program != None:
                program = GET_PROGRAM_BY_NAME(get_Program)   
                
                # check program settings
                program_id = program.id
                error_message_content = CHECK_PROGRAM(program_id)            
              
              
        # i = program ID
        for i in range(1,21):  
            
            if (request.form.get("get_rgb_" + str(i)) != None or
                request.form.get("save_" + str(i)) != None or
                request.form.get("start_" + str(i)) != None or
                request.form.get("stop_" + str(i)) != None or
                request.form.get("add_line_" + str(i)) != None or
                request.form.get("remove_line_" + str(i)) != None or
                request.form.get("line_1_down_" + str(i)) != None or
                request.form.get("line_2_up_" + str(i)) != None or
                request.form.get("line_2_down_" + str(i)) != None or
                request.form.get("line_3_up_" + str(i)) != None or 
                request.form.get("line_3_down_" + str(i)) != None or
                request.form.get("line_4_up_" + str(i)) != None or
                request.form.get("line_4_down_" + str(i)) != None or
                request.form.get("line_5_up_" + str(i)) != None or 
                request.form.get("line_5_down_" + str(i)) != None or
                request.form.get("line_6_up_" + str(i)) != None or 
                request.form.get("line_6_down_" + str(i)) != None or                    
                request.form.get("line_7_up_" + str(i)) != None or 
                request.form.get("line_7_down_" + str(i)) != None or                    
                request.form.get("line_8_up_" + str(i)) != None or 
                request.form.get("line_8_down_" + str(i)) != None or                    
                request.form.get("line_9_up_" + str(i)) != None or 
                request.form.get("line_9_down_" + str(i)) != None or                    
                request.form.get("line_10_up_" + str(i)) != None or                 
                request.form.get("change_program_name_" + str(i))):                    
               
               
                # add line
                if request.form.get("add_line_" + str(i)) != None:
                    ADD_PROGRAM_LINE(i)
                   
                   
                # remove line
                if request.form.get("remove_line_" + str(i)) != None:
                    REMOVE_PROGRAM_LINE(i)
                    
                    
                # save settings
                line_content_1    = request.form.get("set_line_content_1_" + str(i))
                line_exception_1  = request.form.get("set_line_exception_1_" + str(i))
                line_content_2    = request.form.get("set_line_content_2_" + str(i))
                line_exception_2  = request.form.get("set_line_exception_2_" + str(i))
                line_content_3    = request.form.get("set_line_content_3_" + str(i))
                line_exception_3  = request.form.get("set_line_exception_3_" + str(i))                
                line_content_4    = request.form.get("set_line_content_4_" + str(i))
                line_exception_4  = request.form.get("set_line_exception_4_" + str(i))                
                line_content_5    = request.form.get("set_line_content_5_" + str(i))
                line_exception_5  = request.form.get("set_line_exception_5_" + str(i))
                line_content_6    = request.form.get("set_line_content_6_" + str(i))
                line_exception_6  = request.form.get("set_line_exception_6_" + str(i))              
                line_content_7    = request.form.get("set_line_content_7_" + str(i))
                line_exception_7  = request.form.get("set_line_exception_7_" + str(i))              
                line_content_8    = request.form.get("set_line_content_8_" + str(i))
                line_exception_8  = request.form.get("set_line_exception_8_" + str(i))              
                line_content_9    = request.form.get("set_line_content_9_" + str(i))
                line_exception_9  = request.form.get("set_line_exception_9_" + str(i))              
                line_content_10   = request.form.get("set_line_content_10_" + str(i))
                line_exception_10 = request.form.get("set_line_exception_10_" + str(i))              
              
                SET_PROGRAM_SETTINGS(i, line_content_1, line_exception_1, line_content_2, line_exception_2, line_content_3, line_exception_3,
                                     line_content_4, line_exception_4, line_content_5, line_exception_5, line_content_6, line_exception_6,
                                     line_content_7, line_exception_7, line_content_8, line_exception_8, line_content_9, line_exception_9,
                                     line_content_10, line_exception_10)
    
    
                # change line position  
                if request.form.get("line_1_down_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 1, "down")
                if request.form.get("line_2_up_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 2, "up")
                if request.form.get("line_2_down_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 2, "down")
                if request.form.get("line_3_up_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 3, "up")
                if request.form.get("line_3_down_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 3, "down")        
                if request.form.get("line_4_up_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 4, "up")
                if request.form.get("line_4_down_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 4, "down")
                if request.form.get("line_5_up_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 5, "up")
                if request.form.get("line_5_down_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 5, "down")
                if request.form.get("line_6_up_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 6, "up")
                if request.form.get("line_6_down_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 6, "down")                    
                if request.form.get("line_7_up_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 7, "up")
                if request.form.get("line_7_down_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 7, "down")  
                if request.form.get("line_8_up_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 8, "up")
                if request.form.get("line_8_down_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 8, "down")   
                if request.form.get("line_9_up_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 9, "up")
                if request.form.get("line_9_down_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 9, "down")   
                if request.form.get("line_10_up_" + str(i)) != None:
                    CHANGE_PROGRAMS_LINE_POSITION(i, 10, "up")
                    
   
                # start program
                if request.form.get("start_" + str(i)) != None: 
                    START_PROGRAM_THREAD(i)  

                 
                # stop program    
                if request.form.get("stop_" + str(i)) != None: 
                    STOP_PROGRAM_THREAD() 
                 

                # get rgb values
                if request.form.get("get_rgb_" + str(i)) != "rgb(0, 0, 0)" and request.form.get("get_rgb_" + str(i)) != None: 
        
                    collapse_get_rgb = "in"        
                
                    get_rgb = request.form.get("get_rgb_" + str(i))
                     
                    rgb = get_rgb   
                    rgb = rgb.replace("rgb", "") 
                    rgb = rgb.replace("(", "") 
                    rgb = rgb.replace(")", "")   
                                                          
                                                          
                # change program name    
                if request.form.get("change_program_name_" + str(i)) != None:  
                    program_name = request.form.get("change_program_name_" + str(i))      
                    SET_PROGRAM_NAME(i, program_name)              
                  

                program = GET_PROGRAM_BY_ID(i)  
                
                # check program settings
                error_message_content = CHECK_PROGRAM(i)    
            
          
                  
            # delete the selected program   
            if request.form.get("delete_program_" + str(i)) != None: 
                DELETE_PROGRAM(i)     
                

    dropdown_list_programs = GET_ALL_PROGRAMS()
    program_running        = GET_PROGRAM_RUNNING()
    
    
    # list device command options   
    list_device_command_options = []
    
    for device in GET_ALL_MQTT_DEVICES("device"):
        list_device_command_options.append((device.name, device.commands))
        
        
    # list sensor options
    list_sensor_options = []
    
    for sensor in GET_ALL_MQTT_DEVICES("sensor"):
        list_sensor_options.append((sensor.name, sensor.input_values))
        

    # list spotify devices / playlists
    spotify_token = GET_SPOTIFY_TOKEN()    
    
    try:
        sp       = spotipy.Spotify(auth=spotify_token)
        sp.trace = False
        
        spotify_devices   = sp.devices()["devices"]        
        spotify_playlists = sp.current_user_playlists(limit=20)["items"]   
        
    except:
        spotify_devices   = ""       
        spotify_playlists = ""   


    return render_template('dashboard_programs.html',
                            led_update=led_update,
                            dropdown_list_programs=dropdown_list_programs,
                            program=program,
                            rgb=rgb,
                            collapse_get_rgb=collapse_get_rgb,
                            program_running=program_running,
                            error_message_add_program=error_message_add_program,
                            error_message_content=error_message_content,
                            spotify_devices=spotify_devices,
                            spotify_playlists=spotify_playlists,   
                            list_device_command_options=list_device_command_options,
                            list_sensor_options=list_sensor_options,
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system, 
                            )
