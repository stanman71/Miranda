import paho.mqtt.client as mqtt

import math
import re
import time
import threading
import json

from app import app
from app.database.database import *
from app.components.file_management import READ_LOGFILE_MQTT, GET_CONFIG_MQTT_BROKER


""" #################### """
""" mqtt publish message """
""" #################### """

BROKER_ADDRESS = GET_CONFIG_MQTT_BROKER()

def MQTT_PUBLISH(MQTT_TOPIC, MQTT_MSG):

    try:

        def on_publish(client, userdata, mid):
            print ('Message Published...')

        client = mqtt.Client()
        client.on_publish = on_publish
        client.connect(BROKER_ADDRESS) 
        client.publish(MQTT_TOPIC,MQTT_MSG)
        client.disconnect()

        return ""
        
    except:
        pass


""" ################### """
""" led basic functions """
""" ################### """

# This is based on original code from http://stackoverflow.com/a/22649803

def RGBtoXY(r, g, b):
    
    def EnhanceColor(normalized):
        if normalized > 0.04045:
            return math.pow( (normalized + 0.055) / (1.0 + 0.055), 2.4)
        else:
            return normalized / 12.92
    
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
        xFinal = round( (X / (X + Y + Z)), 3 )
        yFinal = round( (Y / (X + Y + Z)), 3 )

    return (xFinal, yFinal)


def SETTING_LED_RGB(led_name, red, green, blue, brightness):
    
    xy = RGBtoXY(red, green, blue)
    
    channel = "SmartHome/zigbee2mqtt/" + led_name + "/set"
    msg     = '{"state":"ON","brightness":' + str(brightness) + ',"color": { "x":' + str(xy[0]) + ',"y":' + str(xy[1]) + '}}'
    MQTT_PUBLISH(channel, msg) 


def SETTING_LED_WHITE(led_name, color_temp, brightness):

    channel = "SmartHome/zigbee2mqtt/" + led_name + "/set"
    msg     = '{"state": "ON","brightness":' + str(brightness) + ',"color_temp":"' + str(color_temp) + '"}'
    MQTT_PUBLISH(channel, msg) 


def SETTING_LED_SIMPLE(led_name, brightness):

    channel = "SmartHome/zigbee2mqtt/" + led_name + "/set"
    msg     = '{"state": "ON","brightness":"' + str(brightness) + '"}'
    MQTT_PUBLISH(channel, msg) 


def SETTING_LED_BRIGHTNESS(led_name, brightness):
    
    channel = "SmartHome/zigbee2mqtt/" + led_name + "/set"
    msg     = '{"state": "ON","brightness":"' + str(brightness) + '"}'
    MQTT_PUBLISH(channel, msg) 


def SETTING_LED_TURN_OFF(led_name):

    channel = "SmartHome/zigbee2mqtt/" + led_name + "/set"
    msg = '{"state": "OFF"}'
    MQTT_PUBLISH(channel, msg) 


""" ##################### """
""" led control functions """
""" ##################### """


