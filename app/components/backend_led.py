import math
import time
import threading
import json

from app import app
from app.database.database import *
from app.components.mqtt import MQTT_PUBLISH, ZIGBEE2MQTT_CHECK_SETTING
from app.components.email import SEND_EMAIL


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
    
    xy = RGBtoXY(int(red), int(green), int(blue))
    
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
    
    
    
""" ####################### """
""" led group check setting """
""" ####################### """


def LED_GROUP_CHECK_SETTING_THREAD(group_id, scene_id, scene, brightness, delay, limit): 
 
    Thread = threading.Thread(target=LED_GROUP_CHECK_SETTING_PROCESS, args=(group_id, scene_id, scene, brightness, delay, limit, ))
    Thread.start()   

 
def LED_GROUP_CHECK_SETTING_PROCESS(group_id, scene_id, scene, brightness, delay, limit): 
               
    if scene == "OFF":
        setting = '{"state":"OFF"}'
    else:
        setting = '{"state":"ON"}'
                    
    # check setting 1 try
    time.sleep(delay)                             
    result = LED_GROUP_CHECK_SETTING(group_id, scene_id, setting, limit)
    
    # set current state
    if result == []:
        SET_LED_GROUP_CURRENT_SETTING(group_id, scene)
        SET_LED_GROUP_CURRENT_BRIGHTNESS(group_id, brightness)   
        
    else:
        # check setting 2 try
        time.sleep(delay)                             
        result = LED_GROUP_CHECK_SETTING(group_id, scene_id, setting, limit)
        
        # set current state 
        if result == []:
            SET_LED_GROUP_CURRENT_SETTING(group_id, scene)
            SET_LED_GROUP_CURRENT_BRIGHTNESS(group_id, brightness)  
        
        else:
            # check setting 3 try
            time.sleep(delay)                             
            result = LED_GROUP_CHECK_SETTING(group_id, scene_id, setting, limit) 
     
              
    # output
    SET_LED_GROUP_CURRENT_SETTING(group_id, scene)
    SET_LED_GROUP_CURRENT_BRIGHTNESS(group_id, brightness)                
                
    group_name = GET_LED_GROUP_BY_ID(group_id).name
                
    if result == []:
        WRITE_LOGFILE_SYSTEM("SUCCESS", "LED | Group - " + group_name + " | Setting changed | " + str(scene) + " : "  + str(brightness) + " %") 
    else:
        WRITE_LOGFILE_SYSTEM("WARNING", "LED | Group - " + group_name + " | "  + str(scene) + " : "  + str(brightness) + " | " + str(result)) 
        SEND_EMAIL("WARNING", "LED | Group - " + group_name + " | "  + str(scene) + " : "  + str(brightness) + " | " + str(result)) 

    return result     
                                                             
    
