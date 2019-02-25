from flask import render_template, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from functools import wraps
import os

from app import app
from app.components.led_control import *
from app.database.database import *


''' CSS PATH '''
# Windows Home
#PATH_CSS = 'C:/Users/stanman/Desktop/Unterlagen/GIT/Python_Projects/SmartHome/app/static/CDNJS/'
# Windows Work
#PATH_CSS = 'C:/Users/mstan/GIT/Python_Projects/SmartHome/app/static/CDNJS/'
# RasPi:
PATH_CSS = '/home/pi/Python/SmartHome/app/static/CDNJS/'


# create role "superuser"
def superuser_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "superuser":
            return f(*args, **kwargs)
        else:
            form = LoginForm()
            return render_template('login.html', form=form, role_check=False)
    return wrap


""" ################ """
""" sites led custom """
""" ################ """

# led scene 01
@app.route('/dashboard/led/scene_01', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_led_scene_01():
    scene = 1
    error_massage = ""

    if request.method == "GET":  
            
        # change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # set RGB color
        rgb_scene  = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))
        SET_SCENE_COLOR(scene, rgb_scene)

        # set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # add led
        add_led = request.args.get("led_scene") 
        if add_led is not None:
            ADD_LED(scene, add_led)
 
    if request.method == "POST": 
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_led_scenes_custom.html', 
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active01="active",
                            error_massage=error_massage
                            )


# led scene 02
@app.route('/dashboard/led/scene_02', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_led_scene_02():
    scene = 2
    error_massage = ""

    if request.method == "GET":  
            
        # change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))  
        SET_SCENE_COLOR(scene, rgb_scene)

        # set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # add led
        add_led = request.args.get("led_scene") 
        if add_led is not None:
            ADD_LED(scene, add_led)
 
    if request.method == "POST": 
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_led_scenes_custom.html',
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active02="active",
                            error_massage=error_massage
                            )


# led scene 03
@app.route('/dashboard/led/scene_03', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_led_scene_03():
    scene = 3
    error_massage = ""

    if request.method == "GET":  
            
        # change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i))) 
        SET_SCENE_COLOR(scene, rgb_scene)

        # set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # add led
        add_led = request.args.get("led_scene") 
        if add_led is not None:
            ADD_LED(scene, add_led)
 
    if request.method == "POST": 
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_led_scenes_custom.html', 
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active03="active",
                            error_massage=error_massage
                            )


# led scene 04
@app.route('/dashboard/led/scene_04', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_led_scene_04():
    scene = 4
    error_massage = ""

    if request.method == "GET":  
            
        # change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))      
        SET_SCENE_COLOR(scene, rgb_scene)

        # set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # add led
        add_led = request.args.get("led_scene") 
        if add_led is not None:
            ADD_LED(scene, add_led)
 
    if request.method == "POST": 
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_led_scenes_custom.html', 
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active04="active",
                            error_massage=error_massage
                            )


# led scene 05
@app.route('/dashboard/led/scene_05', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_led_scene_05():
    scene = 5
    error_massage = ""

    if request.method == "GET":  
            
        # change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))     
        SET_SCENE_COLOR(scene, rgb_scene)

        # set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # add led
        add_led = request.args.get("led_scene") 
        if add_led is not None:
            ADD_LED(scene, add_led)
 

    if request.method == "POST": 
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_led_scenes_custom.html',
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active05="active",
                            error_massage=error_massage
                            )


""" ############# """
""" sites led fix """
""" ############# """

# led scene 06 (north lights)
@app.route('/dashboard/led/scene_06', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_led_scene_06():
    scene = 6
    error_massage = ""

    if request.method == "GET":  
            
        # change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))  
        SET_SCENE_COLOR(scene, rgb_scene)

        # set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # add led
        add_led = request.args.get("led_scene") 
        if add_led is not None:
            ADD_LED(scene, add_led)
 
    if request.method == "POST": 
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_led_scenes_fix.html',
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active06="active",
                            error_massage=error_massage
                            )


# led scene 07 (sunshine)
@app.route('/dashboard/led/scene_07', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_led_scene_07():
    scene = 7
    error_massage = ""

    if request.method == "GET":  
            
        # change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i))) 
        SET_SCENE_COLOR(scene, rgb_scene)

        # set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # add led
        add_led = request.args.get("led_scene") 
        if add_led is not None:
            ADD_LED(scene, add_led)
 
    if request.method == "POST": 
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_led_scenes_fix.html', 
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active07="active",
                            error_massage=error_massage
                            )


# led scene 08
@app.route('/dashboard/led/scene_08', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_led_scene_08():
    scene = 8
    error_massage = ""

    if request.method == "GET":  
            
        # change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))      
        SET_SCENE_COLOR(scene, rgb_scene)

        # set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # add led
        add_led = request.args.get("led_scene") 
        if add_led is not None:
            ADD_LED(scene, add_led)
 
    if request.method == "POST": 
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_led_scenes_fix.html', 
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active08="active",
                            error_massage=error_massage
                            )