def LED_START_SCENE(group_id, scene_id, brightness_global = 100):
    
    if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") == "True":

        try:      
            group = GET_LED_GROUP_BY_ID(group_id)
            scene = GET_LED_SCENE_BY_ID(scene_id)
        
            # led 1
            led_1        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_1)
            brightness_1 = scene.brightness_1*(brightness_global/100)
            
            if led_1.device_type == "led_rgb":
                SETTING_LED_RGB(led_1.name, scene.red_1, scene.green_1, scene.blue_1, int(brightness_1))            
            if led_1.device_type == "led_white":
                SETTING_LED_WHITE(led_1.name, scene.color_temp_1, int(brightness_1))                
            if led_1.device_type == "led_simple":
                SETTING_LED_SIMPLE(led_1.name, int(brightness_1))   

            # led 2
            led_2 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_2)
            
            if group.active_led_2 == "on": 

                if scene.active_setting_2 == "on":
                
                    brightness_2 = scene.brightness_2*(brightness_global/100)
                    
                    if led_2.device_type == "led_rgb":
                        SETTING_LED_RGB(led_2.name, scene.red_2, scene.green_2, scene.blue_2, int(brightness_2))                    
                    if led_2.device_type == "led_white":
                        SETTING_LED_WHITE(led_2.name, scene.color_temp_2, int(brightness_2))                                            
                    if led_1.device_type == "led_simple":
                        SETTING_LED_SIMPLE(led_2.name, int(brightness_2))  
                        
                else:
                    SETTING_LED_TURN_OFF(led_2.name)

            # led 3
            led_3 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_3)           
            
            if group.active_led_3 == "on": 
                
                if scene.active_setting_3 == "on":

                    brightness_3 = scene.brightness_3*(brightness_global/100)
                    
                    if led_3.device_type == "led_rgb":
                        SETTING_LED_RGB(led_3.name, scene.red_3, scene.green_3, scene.blue_3, int(brightness_3)) 
                    if led_3.device_type == "led_white":
                        SETTING_LED_WHITE(led_3.name, scene.color_temp_3, int(brightness_3))                                            
                    if led_1.device_type == "led_simple":
                        SETTING_LED_SIMPLE(led_3.name, int(brightness_3))   

                else:
                    SETTING_LED_TURN_OFF(led_3.name)
                
            # led 4
            led_4 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_4)            
            
            if group.active_led_4 == "on": 
                
                if scene.active_setting_4 == "on":

                    brightness_4 = scene.brightness_4*(brightness_global/100)
                    
                    if led_4.device_type == "led_rgb":
                        SETTING_LED_RGB(led_4.name, scene.red_4, scene.green_4, scene.blue_4, int(brightness_4)) 
                    if led_4.device_type == "led_white":
                        SETTING_LED_WHITE(led_4.name, scene.color_temp_4, int(brightness_4))                                            
                    if led_1.device_type == "led_simple":
                        SETTING_LED_SIMPLE(led_4.name, int(brightness_4))  

                else:
                    SETTING_LED_TURN_OFF(led_4.name)
                
            # led 5
            led_5 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_5)           
            
            if group.active_led_5 == "on": 
                
                if scene.active_setting_5 == "on":

                    brightness_5 = scene.brightness_5*(brightness_global/100)
                    
                    if led_5.device_type == "led_rgb":
                        SETTING_LED_RGB(led_5.name, scene.red_5, scene.green_5, scene.blue_5, int(brightness_5)) 
                    if led_5.device_type == "led_white":
                        SETTING_LED_WHITE(led_5.name, scene.color_temp_5, int(brightness_5))                                            
                    if led_1.device_type == "led_simple":
                        SETTING_LED_SIMPLE(led_5.name, int(brightness_5))  
        
                else:
                    SETTING_LED_TURN_OFF(led_5.name)
                                    
            # led 6
            led_6 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_6)           
            
            if group.active_led_6 == "on": 
                
                if scene.active_setting_6 == "on":

                    brightness_6 = scene.brightness_6*(brightness_global/100)
                    
                    if led_6.device_type == "led_rgb":
                        SETTING_LED_RGB(led_6.name, scene.red_6, scene.green_6, scene.blue_6, int(brightness_6)) 
                    if led_6.device_type == "led_white":
                        SETTING_LED_WHITE(led_6.name, scene.color_temp_6, int(brightness_6))                                            
                    if led_1.device_type == "led_simple":
                        SETTING_LED_SIMPLE(led_6.name, int(brightness_6))                       
     
                else:
                    SETTING_LED_TURN_OFF(led_6.name)
                                    
            # led 7
            led_7 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_7)            
            
            if group.active_led_7 == "on": 
                
                if scene.active_setting_7 == "on":

                    brightness_7 = scene.brightness_7*(brightness_global/100)
                    
                    if led_7.device_type == "led_rgb":
                        SETTING_LED_RGB(led_7.name, scene.red_7, scene.green_7, scene.blue_7, int(brightness_7)) 
                    if led_7.device_type == "led_white":
                        SETTING_LED_WHITE(led_7.name, scene.color_temp_7, int(brightness_7))                                            
                    if led_1.device_type == "led_simple":
                        SETTING_LED_SIMPLE(led_7.name, int(brightness_7))    
           
                else:
                    SETTING_LED_TURN_OFF(led_7.name)
                                    
            # led 8
            led_8 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_8)           
            
            if group.active_led_8 == "on": 
                
                if scene.active_setting_8 == "on":

                    brightness_8 = scene.brightness_8*(brightness_global/100)
                    
                    if led_8.device_type == "led_rgb":
                        SETTING_LED_RGB(led_8.name, scene.red_8, scene.green_8, scene.blue_8, int(brightness_8)) 
                    if led_8.device_type == "led_white":
                        SETTING_LED_WHITE(led_8.name, scene.color_temp_8, int(brightness_8))                                            
                    if led_1.device_type == "led_simple":
                        SETTING_LED_SIMPLE(led_8.name, int(brightness_8))   
      
                else:
                    SETTING_LED_TURN_OFF(led_8.name)
                                    
            # led 9
            led_9 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_9)           
            
            if group.active_led_9 == "on":  
                
                if scene.active_setting_9 == "on":

                    brightness_9 = scene.brightness_9*(brightness_global/100)
                    
                    if led_9.device_type == "led_rgb":
                        SETTING_LED_RGB(led_9.name, scene.red_9, scene.green_9, scene.blue_9, int(brightness_9)) 
                    if led_9.device_type == "led_white":
                        SETTING_LED_WHITE(led_9.name, scene.color_temp_9, int(brightness_9))                                            
                    if led_1.device_type == "led_simple":
                        SETTING_LED_SIMPLE(led_9.name, int(brightness_9))                                           
        
                else:
                    SETTING_LED_TURN_OFF(led_9.name)                    

            # set current state
            scene_name = GET_LED_SCENE_BY_ID(scene_id).name
            
            SET_LED_GROUP_CURRENT_SETTING(group_id, scene_name)
            SET_LED_GROUP_CURRENT_BRIGHTNESS(group_id, brightness_global)      

            time.sleep(1)
                
            return LED_CHECK_SETTING() 

        
        except Exception as e:
            WRITE_LOGFILE_SYSTEM("ERROR", "LED | start scene | " + str(e))
            return [str(e)]
        
    else:
        return ["Keine LED-Steuerung aktiviert"]
                


