import math
import re
import time
import threading

from app import app
from app.database.database import *
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
            if group.active_led_2 == "on": 

                channel = "SmartHome/zigbee2mqtt/" + group.led_name_2 + "/set"

                if scene.active_setting_2 == "on":        
                    msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_2*(brightness_global/100)) +
                            ',"color": { "r":' + str(scene.red_2) + ',"g":' + str(scene.green_2) + ',"b":' + str(scene.blue_2) + 
                            ',"transition": 3}}')
                else:
                    msg = '{"state": "OFF"}'

                MQTT_PUBLISH(channel, msg) 
            
            # led 3
            if group.active_led_3 == "on": 

                channel = "SmartHome/zigbee2mqtt/" + group.led_name_3 + "/set"

                if scene.active_setting_3 == "on":        
                    msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_3*(brightness_global/100)) +
                            ',"color": { "r":' + str(scene.red_3) + ',"g":' + str(scene.green_3) + ',"b":' + str(scene.blue_3) + 
                            ',"transition": 3}}')
                else:
                    msg = '{"state": "OFF"}'

                MQTT_PUBLISH(channel, msg) 

            # led 4
            if group.active_led_4 == "on": 

                channel = "SmartHome/zigbee2mqtt/" + group.led_name_4 + "/set"

                if scene.active_setting_4 == "on":        
                    msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_4*(brightness_global/100)) +
                            ',"color": { "r":' + str(scene.red_4) + ',"g":' + str(scene.green_4) + ',"b":' + str(scene.blue_4) + 
                            ',"transition": 3}}')
                else:
                    msg = '{"state": "OFF"}'

                MQTT_PUBLISH(channel, msg)             
                        
            # led 5
            if group.active_led_5 == "on": 

                channel = "SmartHome/zigbee2mqtt/" + group.led_name_5 + "/set"

                if scene.active_setting_5 == "on":        
                    msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_5*(brightness_global/100)) +
                            ',"color": { "r":' + str(scene.red_5) + ',"g":' + str(scene.green_5) + ',"b":' + str(scene.blue_5) + 
                            ',"transition": 3}}')
                else:
                    msg = '{"state": "OFF"}'

                MQTT_PUBLISH(channel, msg) 
            
            # led 6
            if group.active_led_6 == "on": 

                channel = "SmartHome/zigbee2mqtt/" + group.led_name_6 + "/set"

                if scene.active_setting_6 == "on":        
                    msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_6*(brightness_global/100)) +
                            ',"color": { "r":' + str(scene.red_6) + ',"g":' + str(scene.green_6) + ',"b":' + str(scene.blue_6) + 
                            ',"transition": 3}}')
                else:
                    msg = '{"state": "OFF"}'

                MQTT_PUBLISH(channel, msg) 

            # led 7
            if group.active_led_7 == "on": 

                channel = "SmartHome/zigbee2mqtt/" + group.led_name_7 + "/set"

                if scene.active_setting_7 == "on":        
                    msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_7*(brightness_global/100)) +
                            ',"color": { "r":' + str(scene.red_7) + ',"g":' + str(scene.green_7) + ',"b":' + str(scene.blue_7) + 
                            ',"transition": 3}}')
                else:
                    msg = '{"state": "OFF"}'

                MQTT_PUBLISH(channel, msg)     

            # led 8
            if group.active_led_8 == "on": 

                channel = "SmartHome/zigbee2mqtt/" + group.led_name_8 + "/set"

                if scene.active_setting_8 == "on":        
                    msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_8*(brightness_global/100)) +
                            ',"color": { "r":' + str(scene.red_8) + ',"g":' + str(scene.green_8) + ',"b":' + str(scene.blue_8) + 
                            ',"transition": 3}}')
                else:
                    msg = '{"state": "OFF"}'

                MQTT_PUBLISH(channel, msg) 
            
            # led 9
            if group.active_led_9 == "on": 

                channel = "SmartHome/zigbee2mqtt/" + group.led_name_9 + "/set"

                if scene.active_setting_9 == "on":        
                    msg =  ('{"state": "ON", "brightness":' + str(scene.brightness_9*(brightness_global/100)) +
                            ',"color": { "r":' + str(scene.red_9) + ',"g":' + str(scene.green_9) + ',"b":' + str(scene.blue_9) + 
                            ',"transition": 3}}')
                else:
                    msg = '{"state": "OFF"}'

                MQTT_PUBLISH(channel, msg) 

        except:
            pass
                

