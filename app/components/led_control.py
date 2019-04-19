import math
import re
import time

from app import app
from app.database.database import *
from app.components.phue import Bridge
from app.components.mqtt import MQTT_PUBLISH


""" ############# """
""" led functions """
""" ############# """

def LED_START_SCENE(group_id, scene_id, brightness_global = 100):

    if GET_SETTING_VALUE("zigbee") == "True":

        try:
            group = GET_LED_GROUP_BY_ID(group_id)
            scene = GET_LED_SCENE_BY_ID(scene_id)

            # led 1
            channel = "SmartHome/zigbee2mqtt/" + group.led_name_1 + "/set"
            
            msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_1*(brightness_global/100)) +
                    ',"color": { "r":' + str(scene.red_1) + ',"g":' + str(scene.green_1) + ',"b":' + str(scene.blue_1) + 
                    ',"transition": 3}}')
            MQTT_PUBLISH(channel, msg) 

            # led 2
            channel = "SmartHome/zigbee2mqtt/" + group.led_name_2 + "/set"
            
            msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_2*(brightness_global/100)) +
                    ',"color": { "r":' + str(scene.red_2) + ',"g":' + str(scene.green_2) + ',"b":' + str(scene.blue_2) + 
                    ',"transition": 3}}')
            MQTT_PUBLISH(channel, msg) 
            
            # led 3
            channel = "SmartHome/zigbee2mqtt/" + group.led_name_3 + "/set"
            
            msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_3*(brightness_global/100)) +
                    ',"color": { "r":' + str(scene.red_3) + ',"g":' + str(scene.green_3) + ',"b":' + str(scene.blue_3) + 
                    ',"transition": 3}}')
            MQTT_PUBLISH(channel, msg) 
                        
            # led 4
            channel = "SmartHome/zigbee2mqtt/" + group.led_name_4 + "/set"
            
            msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_4*(brightness_global/100)) +
                    ',"color": { "r":' + str(scene.red_4) + ',"g":' + str(scene.green_4) + ',"b":' + str(scene.blue_4) + 
                    ',"transition": 3}}')
            MQTT_PUBLISH(channel, msg) 

            # led 5
            channel = "SmartHome/zigbee2mqtt/" + group.led_name_5 + "/set"
            
            msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_5*(brightness_global/100)) +
                    ',"color": { "r":' + str(scene.red_5) + ',"g":' + str(scene.green_5) + ',"b":' + str(scene.blue_5) + 
                    ',"transition": 3}}')
            MQTT_PUBLISH(channel, msg) 
            
            # led 6
            channel = "SmartHome/zigbee2mqtt/" + group.led_name_6 + "/set"
            
            msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_6*(brightness_global/100)) +
                    ',"color": { "r":' + str(scene.red_6) + ',"g":' + str(scene.green_6) + ',"b":' + str(scene.blue_6) + 
                    ',"transition": 3}}')
            MQTT_PUBLISH(channel, msg) 
            
            # led 7
            channel = "SmartHome/zigbee2mqtt/" + group.led_name_7 + "/set"
            
            msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_7*(brightness_global/100)) +
                    ',"color": { "r":' + str(scene.red_7) + ',"g":' + str(scene.green_7) + ',"b":' + str(scene.blue_7) + 
                    ',"transition": 3}}')
            MQTT_PUBLISH(channel, msg) 

            # led 8
            channel = "SmartHome/zigbee2mqtt/" + group.led_name_8 + "/set"
            
            msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_8*(brightness_global/100)) +
                    ',"color": { "r":' + str(scene.red_8) + ',"g":' + str(scene.green_8) + ',"b":' + str(scene.blue_8) + 
                    ',"transition": 3}}')
            MQTT_PUBLISH(channel, msg) 
            
            # led 9
            channel = "SmartHome/zigbee2mqtt/" + group.led_name_9 + "/set"
            
            msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_9*(brightness_global/100)) +
                    ',"color": { "r":' + str(scene.red_9) + ',"g":' + str(scene.green_9) + ',"b":' + str(scene.blue_9) + 
                    ',"transition": 3}}')
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