def LED_SET_BRIGHTNESS_DIMMER(group_id, command):
    
    group              = GET_LED_GROUP_BY_ID(group_id)
    current_brightness = group.current_brightness
    
    if command == "turn_up":
        target_brightness = int(current_brightness) + 20
        
        if target_brightness > 100:
            target_brightness = 100
    
    if command == "turn_down":
        target_brightness = int(current_brightness) - 20
        
        if target_brightness < 0:
            target_brightness = 0    
             
    error_message = LED_SET_BRIGHTNESS(group.id, target_brightness)
    
    return error_message
    
    

def LED_SET_BRIGHTNESS(group_id, brightness_global = 100):
    
    if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") == "True":

        try:
            group      = GET_LED_GROUP_BY_ID(group_id)
            scene_name = GET_LED_GROUP_BY_ID(group_id).current_setting
            scene      = GET_LED_SCENE_BY_NAME(scene_name)
            
            # led 1
            led_1        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_1)
            brightness_1 = scene.brightness_1*(brightness_global/100)
            
            SETTING_LED_BRIGHTNESS(led_1.name, int(brightness_1))
                
            # led 2
            if group.active_led_2 == "on":       
                led_2        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_2)
                brightness_2 = scene.brightness_2*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_2.name, int(brightness_2))

            # led 3
            if group.active_led_3 == "on":      
                led_3        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_3)
                brightness_3 = scene.brightness_3*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_3.name, int(brightness_3))

            # led 4
            if group.active_led_4 == "on":      
                led_4        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_4)
                brightness_4 = scene.brightness_4*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_4.name, int(brightness_4))

            # led 5
            if group.active_led_5 == "on":      
                led_5        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_5)
                brightness_5 = scene.brightness_5*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_5.name, int(brightness_5))

            # led 6
            if group.active_led_6 == "on":       
                led_6        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_6)
                brightness_6 = scene.brightness_6*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_6.name, int(brightness_6))

            # led 7
            if group.active_led_7 == "on":      
                led_7        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_7)
                brightness_7 = scene.brightness_7*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_7.name, int(brightness_7))

            # led 8
            if group.active_led_8 == "on":      
                led_8        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_8)
                brightness_8 = scene.brightness_8*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_8.name, int(brightness_8))

            # led 9
            if group.active_led_9 == "on":      
                led_9        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_9)
                brightness_9 = scene.brightness_9*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_9.name, int(brightness_9))
              
            time.sleep(1)
            
            # set current state
            SET_LED_GROUP_CURRENT_BRIGHTNESS(group_id, brightness_global)
                
            return LED_CHECK_SETTING() 
        
        except Exception as e:
            WRITE_LOGFILE_SYSTEM("ERROR", "LED | set brightness | " + str(e))
            return [str(e)]

    else:
        return ["Keine LED-Steuerung aktiviert"]  