def LED_GROUP_CHECK_SETTING(group_id, scene_id, setting, limit):
    
    if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") == "True":
        
        error_list = []

        try:      
            group = GET_LED_GROUP_BY_ID(group_id)
            
            # group isn't offline
            if scene_id != 0:
                
                scene = GET_LED_SCENE_BY_ID(scene_id)

                # led 1
                led_1 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_1)

                if ZIGBEE2MQTT_CHECK_SETTING(led_1.name, setting, limit) == False:
                    error_list.append(led_1.name + " >>> Setting not confirmed")

                # led 2
                led_2 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_2)
                
                if group.active_led_2 == "True": 

                    if scene.active_setting_2 == "True":
                        if ZIGBEE2MQTT_CHECK_SETTING(led_2.name, setting, limit) == False:
                            error_list.append(led_2.name + " >>> Setting not confirmed")
                                    
                    else:
                        if ZIGBEE2MQTT_CHECK_SETTING(led_2.name, '{"state":"OFF"}', limit) == False:
                            error_list.append(led_2.name + " >>> Setting not confirmed")

                # led 3
                led_3 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_3)
                
                if group.active_led_3 == "True": 

                    if scene.active_setting_3 == "True":
                        if ZIGBEE2MQTT_CHECK_SETTING(led_3.name, setting, limit) == False:
                            error_list.append(led_3.name + " >>> Setting not confirmed")
                                    
                    else:
                        if ZIGBEE2MQTT_CHECK_SETTING(led_3.name, '{"state":"OFF"}', limit) == False:
                            error_list.append(led_3.name + " >>> Setting not confirmed")

                # led 4
                led_4 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_4)
                
                if group.active_led_4 == "True": 

                    if scene.active_setting_4 == "True":
                        if ZIGBEE2MQTT_CHECK_SETTING(led_4.name, setting, limit) == False:
                            error_list.append(led_4.name + " >>> Setting not confirmed")
                                    
                    else:
                        if ZIGBEE2MQTT_CHECK_SETTING(led_4.name, '{"state":"OFF"}', limit) == False:
                            error_list.append(led_4.name + " >>> Setting not confirmed")

                # led 5
                led_5 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_5)
                
                if group.active_led_5 == "True": 

                    if scene.active_setting_5 == "True":
                        if ZIGBEE2MQTT_CHECK_SETTING(led_5.name, setting, limit) == False:
                            error_list.append(led_5.name + " >>> Setting not confirmed")
                                    
                    else:
                        if ZIGBEE2MQTT_CHECK_SETTING(led_5.name, '{"state":"OFF"}', limit) == False:
                            error_list.append(led_5.name + " >>> Setting not confirmed")

                # led 6
                led_6 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_6)
                
                if group.active_led_6 == "True": 

                    if scene.active_setting_6 == "True":
                        if ZIGBEE2MQTT_CHECK_SETTING(led_6.name, setting, limit) == False:
                            error_list.append(led_6.name + " >>> Setting not confirmed")
                                    
                    else:
                        if ZIGBEE2MQTT_CHECK_SETTING(led_6.name, '{"state":"OFF"}', limit) == False:
                            error_list.append(led_6.name + " >>> Setting not confirmed")

                # led 7
                led_7 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_7)
                
                if group.active_led_7 == "True": 

                    if scene.active_setting_7 == "True":
                        if ZIGBEE2MQTT_CHECK_SETTING(led_7.name, setting, limit) == False:
                            error_list.append(led_7.name + " >>> Setting not confirmed")
                                    
                    else:
                        if ZIGBEE2MQTT_CHECK_SETTING(led_7.name, '{"state":"OFF"}', limit) == False:
                            error_list.append(led_7.name + " >>> Setting not confirmed")

                # led 8
                led_8 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_8)
                
                if group.active_led_8 == "True": 

                    if scene.active_setting_8 == "True":
                        if ZIGBEE2MQTT_CHECK_SETTING(led_8.name, setting, limit) == False:
                            error_list.append(led_8.name + " >>> Setting not confirmed")
                                    
                    else:
                        if ZIGBEE2MQTT_CHECK_SETTING(led_8.name, '{"state":"OFF"}', limit) == False:
                            error_list.append(led_8.name + " >>> Setting not confirmed")

                # led 9
                led_9 = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_9)
                
                if group.active_led_9 == "True": 

                    if scene.active_setting_9 == "True":
                        if ZIGBEE2MQTT_CHECK_SETTING(led_9.name, setting, limit) == False:
                            error_list.append(led_9.name + " >>> Setting not confirmed")
                                    
                    else:
                        if ZIGBEE2MQTT_CHECK_SETTING(led_9.name, '{"state":"OFF"}', limit) == False:
                            error_list.append(led_9.name + " >>> Setting not confirmed")

            return error_list
                
        
        except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "LED | Start Scene | " + setting + " | " + str(e))
            SEND_EMAIL("ERROR", "LED | Start Scene | " + setting + " | " + str(e))            
            return [str(e)]
        
        
    else:
        return ["Keine LED-Steuerung aktiviert"]
    


""" ##################### """
"""  led group functions """
""" ##################### """


def LED_GROUP_SET_SCENE(group_id, scene_id, brightness_global = 100):
    
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
            
            if group.active_led_2 == "True": 

                if scene.active_setting_2 == "True":
                
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
            
            if group.active_led_3 == "True": 
                
                if scene.active_setting_3 == "True":

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
            
            if group.active_led_4 == "True": 
                
                if scene.active_setting_4 == "True":

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
            
            if group.active_led_5 == "True": 
                
                if scene.active_setting_5 == "True":

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
            
            if group.active_led_6 == "True": 
                
                if scene.active_setting_6 == "True":

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
            
            if group.active_led_7 == "True": 
                
                if scene.active_setting_7 == "True":

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
            
            if group.active_led_8 == "True": 
                
                if scene.active_setting_8 == "True":

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
            
            if group.active_led_9 == "True":  
                
                if scene.active_setting_9 == "True":

                    brightness_9 = scene.brightness_9*(brightness_global/100)
                    
                    if led_9.device_type == "led_rgb":
                        SETTING_LED_RGB(led_9.name, scene.red_9, scene.green_9, scene.blue_9, int(brightness_9)) 
                    if led_9.device_type == "led_white":
                        SETTING_LED_WHITE(led_9.name, scene.color_temp_9, int(brightness_9))                                            
                    if led_1.device_type == "led_simple":
                        SETTING_LED_SIMPLE(led_9.name, int(brightness_9))                                           
        
                else:
                    SETTING_LED_TURN_OFF(led_9.name)                       

            return ""

        
        except Exception as e:
            WRITE_LOGFILE_SYSTEM("ERROR", "LED | Start Scene | " + str(e))            
            SEND_EMAIL("ERROR", "LED | Start Scene | " + str(e))
            return [str(e)]
        
    else:
        return ["Keine LED-Steuerung aktiviert"]
                


