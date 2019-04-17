import math
import re
import time
import json

from app import app
from app.database.database import *
from app.components.phue import Bridge
from app.components.mqtt import MQTT_PUBLISH


""" ################# """
""" support functions """
""" ################# """

# This is based on original code from http://stackoverflow.com/a/22649803

def EnhanceColor(normalized):
    if normalized > 0.04045:
        return math.pow( (normalized + 0.055) / (1.0 + 0.055), 2.4)
    else:
        return normalized / 12.92


def RGBtoXY(r, g, b):
    rNorm = r / 255.0
    gNorm = g / 255.0
    bNorm = b / 255.0

    rFinal = EnhanceColor(rNorm)
    gFinal = EnhanceColor(gNorm)
    bFinal = EnhanceColor(bNorm)
    
    X = rFinal * 0.649926 + gFinal * 0.103455 + bFinal * 0.197109
    Y = rFinal * 0.234327 + gFinal * 0.743075 + bFinal * 0.022598
    Z = rFinal * 0.000000 + gFinal * 0.053077 + bFinal * 1.035763

    if X + Y + Z == 0:
        return (0,0)
    else:
        xFinal = X / (X + Y + Z)
        yFinal = Y / (X + Y + Z)
    
    return (xFinal, yFinal)


""" ############# """
""" led functions """
""" ############# """

def LED_START_SCENE(group_id, scene_id, brightness_global = 100):

    if GET_SETTING_VALUE("zigbee") == "True":

        try:
            group = GET_LED_GROUP_BY_ID(group_id)
            scene = GET_LED_SCENE_BY_ID(scene_id)

            # led 1
            channel = "SmartHome/zigbee/" + group.led_name_1 + "/set"
            msg =  {"state": "ON",
                    "brightness": scene.brightness_1*(brightness_global/100),
                    "color": {  
                    "r": scene.red_1,
                    "g": scene.green_1,
                    "b": scene.blue_1}
                    }

            MQTT_PUBLISH(channel, msg) 
            
            # led 2
            if group.active_led_2 == "on" and scene.active_setting_2 == "on":
                channel = "SmartHome/zigbee/" + group.led_name_2 + "/set"
                msg =  {"state": "ON",
                        "brightness": scene.brightness_2*(brightness_global/100),
                        "color": {  
                        "r": scene.red_2,
                        "g": scene.green_2,
                        "b": scene.blue_2}
                        }

                MQTT_PUBLISH(channel, msg) 

        except:
            pass
                

""" ################# """
""" program functions """
""" ################# """

def START_PROGRAM(group_id, program_id):  

    if GET_SETTING_VALUE("zigbee") == "True":


        content = GET_PROGRAM_ID(id).content

        # select each command line
        for line in content.splitlines():
            if "rgb" in line: 
                PROGRAM_SET_COLOR(line)
            if "bri" in line: 
                PROGRAM_SET_BRIGHTNESS(line)
            if "pause" in line: 
                break_value = line.split(":")
                break_value = int(break_value[1])
                time.sleep(break_value)
              
    else:
        return "Keine LED-Steuerung" 


""" ############# """
""" led turn off  """
""" ############# """

def LED_OFF(break_value):

    if GET_SETTING_VALUE("hue_bridge") == "True":

        try:
            b = CONNECT_HUE_BRIDGE()
            lights = b.get_light_objects('list')

            for light in lights:
                # led on ?
                if light.on == True: 
                    # turn off the light
                    while light.brightness > 30:
                        brightness = int(light.brightness-20)
                        if brightness < 30:
                            light.on = False
                            break 
                        else:
                            light.brightness = brightness
                            time.sleep(break_value)               
        
            # backup to deactivate all led 
            for light in lights:
                light.on = False

        except:
            return TEST_HUE_BRIDGE()
                  
    else:
        return ("Keine LED-Steuerung")   