def LED_TURN_OFF_GROUP(group_id):

    if GET_SETTING_VALUE("zigbee") == "True":

        try:
            group = GET_LED_GROUP_BY_ID(group_id)


            # led 1
            channel = "SmartHome/zigbee2mqtt/" + group.led_name_1 + "/set"
            msg = '{"state": "OFF"}'
            MQTT_PUBLISH(channel, msg) 

            # led 2
            if group.active_led_2 == "on": 
                channel = "SmartHome/zigbee2mqtt/" + group.led_name_2 + "/set"
                msg = '{"state": "OFF"}'
                MQTT_PUBLISH(channel, msg) 

            # led 3
            if group.active_led_3 == "on": 
                channel = "SmartHome/zigbee2mqtt/" + group.led_name_3 + "/set"
                msg = '{"state": "OFF"}'
                MQTT_PUBLISH(channel, msg) 

            # led 4
            if group.active_led_4 == "on": 
                channel = "SmartHome/zigbee2mqtt/" + group.led_name_4 + "/set"
                msg = '{"state": "OFF"}'
                MQTT_PUBLISH(channel, msg) 

            # led 5
            if group.active_led_5 == "on": 
                channel = "SmartHome/zigbee2mqtt/" + group.led_name_5 + "/set"
                msg = '{"state": "OFF"}'
                MQTT_PUBLISH(channel, msg) 

            # led 6
            if group.active_led_6 == "on": 
                channel = "SmartHome/zigbee2mqtt/" + group.led_name_6 + "/set"
                msg = '{"state": "OFF"}'
                MQTT_PUBLISH(channel, msg) 

            # led 7
            if group.active_led_7 == "on": 
                channel = "SmartHome/zigbee2mqtt/" + group.led_name_7 + "/set"
                msg = '{"state": "OFF"}'
                MQTT_PUBLISH(channel, msg)                 

            # led 8
            if group.active_led_8 == "on": 
                channel = "SmartHome/zigbee2mqtt/" + group.led_name_8 + "/set"
                msg = '{"state": "OFF"}'
                MQTT_PUBLISH(channel, msg) 
            
            # led 9
            if group.active_led_9 == "on": 
                channel = "SmartHome/zigbee2mqtt/" + group.led_name_9 + "/set"
                msg = '{"state": "OFF"}'
                MQTT_PUBLISH(channel, msg) 

        except:
            pass


def LED_TURN_OFF_ALL():
    
    if GET_SETTING_VALUE("zigbee") == "True":    

        leds = GET_ALL_MQTT_DEVICES("led")

        for led in leds:
            channel = "SmartHome/zigbee2mqtt/" + led.name + "/set"
            msg = '{"state": "OFF"}'
            MQTT_PUBLISH(channel, msg)         



""" ################# """
""" program functions """
""" ################# """

def SET_LED_RGB(group_id, led_id, red, green, blue):

    group = GET_LED_GROUP_BY_ID(group_id)

    # led 1
    if led_id == "1":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_1 + "/set"
        msg     =  ('{"state": "ON","color": { "r":' + str(red) + 
                    ',"g":' + str(green) + ',"b":' + str(blue) + ',"transition": 3}}')
        MQTT_PUBLISH(channel, msg) 

    # led 2
    if led_id == "2":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_2 + "/set"
        msg     =  ('{"state": "ON","color": { "r":' + str(red) + 
                    ',"g":' + str(green) + ',"b":' + str(blue) + ',"transition": 3}}')
        MQTT_PUBLISH(channel, msg)    

    # led 3
    if led_id == "3":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_3 + "/set"
        msg     =  ('{"state": "ON","color": { "r":' + str(red) + 
                    ',"g":' + str(green) + ',"b":' + str(blue) + ',"transition": 3}}')
        MQTT_PUBLISH(channel, msg) 

    # led 4
    if led_id == "4":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_4 + "/set"
        msg     =  ('{"state": "ON","color": { "r":' + str(red) + 
                    ',"g":' + str(green) + ',"b":' + str(blue) + ',"transition": 3}}')
        MQTT_PUBLISH(channel, msg)    

    # led 5
    if led_id == "5":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_5 + "/set"
        msg     =  ('{"state": "ON","color": { "r":' + str(red) + 
                    ',"g":' + str(green) + ',"b":' + str(blue) + ',"transition": 3}}')
        MQTT_PUBLISH(channel, msg) 

    # led 6
    if led_id == "6":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_6 + "/set"
        msg     =  ('{"state": "ON","color": { "r":' + str(red) + 
                    ',"g":' + str(green) + ',"b":' + str(blue) + ',"transition": 3}}')
        MQTT_PUBLISH(channel, msg)    

    # led 7
    if led_id == "7":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_7 + "/set"
        msg     =  ('{"state": "ON","color": { "r":' + str(red) + 
                    ',"g":' + str(green) + ',"b":' + str(blue) + ',"transition": 3}}')
        MQTT_PUBLISH(channel, msg) 

    # led 8
    if led_id == "8":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_8 + "/set"
        msg     =  ('{"state": "ON","color": { "r":' + str(red) + 
                    ',"g":' + str(green) + ',"b":' + str(blue) + ',"transition": 3}}')
        MQTT_PUBLISH(channel, msg)    

    # led 9
    if led_id == "9":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_9 + "/set"
        msg     =  ('{"state": "ON","color": { "r":' + str(red) + 
                    ',"g":' + str(green) + ',"b":' + str(blue) + ',"transition": 3}}')
        MQTT_PUBLISH(channel, msg) 