def LED_GROUP_SET_BRIGHTNESS_DIMMER(group_id, command):
    
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
             
    LED_SET_BRIGHTNESS(group.id, target_brightness)
    
    

def LED_GROUP_SET_BRIGHTNESS(group_id, brightness_global = 100):
    
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
            if group.active_led_2 == "True":       
                led_2        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_2)
                brightness_2 = scene.brightness_2*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_2.name, int(brightness_2))

            # led 3
            if group.active_led_3 == "True":      
                led_3        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_3)
                brightness_3 = scene.brightness_3*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_3.name, int(brightness_3))

            # led 4
            if group.active_led_4 == "True":      
                led_4        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_4)
                brightness_4 = scene.brightness_4*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_4.name, int(brightness_4))

            # led 5
            if group.active_led_5 == "True":      
                led_5        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_5)
                brightness_5 = scene.brightness_5*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_5.name, int(brightness_5))

            # led 6
            if group.active_led_6 == "True":       
                led_6        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_6)
                brightness_6 = scene.brightness_6*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_6.name, int(brightness_6))

            # led 7
            if group.active_led_7 == "True":      
                led_7        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_7)
                brightness_7 = scene.brightness_7*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_7.name, int(brightness_7))

            # led 8
            if group.active_led_8 == "True":      
                led_8        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_8)
                brightness_8 = scene.brightness_8*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_8.name, int(brightness_8))

            # led 9
            if group.active_led_9 == "True":      
                led_9        = GET_MQTT_DEVICE_BY_IEEEADDR(group.led_ieeeAddr_9)
                brightness_9 = scene.brightness_9*(brightness_global/100)
                
                SETTING_LED_BRIGHTNESS(led_9.name, int(brightness_9))
                
            return ""
        
        
        except Exception as e:
            WRITE_LOGFILE_SYSTEM("ERROR", "LED | Set Brightness | " + str(e))
            SEND_EMAIL("ERROR", "LED | Set Brightness | " + str(e))            
            return [str(e)]

    else:
        return ["Keine LED-Steuerung aktiviert"]  


def LED_GROUP_TURN_OFF(group_id):

    if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") == "True":

        try:
            group = GET_LED_GROUP_BY_ID(group_id)
            
            # led 1
            SETTING_LED_TURN_OFF(group.led_name_1)
                
            # led 2
            if group.active_led_2 == "True": 
                SETTING_LED_TURN_OFF(group.led_name_2)
            # led 3
            if group.active_led_3 == "True": 
                SETTING_LED_TURN_OFF(group.led_name_3)
            # led 4
            if group.active_led_4 == "True": 
                SETTING_LED_TURN_OFF(group.led_name_4)
            # led 5
            if group.active_led_5 == "True": 
                SETTING_LED_TURN_OFF(group.led_name_5)
            # led 6
            if group.active_led_6 == "True": 
                SETTING_LED_TURN_OFF(group.led_name_6)
            # led 7
            if group.active_led_7 == "True": 
                SETTING_LED_TURN_OFF(group.led_name_7)
            # led 8
            if group.active_led_8 == "True": 
                SETTING_LED_TURN_OFF(group.led_name_8)
            # led 9
            if group.active_led_9 == "True": 
                SETTING_LED_TURN_OFF(group.led_name_9)
            
            return ""

        except Exception as e:
            WRITE_LOGFILE_SYSTEM("ERROR", "LED | Turn_off | " + str(e))
            SEND_EMAIL("ERROR", "LED | Turn_off | " + str(e))            
            return [str(e)]

    else:
        return ["Keine LED-Steuerung aktiviert"]  
        
