from flask import render_template, url_for, request

from app.components.led_control import *
from app.database.database import *


""" ##### """
""" index """
""" ##### """

@app.route('/', methods=['GET', 'POST'])
def index():

    connect_bridge  = False
    program_message = False
    scene = 0
    brightness_global = 100
    error_message = ""

    value_list = ["", "", "", "", "", "", "", "", ""]


    if request.method == "GET":     
        # change scene   
        try:     
            scene = int(request.args.get("radio_scene"))
            brightness_global = request.args.get("brightness_global")
            error_message = LED_SET_SCENE(scene,brightness_global)
            # add radio check
            for i in range (1,12):
                if scene == i:
                    value_list[i-1] = "checked = 'on'"
        except:
            pass

        # select a program   
        try:     
            program = int(request.args.get("radio_program"))
            error_message = START_PROGRAM(program)            
        except:
            pass

    scene_list   = GET_ALL_SCENES()
    program_list = GET_ALL_PROGRAMS()

    return render_template('index.html',
                            scene_list=scene_list,
                            value_list=value_list,                         
                            brightness_global=brightness_global,
                            program_list=program_list,
                            error_message=error_message
                            )

