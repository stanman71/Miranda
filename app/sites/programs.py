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


""" ######## """
""" programs """
""" ######## """

# programs
@app.route('/dashboard/programs', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_programs():

    """ ### """
    """ led """
    """ ### """

    program = ""
    rgb = "rgb(0, 0, 0)"
    led_update = ""
    error_message_add_program = ""
    
    if request.method == 'POST':

        if request.form.get("add_program") != None:  
              
            # add program
            new_program = request.form.get("set_program_name") 

            print(request.form.get("set_program_name") )

            if new_program != None and new_program != "":
                error_message_add_program = ADD_LED_PROGRAM(new_program) 
            else:
                error_message_add_program = "Kein Name angegeben" 
    
        if request.form.get("get_program_name") != None: 
            
            # get the selected program
            get_Program = request.form.get("get_program_name") 
            if get_Program != None:
                program = GET_LED_PROGRAM_BY_NAME(get_Program)            
              
        # i = program ID
        for i in range(1,21):  
            
            if (request.form.get("save_" + str(i)) != None or
                request.form.get("color_" + str(i)) != None or
                request.form.get("start_" + str(i)) != None or
                request.form.get("change_name_" + str(i)) != None):
                    
                # save content
                content = request.form.get("content")
                SAVE_LED_PROGRAM(i, content)                 
                       
                # start program
                start_Program = request.form.get("start_" + str(i))
                if start_Program != None:  
                    if request.form.get("get_group") != "":   
                        group = request.form.get("get_group")
                        LED_START_PROGRAM_THREAD(int(group), i)  

                # get rgb values
                get_rgb = request.form.get("get_rgb_" + str(i)) 
                if get_rgb != None:
                    rgb = get_rgb               
                    program = GET_LED_PROGRAM_BY_ID(i) 
                    
                # change program name                    
                program_name = request.form.get("program_name_" + str(i)) 
                if program_name != None:
                    SET_LED_PROGRAM_NAME(i, program_name)              
                    program = GET_LED_PROGRAM_BY_ID(i)  
                    
                
            if request.form.get("delete_program_" + str(i)) != None: 
                # delete the selected program
                DELETE_LED_PROGRAM(i)     


    dropdown_list_programs = GET_ALL_LED_PROGRAMS()
    dropdown_list_groups   = GET_ALL_ACTIVE_LED_GROUPS()

    return render_template('dashboard_programs.html',
                            led_update=led_update,
                            dropdown_list_programs=dropdown_list_programs,
                            dropdown_list_groups=dropdown_list_groups,
                            program=program,
                            rgb=rgb,
                            programs="active",
                            error_message_add_program=error_message_add_program,
                            role=current_user.role,
                            )
