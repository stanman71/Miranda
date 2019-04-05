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


""" ################ """
""" sites led scenes """
""" ################ """

# led scene 01
@app.route('/dashboard/led/scene_01', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scene_01():
    scene = 1
    error_message = ""

    if request.method == "POST":  
        # change scene name
        if request.form.get("change_settings_name") is not None: 
            name = request.form.get("set_name") 
            if name is not None:
                error_message = SET_SCENE_NAME(scene, name)
        # set RGB color
        if request.form.get("change_settings_color") is not None: 
            rgb_scene  = []
            for i in range(1,10):
                rgb_scene.append(request.form.get(str(scene) + " " + str(i)))
            SET_SCENE_COLOR(scene, rgb_scene)
        # set brightness
        if request.form.get("change_settings_brightness") is not None: 
            brightness = []
            for i in range(1,10):
                brightness.append(request.form.get(str(i)))
            SET_SCENE_BRIGHTNESS(scene, brightness)  
        # add led
        if request.form.get("change_settings_led") is not None: 
            new_led = request.form.get("add_led") 
            ADD_LED(scene, new_led)     
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    # start scene
    error_message = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()
    scene_names_list = GET_ALL_SCENES()

    return render_template('dashboard_led_scenes.html', 
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            scene_names_list=scene_names_list,
                            number=scene,
                            active01="active",
                            error_message=error_message,
                            role=current_user.role,
                            )


# led scene 02
@app.route('/dashboard/led/scene_02', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scene_02():
    scene = 2
    error_message = ""

    if request.method == "POST":  
        # change scene name
        if request.form.get("change_settings_name") is not None: 
            name = request.form.get("set_name") 
            if name is not None:
                error_message = SET_SCENE_NAME(scene, name)
        # set RGB color
        if request.form.get("change_settings_color") is not None: 
            rgb_scene  = []
            for i in range(1,10):
                rgb_scene.append(request.form.get(str(scene) + " " + str(i)))
            SET_SCENE_COLOR(scene, rgb_scene)
        # set brightness
        if request.form.get("change_settings_brightness") is not None: 
            brightness = []
            for i in range(1,10):
                brightness.append(request.form.get(str(i)))
            SET_SCENE_BRIGHTNESS(scene, brightness)  
        # add led
        if request.form.get("change_settings_led") is not None: 
            new_led = request.form.get("add_led") 
            ADD_LED(scene, new_led)     
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    # start scene
    error_message = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()
    scene_names_list = GET_ALL_SCENES()

    return render_template('dashboard_led_scenes.html',
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            scene_names_list=scene_names_list,                            
                            number=scene,
                            active02="active",
                            error_message=error_message,
                            role=current_user.role,
                            )


# led scene 03
@app.route('/dashboard/led/scene_03', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scene_03():
    scene = 3
    error_message = ""

    if request.method == "POST":  
        # change scene name
        if request.form.get("change_settings_name") is not None: 
            name = request.form.get("set_name") 
            if name is not None:
                error_message = SET_SCENE_NAME(scene, name)
        # set RGB color
        if request.form.get("change_settings_color") is not None: 
            rgb_scene  = []
            for i in range(1,10):
                rgb_scene.append(request.form.get(str(scene) + " " + str(i)))
            SET_SCENE_COLOR(scene, rgb_scene)
        # set brightness
        if request.form.get("change_settings_brightness") is not None: 
            brightness = []
            for i in range(1,10):
                brightness.append(request.form.get(str(i)))
            SET_SCENE_BRIGHTNESS(scene, brightness)  
        # add led
        if request.form.get("change_settings_led") is not None: 
            new_led = request.form.get("add_led") 
            ADD_LED(scene, new_led)     
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    # start scene
    error_message = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()
    scene_names_list = GET_ALL_SCENES()

    return render_template('dashboard_led_scenes.html',
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            scene_names_list=scene_names_list,                            
                            number=scene,
                            active03="active",
                            error_message=error_message,
                            role=current_user.role,
                            )


# led scene 04
@app.route('/dashboard/led/scene_04', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scene_04():
    scene = 4
    error_message = ""

    if request.method == "POST":  
        # change scene name
        if request.form.get("change_settings_name") is not None: 
            name = request.form.get("set_name") 
            if name is not None:
                error_message = SET_SCENE_NAME(scene, name)
        # set RGB color
        if request.form.get("change_settings_color") is not None: 
            rgb_scene  = []
            for i in range(1,10):
                rgb_scene.append(request.form.get(str(scene) + " " + str(i)))
            SET_SCENE_COLOR(scene, rgb_scene)
        # set brightness
        if request.form.get("change_settings_brightness") is not None: 
            brightness = []
            for i in range(1,10):
                brightness.append(request.form.get(str(i)))
            SET_SCENE_BRIGHTNESS(scene, brightness)  
        # add led
        if request.form.get("change_settings_led") is not None: 
            new_led = request.form.get("add_led") 
            ADD_LED(scene, new_led)     
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    # start scene
    error_message = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()
    scene_names_list = GET_ALL_SCENES()

    return render_template('dashboard_led_scenes.html',
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            scene_names_list=scene_names_list,                            
                            number=scene,
                            active04="active",
                            error_message=error_message,
                            role=current_user.role,
                            )                            


# led scene 05
@app.route('/dashboard/led/scene_05', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scene_05():
    scene = 5
    error_message = ""

    if request.method == "POST":  
        # change scene name
        if request.form.get("change_settings_name") is not None: 
            name = request.form.get("set_name") 
            if name is not None:
                error_message = SET_SCENE_NAME(scene, name)
        # set RGB color
        if request.form.get("change_settings_color") is not None: 
            rgb_scene  = []
            for i in range(1,10):
                rgb_scene.append(request.form.get(str(scene) + " " + str(i)))
            SET_SCENE_COLOR(scene, rgb_scene)
        # set brightness
        if request.form.get("change_settings_brightness") is not None: 
            brightness = []
            for i in range(1,10):
                brightness.append(request.form.get(str(i)))
            SET_SCENE_BRIGHTNESS(scene, brightness)  
        # add led
        if request.form.get("change_settings_led") is not None: 
            new_led = request.form.get("add_led") 
            ADD_LED(scene, new_led)     
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)
 
    # start scene
    error_message = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()
    scene_names_list = GET_ALL_SCENES()

    return render_template('dashboard_led_scenes.html',
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            scene_names_list=scene_names_list,
                            number=scene,
                            active05="active",
                            error_message=error_message,
                            role=current_user.role,
                            )


# led scene 06 
@app.route('/dashboard/led/scene_06', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scene_06():
    scene = 6
    error_message = ""

    if request.method == "POST":  
        # change scene name
        if request.form.get("change_settings_name") is not None: 
            name = request.form.get("set_name") 
            if name is not None:
                error_message = SET_SCENE_NAME(scene, name)
        # set RGB color
        if request.form.get("change_settings_color") is not None: 
            rgb_scene  = []
            for i in range(1,10):
                rgb_scene.append(request.form.get(str(scene) + " " + str(i)))
            SET_SCENE_COLOR(scene, rgb_scene)
        # set brightness
        if request.form.get("change_settings_brightness") is not None: 
            brightness = []
            for i in range(1,10):
                brightness.append(request.form.get(str(i)))
            SET_SCENE_BRIGHTNESS(scene, brightness)  
        # add led
        if request.form.get("change_settings_led") is not None: 
            new_led = request.form.get("add_led") 
            ADD_LED(scene, new_led)     
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    # start scene
    error_message = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()
    scene_names_list = GET_ALL_SCENES()

    return render_template('dashboard_led_scenes.html',
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            scene_names_list=scene_names_list,
                            number=scene,
                            active06="active",
                            error_message=error_message,
                            role=current_user.role,
                            )


# led scene 07 
@app.route('/dashboard/led/scene_07', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scene_07():
    scene = 7
    error_message = ""

    if request.method == "POST":  
        # change scene name
        if request.form.get("change_settings_name") is not None: 
            name = request.form.get("set_name") 
            if name is not None:
                error_message = SET_SCENE_NAME(scene, name)
        # set RGB color
        if request.form.get("change_settings_color") is not None: 
            rgb_scene  = []
            for i in range(1,10):
                rgb_scene.append(request.form.get(str(scene) + " " + str(i)))
            SET_SCENE_COLOR(scene, rgb_scene)
        # set brightness
        if request.form.get("change_settings_brightness") is not None: 
            brightness = []
            for i in range(1,10):
                brightness.append(request.form.get(str(i)))
            SET_SCENE_BRIGHTNESS(scene, brightness)  
        # add led
        if request.form.get("change_settings_led") is not None: 
            new_led = request.form.get("add_led") 
            ADD_LED(scene, new_led)     
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    # start scene
    error_message = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()
    scene_names_list = GET_ALL_SCENES()

    return render_template('dashboard_led_scenes.html', 
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            scene_names_list=scene_names_list,
                            number=scene,
                            active07="active",
                            error_message=error_message,
                            role=current_user.role,
                            )


# led scene 08
@app.route('/dashboard/led/scene_08', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scene_08():
    scene = 8
    error_message = ""

    if request.method == "POST":  
        # change scene name
        if request.form.get("change_settings_name") is not None: 
            name = request.form.get("set_name") 
            if name is not None:
                error_message = SET_SCENE_NAME(scene, name)
        # set RGB color
        if request.form.get("change_settings_color") is not None: 
            rgb_scene  = []
            for i in range(1,10):
                rgb_scene.append(request.form.get(str(scene) + " " + str(i)))
            SET_SCENE_COLOR(scene, rgb_scene)
        # set brightness
        if request.form.get("change_settings_brightness") is not None: 
            brightness = []
            for i in range(1,10):
                brightness.append(request.form.get(str(i)))
            SET_SCENE_BRIGHTNESS(scene, brightness)  
        # add led
        if request.form.get("change_settings_led") is not None: 
            new_led = request.form.get("add_led") 
            ADD_LED(scene, new_led)     
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    # start scene
    error_message = LED_SET_SCENE(scene)

    entries_scene    = GET_SCENE(scene)[0]
    scene_name       = GET_SCENE(scene)[1]
    dropdown_list    = GET_DROPDOWN_LIST_LED()
    scene_names_list = GET_ALL_SCENES()

    return render_template('dashboard_led_scenes.html', 
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            scene_names_list=scene_names_list,
                            number=scene,
                            active08="active",
                            error_message=error_message,
                            role=current_user.role,
                            )


# led scene 09
@app.route('/dashboard/led/scene_09', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scene_09():
    scene = 9
    error_message = ""

    if request.method == "POST":  
        # change scene name
        if request.form.get("change_settings_name") is not None: 
            name = request.form.get("set_name") 
            if name is not None:
                error_message = SET_SCENE_NAME(scene, name)
        # set RGB color
        if request.form.get("change_settings_color") is not None: 
            rgb_scene  = []
            for i in range(1,10):
                rgb_scene.append(request.form.get(str(scene) + " " + str(i)))
            SET_SCENE_COLOR(scene, rgb_scene)
        # set brightness
        if request.form.get("change_settings_brightness") is not None: 
            brightness = []
            for i in range(1,10):
                brightness.append(request.form.get(str(i)))
            SET_SCENE_BRIGHTNESS(scene, brightness)  
        # add led
        if request.form.get("change_settings_led") is not None: 
            new_led = request.form.get("add_led") 
            ADD_LED(scene, new_led)     
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    # start scene
    error_message = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()
    scene_names_list = GET_ALL_SCENES()

    return render_template('dashboard_led_scenes.html',
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            scene_names_list=scene_names_list,
                            number=scene,
                            active09="active",
                            error_message=error_message,
                            role=current_user.role,
                            )


# led scene 10
@app.route('/dashboard/led/scene_10', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scene_10():
    scene = 10
    error_message = ""

    if request.method == "POST":  
        # change scene name
        if request.form.get("change_settings_name") is not None: 
            name = request.form.get("set_name") 
            if name is not None:
                error_message = SET_SCENE_NAME(scene, name)
        # set RGB color
        if request.form.get("change_settings_color") is not None: 
            rgb_scene  = []
            for i in range(1,10):
                rgb_scene.append(request.form.get(str(scene) + " " + str(i)))
            SET_SCENE_COLOR(scene, rgb_scene)
        # set brightness
        if request.form.get("change_settings_brightness") is not None: 
            brightness = []
            for i in range(1,10):
                brightness.append(request.form.get(str(i)))
            SET_SCENE_BRIGHTNESS(scene, brightness)  
        # add led
        if request.form.get("change_settings_led") is not None: 
            new_led = request.form.get("add_led") 
            ADD_LED(scene, new_led)     
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    # start scene
    error_message = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()
    scene_names_list = GET_ALL_SCENES()

    return render_template('dashboard_led_scenes.html',
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            scene_names_list=scene_names_list,                            
                            number=scene,
                            active10="active",
                            error_message=error_message,
                            role=current_user.role,
                            )


# led scene 99
@app.route('/dashboard/led/scene_99', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_led_scene_99():
    scene = 99
    error_message = ""

    if request.method == "POST":  
        # change scene name
        if request.form.get("change_settings_name") is not None: 
            name = request.form.get("set_name") 
            if name is not None:
                error_message = SET_SCENE_NAME(scene, name)
        # set RGB color
        if request.form.get("change_settings_color") is not None: 
            rgb_scene  = []
            for i in range(1,10):
                rgb_scene.append(request.form.get(str(scene) + " " + str(i)))
            SET_SCENE_COLOR(scene, rgb_scene)
        # set brightness
        if request.form.get("change_settings_brightness") is not None: 
            brightness = []
            for i in range(1,10):
                brightness.append(request.form.get(str(i)))
            SET_SCENE_BRIGHTNESS(scene, brightness)  
        # add led
        if request.form.get("change_settings_led") is not None: 
            new_led = request.form.get("add_led") 
            ADD_LED(scene, new_led)     
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    # start scene
    error_message = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()
    scene_names_list = GET_ALL_SCENES()

    return render_template('dashboard_led_scenes.html',
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            scene_names_list=scene_names_list,
                            number=scene,
                            active99="active",
                            error_message=error_message,
                            role=current_user.role,
                            )


# delete led 
@app.route('/dashboard/led/scene/delete/<int:scene>/<int:id>')
@login_required
@user_required
def delete_led(scene, id): 
    DEL_LED(scene, id)
    if scene == 1:
        return redirect(url_for('dashboard_led_scene_01'))
    if scene == 2:
        return redirect(url_for('dashboard_led_scene_02'))
    if scene == 3:
        return redirect(url_for('dashboard_led_scene_03'))
    if scene == 4:
        return redirect(url_for('dashboard_led_scene_04'))
    if scene == 5:
        return redirect(url_for('dashboard_led_scene_05'))
    if scene == 6:
        return redirect(url_for('dashboard_led_scene_06'))
    if scene == 7:
        return redirect(url_for('dashboard_led_scene_07'))
    if scene == 8:
        return redirect(url_for('dashboard_led_scene_08'))
    if scene == 9:
        return redirect(url_for('dashboard_led_scene_09'))
    if scene == 10:
        return redirect(url_for('dashboard_led_scene_10'))
    if scene == 99:
        return redirect(url_for('dashboard_led_scene_99'))

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
                error_message = NEW_PROGRAM(new_program) 
            else:
                error_message = "Kein Name angegeben" 
    
        if request.form.get("get_program_name") is not None: 
            # get the selected program, remove SUNRISE delete option
            get_Program = request.form.get("get_program_name") 
            if get_Program is not None:
                program = GET_PROGRAM_NAME(get_Program)
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
                    UPDATE_PROGRAM(i, update_Program)
                # start program
                start_Program = request.form.get("start_" + str(i))
                if start_Program is not None:
                    led_update = START_PROGRAM(i)
                # get rgb values
                get_rgb = request.form.get("get_rgb_" + str(i)) 
                if get_rgb is not None:
                    rgb = get_rgb               
                    program = GET_PROGRAM_ID(i)   
                # change program name                    
                program_name = request.form.get("program_name_" + str(i)) 
                if program_name is not None:
                    SET_PROGRAM_NAME(i, program_name)              
                    program = GET_PROGRAM_ID(i)  
                
                program = GET_PROGRAM_ID(i)
                if "SUNRISE" in program.name:
                    program_delete = ""
                else:
                    program_delete = program
                
                
        if request.form.get("delete_program") is not None:     
            # delete the selected program
            delete_Program = request.form.get("delete_program") 
            delete_Program = delete_Program.split(" ")[0]
            DELETE_PROGRAM(delete_Program)     

    dropdown_list = GET_ALL_PROGRAMS()
    scene_names_list = GET_ALL_SCENES()

    return render_template('dashboard_led_programs.html',
                            led_update=led_update,
                            dropdown_list=dropdown_list,
                            program=program,
                            program_delete=program_delete,
                            rgb=rgb,
                            scene_names_list=scene_names_list,
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