def SET_LED_BRIGHTNESS(group_id, led_id, brightness):

    group = GET_LED_GROUP_BY_ID(group_id)

    # led 1
    if led_id == "1":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_1 + "/set"
        msg     = '{"state": "ON", "brightness":' + str(brightness) + ',"transition": 3}}'
        MQTT_PUBLISH(channel, msg) 

    # led 2
    if led_id == "2":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_2 + "/set"
        msg     = '{"state": "ON", "brightness":' + str(brightness) + ',"transition": 3}}'
        MQTT_PUBLISH(channel, msg) 

    # led 3
    if led_id == "3":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_3 + "/set"
        msg     = '{"state": "ON", "brightness":' + str(brightness) + ',"transition": 3}}'
        MQTT_PUBLISH(channel, msg)        

    # led 4
    if led_id == "4":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_4 + "/set"
        msg     = '{"state": "ON", "brightness":' + str(brightness) + ',"transition": 3}}'
        MQTT_PUBLISH(channel, msg)  

    # led 5
    if led_id == "5":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_5 + "/set"
        msg     = '{"state": "ON", "brightness":' + str(brightness) + ',"transition": 3}}'
        MQTT_PUBLISH(channel, msg) 

    # led 6
    if led_id == "6":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_6 + "/set"
        msg     = '{"state": "ON", "brightness":' + str(brightness) + ',"transition": 3}}'
        MQTT_PUBLISH(channel, msg)  

    # led 7
    if led_id == "7":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_7 + "/set"
        msg     = '{"state": "ON", "brightness":' + str(brightness) + ',"transition": 3}}'
        MQTT_PUBLISH(channel, msg) 

    # led 8
    if led_id == "8":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_8 + "/set"
        msg     = '{"state": "ON", "brightness":' + str(brightness) + ',"transition": 3}}'
        MQTT_PUBLISH(channel, msg)  

    # led 9
    if led_id == "9":
        channel = "SmartHome/zigbee2mqtt/" + group.led_name_9 + "/set"
        msg     = '{"state": "ON", "brightness":' + str(brightness) + ',"transition": 3}}'
        MQTT_PUBLISH(channel, msg) 


def START_LED_PROGRAM_THREAD(group_id, program_id):

    class led_program_Thread(threading.Thread):

        def __init__(self, ID = 1, name = "led_program_Thread"):
            threading.Thread.__init__(self)
            self.ID = ID
            self.name = name

        def run(self):

            if GET_SETTING_VALUE("zigbee") == "True":

                LED_TURN_OFF_GROUP(group_id)

                content = GET_LED_PROGRAM_BY_ID(program_id).content

                # select each command line
                for line in content.splitlines():

                    if "rgb" in line: 
                        led_id = line.split(":")[0]
                        rgb    = re.findall(r'\d+', line.split(":")[1])
                        red    = rgb[0]
                        green  = rgb[1]           
                        blue   = rgb[2]  
                        SET_LED_RGB(group_id, led_id, red, green, blue)
                        
                    if "bri" in line: 
                        led_id = line.split(":")[0]
                        brightness = re.findall(r'\d+', line.split(":")[1])
                        brightness = brightness[0]
                        SET_LED_BRIGHTNESS(group_id, led_id, brightness)

                    if "pause" in line: 
                        break_value = line.split(":")
                        break_value = int(break_value[1])
                        time.sleep(break_value)
                    
            else:
                return "Keine LED-Steuerung"             
            
    # start thread
    t1 = led_program_Thread()
    t1.start()
