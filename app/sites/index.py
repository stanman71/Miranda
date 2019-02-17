from flask import Flask, render_template, url_for, request
import sys


""" ############# """
""" module import """
""" ############# """

sys.path.insert(0, "./app/components")

from led_control import *
from sensors_control import *


""" ##### """
""" index """
""" ##### """

@app.route('/', methods=['GET', 'POST'])
def index():

    connect_bridge  = False
    program_massage = False
    scene = 0
    brightness_global = 100

    value_list = ["", "", "", "", "", "", "", "", ""]

    # connect to the bridge and an update
    led_update = ""
    led_update = UPDATE_LED(GET_LED_NAMES())

    if request.method == "GET":     
        # change scene   
        try:     
            scene = int(request.args.get("radio_scene"))
            brightness_global = request.args.get("brightness_global")
            LED_SET_SCENE(scene,brightness_global)
            # add radio check
            for i in range (1,10):
                if scene == i:
                    value_list[i-1] = "checked = 'on'"
        except:
            pass

        # select a program   
        try:     
            program = int(request.args.get("radio_program"))
            program_massage = START_PROGRAM(program)            
        except:
            pass

    scene_list   = GET_ALL_SCENES()
    program_list = GET_ALL_PROGRAMS()

    return render_template('index.html', 
                            led_update=led_update,
                            scene_list=scene_list,
                            value_list=value_list,                         
                            brightness_global=brightness_global,
                            program_list=program_list,
                            program_massage=program_massage
                            )