def LED_TURN_OFF_GROUP(group_id):

    if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") == "True":

        try:
            group = GET_LED_GROUP_BY_ID(group_id)
            
            # led 1
            SETTING_LED_TURN_OFF(group.led_name_1)
                
            # led 2
            if group.active_led_2 == "on": 
                SETTING_LED_TURN_OFF(group.led_name_2)
            # led 3
            if group.active_led_3 == "on": 
                SETTING_LED_TURN_OFF(group.led_name_3)
            # led 4
            if group.active_led_4 == "on": 
                SETTING_LED_TURN_OFF(group.led_name_4)
            # led 5
            if group.active_led_5 == "on": 
                SETTING_LED_TURN_OFF(group.led_name_5)
            # led 6
            if group.active_led_6 == "on": 
                SETTING_LED_TURN_OFF(group.led_name_6)
            # led 7
            if group.active_led_7 == "on": 
                SETTING_LED_TURN_OFF(group.led_name_7)
            # led 8
            if group.active_led_8 == "on": 
                SETTING_LED_TURN_OFF(group.led_name_8)
            # led 9
            if group.active_led_9 == "on": 
                SETTING_LED_TURN_OFF(group.led_name_9)
     
            time.sleep(1)
            
            # set current state
            SET_LED_GROUP_CURRENT_SETTING(group_id, "OFF") 
            SET_LED_GROUP_CURRENT_BRIGHTNESS(group_id, 0)           
            
            return LED_CHECK_SETTING() 

        except Exception as e:
            WRITE_LOGFILE_SYSTEM("ERROR", "LED | turn_off | " + str(e))
            return [str(e)]

    else:
        return ["Keine LED-Steuerung aktiviert"]  
        

def LED_TURN_OFF_ALL():
    
    if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") == "True":   
        
        try: 
            leds = GET_ALL_MQTT_DEVICES("led")

            for led in leds:
                SETTING_LED_TURN_OFF(led.name)
                
            time.sleep(1)
            
            # set current state
            for group in GET_ALL_ACTIVE_LED_GROUPS():   
                SET_LED_GROUP_CURRENT_SETTING(group.id, "OFF")
                SET_LED_GROUP_CURRENT_BRIGHTNESS(group.id, 0)
                
            return LED_CHECK_SETTING() 
            
        except Exception as e:
            WRITE_LOGFILE_SYSTEM("ERROR", "LED | turn_off | " + str(e))
            return str(e)

    else:
        return ["Keine LED-Steuerung aktiviert"]  


""" ################# """
""" program functions """
""" ################# """


