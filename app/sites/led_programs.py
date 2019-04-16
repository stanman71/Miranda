from flask import render_template, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from functools import wraps
import os

from app import app
from app.components.led_control import *
from app.database.database import *
from app.components.file_management import GET_PATH

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
        for i in range(1,25):  
            
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
                    led_update = START_LED_PROGRAM(i)
                # get rgb values
                get_rgb = request.form.get("get_rgb_" + str(i)) 
                if get_rgb is not None:
                    rgb = get_rgb               
                    program = GET_LED_PROGRAM_BY_ID(i)   
                # change program name                    
                program_name = request.form.get("program_name_" + str(i)) 
                if program_name is not None:
                    SET_LED_PROGRAM_NAME(i, program_name)              
                    program = GET_PROGRAM_BY_ID(i)  
                
                program = GET_PROGRAM_BY_ID(i)
                if "SUNRISE" in program.name:
                    program_delete = ""
                else:
                    program_delete = program
                
                
        if request.form.get("delete_program") is not None:     
            # delete the selected program
            delete_Program = request.form.get("delete_program") 
            delete_Program = delete_Program.split(" ")[0]
            DELETE_LED_PROGRAM(delete_Program)     

    dropdown_list = GET_ALL_LED_PROGRAMS()

    return render_template('dashboard_led_programs.html',
                            led_update=led_update,
                            dropdown_list=dropdown_list,
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