# led scene 09
@app.route('/dashboard/led/scene_09', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_led_scene_09():
    scene = 9
    error_massage = ""

    if request.method == "GET":  
            
        # change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))     
        SET_SCENE_COLOR(scene, rgb_scene)

        # set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # add led
        add_led = request.args.get("led_scene") 
        if add_led is not None:
            ADD_LED(scene, add_led)
 

    if request.method == "POST": 
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_led_scenes_fix.html',
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active09="active",
                            error_massage=error_massage
                            )


# led scene 10
@app.route('/dashboard/led/scene_10', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_led_scene_10():
    scene = 10
    error_massage = ""

    if request.method == "GET":  
            
        # change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))     
        SET_SCENE_COLOR(scene, rgb_scene)

        # set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # add led
        add_led = request.args.get("led_scene") 
        if add_led is not None:
            ADD_LED(scene, add_led)
 

    if request.method == "POST": 
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_led_scenes_fix.html',
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active10="active",
                            error_massage=error_massage
                            )


# led scene 99
@app.route('/dashboard/led/scene_99', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_led_scene_99():
    scene = 99
    error_massage = ""

    if request.method == "GET":  
            
        # change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))     
        SET_SCENE_COLOR(scene, rgb_scene)

        # set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # add led
        add_led = request.args.get("led_scene") 
        if add_led is not None:
            ADD_LED(scene, add_led)
 

    if request.method == "POST": 
        # delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_led_scenes_fix.html',
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active99="active",
                            error_massage=error_massage
                            )


# delete led 
@app.route('/dashboard/led/scene/delete/<int:scene>/<int:id>')
@login_required
@superuser_required
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
@superuser_required
def dashboard_led_programs():
    program = ""
    rgb = "rgb(0, 0, 0)"
    led_update = ""
    error_massage = ""
    program_delete = ""

    if request.method == "GET": 
        # create a new program
        new_program = request.args.get("new_program") 
        if new_program is not None and new_program is not "":
            error_massage = NEW_PROGRAM(new_program)

        # get the selected program
        get_Program = request.args.get("get_program") 
        if get_Program is not None:
            program = GET_PROGRAM_NAME(get_Program)
            if "SUNRISE" in program.name:
                program_delete = ""
            else:
                program_delete = program

        # update programs, i = program ID
        for i in range(1,25):
            update_Program = request.args.get("update_" + str(i))
            if update_Program is not None:
                UPDATE_PROGRAM(i, update_Program)

        # start program
        for i in range(1,25):
            start_Program = request.args.get("start_" + str(i))
            if start_Program is not None:
                led_update = START_PROGRAM(i)

        # get rgb values
        for i in range(1,25):
            get_rgb = request.args.get("get_rgb_" + str(i)) 
            if get_rgb is not None:
                rgb = get_rgb               
                program = GET_PROGRAM_ID(i)  

        # rename program
        for i in range(1,25):
            program_name = request.args.get("program_name_" + str(i)) 
            if program_name is not None:
                SET_PROGRAM_NAME(i, program_name)              
                program = GET_PROGRAM_ID(i)  
            
        # delete the selected program
        delete_Program = request.args.get("delete_program") 
        if delete_Program is not None:
            delete_Program = delete_Program.split(" ")[0]
            print(delete_Program)
            DELETE_PROGRAM(delete_Program)              

    dropdown_list        = GET_DROPDOWN_LIST_PROGRAMS()
    dropdown_list_delete = GET_DROPDOWN_LIST_PROGRAMS()

    if "SUNRISE" in dropdown_list_delete:
        dropdown_list_delete.remove("SUNRISE")

    return render_template('dashboard_led_programs.html',
                            led_update=led_update,
                            dropdown_list=dropdown_list,
                            dropdown_list_delete=dropdown_list_delete,
                            program=program,
                            program_delete=program_delete,
                            rgb=rgb,
                            error_massage=error_massage
                            )


# led settings
@app.route('/dashboard/led/settings')
@login_required
@superuser_required
def dashboard_led_settings():
    led_update = "" 

    if request.method == "GET": 
        # change bridge ip
        bridge_ip = request.args.get("bridge_ip") 
        if bridge_ip is not None:
            SET_BRIDGE_IP(bridge_ip)
            led_update = UPDATE_LED(GET_LED_NAMES())    

    led_list = GET_ALL_LEDS()
    ip = GET_BRIDGE_IP()  

    return render_template('dashboard_led_settings.html',
                            led_update=led_update,
                            ip=ip,
                            led_list=led_list
                            )
    

""" ############### """
""" sites file host """
""" ############### """

# Host files for colorpicker_local
@app.route('/get_media/<path:filename>', methods=['GET'])
def get_media(filename):
    return send_from_directory(PATH_CSS, filename)