def LED_START_PROGRAM_THREAD(group_id, program_id):

    try:
        LED_TURN_OFF_GROUP(group_id)
        
        # set current state
        program_name = GET_LED_PROGRAM_BY_ID(program_id).name  
        
        
        content = GET_LED_PROGRAM_BY_ID(program_id).content

        for line in content.splitlines():
            
            if "rgb" in line or "color_temp" in line: 
                brightness = line.split(":")[2]
                break
        
        SET_LED_GROUP_CURRENT_SETTING(group_id, program_name)
        SET_LED_GROUP_CURRENT_BRIGHTNESS(group_id, int(brightness))

        # start thread
        Thread = threading.Thread(target=LED_PROGRAM_THREAD, args=(group_id, program_id, ))
        Thread.start()  
        
        return "" 
     
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "LED | start program | " + str(e))
        return str(e)
    

def LED_PROGRAM_THREAD(group_id, program_id):

    if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") == "True":
        
        content = GET_LED_PROGRAM_BY_ID(program_id).content

        # select each command line
        for line in content.splitlines():

            if "led_rgb" in line: 
                led_id = line.split(":")[0]
                
                if led_id == "1":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_1
                if led_id == "2":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_2                    
                if led_id == "3":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_3                  
                if led_id == "4":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_4  
                if led_id == "5":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_5  
                if led_id == "6":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_6                    
                if led_id == "7":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_7                  
                if led_id == "8":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_8  
                if led_id == "9":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_9  

                rgb        = re.findall(r'\d+', line.split(":")[1])
                red        = rgb[0]
                green      = rgb[1]           
                blue       = rgb[2]
                
                brightness = line.split(":")[2]
                
                SETTING_LED_RGB(led_name, int(red), int(green), int(blue), int(brightness))

            if "led_white" in line: 
                led_id = line.split(":")[0]

                if led_id == "1":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_1
                if led_id == "2":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_2                    
                if led_id == "3":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_3                  
                if led_id == "4":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_4  
                if led_id == "5":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_5  
                if led_id == "6":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_6                    
                if led_id == "7":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_7                  
                if led_id == "8":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_8  
                if led_id == "9":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_9   

                color_temp = re.findall(r'\d+', line.split(":")[1])
                color_temp = color_temp[0]
                
                brightness = line.split(":")[2]
                
                SETTING_LED_WHITE(led_name, int(color_temp), int(brightness))

            if "led_simple" in line: 
                led_id = line.split(":")[0]

                if led_id == "1":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_1
                if led_id == "2":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_2                    
                if led_id == "3":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_3                  
                if led_id == "4":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_4  
                if led_id == "5":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_5  
                if led_id == "6":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_6                    
                if led_id == "7":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_7                  
                if led_id == "8":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_8  
                if led_id == "9":
                    led_name = GET_LED_GROUP_BY_ID(group_id).led_name_9   

                brightness = line.split(":")[1]
                
                SETTING_LED_SIMPLE(led_name, int(brightness))

            if "pause" in line: 
                break_value = line.split(":")
                break_value = int(break_value[1])
                time.sleep(break_value)
                
        time.sleep(1)
        
        return LED_CHECK_SETTING() 
              
    else:
        return ["Keine LED-Steuerung aktiviert"]           

        
""" ################## """
"""  check led setting """
""" ################## """
 
def LED_CHECK_SETTING():
            
    input_messages = READ_LOGFILE_MQTT("zigbee2mqtt", "SmartHome/zigbee2mqtt/bridge/log", 5)
            
    list_errors = []
 
    if input_messages != "Message nicht gefunden":
        for input_message in input_messages:
            input_message = str(input_message[2])
  
            data = json.loads(input_message)
            
            if data["type"] == "zigbee_publish_error":
                if (data["meta"]["entity"]["ID"]) not in list_errors:
                    list_errors.append(data["meta"]["entity"]["ID"])
                    list_errors.append(data["message"])
                    
    if list_errors != []:
        WRITE_LOGFILE_SYSTEM("WARNING", "LED | >>> " + str(list_errors))
        return list_errors
        
    else:
        return ""
        
        
