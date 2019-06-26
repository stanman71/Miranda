from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps
import os
import re

from app import app
from app.components.process_program import START_PROGRAM_THREAD, STOP_PROGRAM_THREAD, GET_PROGRAM_RUNNING
from app.database.database import *
from app.components.checks import CHECK_PROGRAM


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
    rgb = "(0, 0, 0)"
    led_update = ""
    error_message_add_program = ""
    error_message_content = ""
    
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
            
            if (request.form.get("save_" + str(i)) != None or
                request.form.get("color_" + str(i)) != None or
                request.form.get("start_" + str(i)) != None or
                request.form.get("stop_" + str(i)) != None or
                request.form.get("change_name_" + str(i)) != None):
                    
                    
                # save content
                content = request.form.get("content")
                
                SAVE_PROGRAM(i, content)                 
                       
                       
                # start program
                start_Program = request.form.get("start_" + str(i))
                
                if start_Program != None:  
                    START_PROGRAM_THREAD(i)  

                 
                # stop program    
                if request.form.get("stop_" + str(i)) != None: 
                    STOP_PROGRAM_THREAD() 
                 

                # get rgb values
                get_rgb = request.form.get("get_rgb_" + str(i)) 
                
                if get_rgb != None:
                    rgb = get_rgb   
                    rgb = rgb.replace("rgb", "")            
                    program = GET_PROGRAM_BY_ID(i) 
                    
                    
                # change program name                    
                program_name = request.form.get("program_name_" + str(i)) 
                
                if program_name != None:
                    SET_PROGRAM_NAME(i, program_name)              
                    program = GET_PROGRAM_BY_ID(i)  
                
                 
                # check program settings
                error_message_content = CHECK_PROGRAM(i)    
            
          
                  
            # delete the selected program   
            if request.form.get("delete_program_" + str(i)) != None: 
                DELETE_PROGRAM(i)     
                

    dropdown_list_programs = GET_ALL_PROGRAMS()
    program_running        = GET_PROGRAM_RUNNING()

    return render_template('dashboard_programs.html',
                            led_update=led_update,
                            dropdown_list_programs=dropdown_list_programs,
                            program=program,
                            rgb=rgb,
                            program_running=program_running,
                            error_message_add_program=error_message_add_program,
                            error_message_content=error_message_content,
                            role=current_user.role,
                            )
