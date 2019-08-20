import heapq
import re

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.process_scheduler import SCHEDULER_TIME_PROCESS, SCHEDULER_SENSOR_PROCESS, SCHEDULER_PING_PROCESS
from app.components.process_controller import CONTROLLER_PROCESS
from app.components.mqtt import *
from app.components.backend_led import *
from app.components.shared_resources import process_management_queue
from app.components.tasks import START_SPEECHCONTROL_TASK
from app.components.backend_watering import START_WATERING_THREAD
from app.components.email import SEND_EMAIL

""" ################ """
""" management queue """
""" ################ """

# https://www.bogotobogo.com/python/python_PriorityQueue_heapq_Data_Structure.php

def PROCESS_MANAGEMENT_THREAD():

    try:
        Thread = threading.Thread(target=PROCESS_MANAGEMENT)
        Thread.start() 
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Thread | Process Management | " + str(e)) 
        SEND_EMAIL("ERROR", "Thread | Process Management | " + str(e))      


def PROCESS_MANAGEMENT():
    
    while True:
        
        try:
            process = heapq.heappop(process_management_queue)[1]
            
            
            # ############
            #  controller
            # ############
            
            if process[0] == "controller":
                ieeeAddr = process[1]
                msg      = process[2]
                
                CONTROLLER_PROCESS(ieeeAddr, msg)           
                
                
            # ###########
            #  dashboard
            # ###########
                
            if process[0] == "dashboard":
                    
                        
                if process[1] == "led_scene":
                    group_id          = process[2]
                    scene_id          = process[3] 
                    brightness_global = process[4]
                    
                    SET_LED_GROUP_SCENE(group_id, scene_id, brightness_global)
                
                
                if process[1] == "led_brightness":
                    group_id          = process[2]
                    brightness_global = process[3]  
                                    
                    SET_LED_GROUP_BRIGHTNESS(group_id, brightness_global)
                    
                    
                if process[1] == "led_off_group":
                    group_id          = process[2]
                                        
                    SET_LED_GROUP_TURN_OFF(group_id)
                
                
                if process[1] == "device":
                    channel = process[2]
                    msg     = process[3]
                    
                    MQTT_PUBLISH(channel, msg)                  
    
    
            # #########
            #  program
            # #########
    
            if process[0] == "program":
                
                
                if process[1] == "device":
                    MQTT_PUBLISH(process[2], process[3])    
                    
                    
                if process[1] == "led_rgb": 
                    led_name      = process[2]
                    rgb_values    = re.findall(r'\d+', process[3])
                    led_brightnes = process[4]
                    
                    SET_LED_BULB_RGB(led_name, rgb_values[0], rgb_values[1], rgb_values[2], led_brightnes)
                    
                    CHECK_ZIGBEE2MQTT_SETTING_THREAD(led_name, '{"brightness":' + str(led_brightnes) + '}', 3, 10)
                
                
                if process[1] == "led_white":
                    led_name      = process[2]
                    color_temp    = process[3]
                    led_brightnes = process[4]      
                            
                    SET_LED_BULB_WHITE(led_name, color_temp, led_brightness)
                    
                    CHECK_ZIGBEE2MQTT_SETTING_THREAD(led_name, '{"brightness":' + str(led_brightness) + '}', 3, 10)
                    
                    
                if process[1] == "led_simple":
                    led_name       = process[2]
                    led_brightness = process[3] 
                                    
                    SET_LED_BULB_SIMPLE(led_name, led_brightness)
                    
                    CHECK_ZIGBEE2MQTT_SETTING_THREAD(led_name, '{"brightness":' + str(led_brightness) + '}', 3, 10)


                if process[1] == "turn_off":
                    led_name      = process[2]
                    
                    SET_LED_BULB_TURN_OFF(led_name)
                    
                    CHECK_ZIGBEE2MQTT_SETTING_THREAD(led_name, '{"state":"OFF"}', 3, 10)
                    
                    
                if process[1] == "led_group":
                    led_group_name = process[2]
                    scene_name     = process[3]
                    
                    group_id = GET_LED_GROUP_BY_NAME(led_group_name).id
                    
                    if scene_name == "turn_off":
                        SET_LED_GROUP_TURN_OFF(int(group_id))
                        
                        CHECK_LED_GROUP_SETTING_PROCESS(int(group_id), 0, "OFF", 0, 3, 10) 
                        
                    else:
                        scene_id          = GET_LED_SCENE_BY_NAME(scene_name).id
                        brightness_global = process[4]
                        
                        SET_LED_GROUP_SCENE(int(group_id), int(scene_id), int(brightness_global))
                        
                        CHECK_LED_GROUP_SETTING_PROCESS(int(group_id), int(scene_id), scene_name, int(brightness_global), 3, 10)
                    
                    
            # ###########
            #  scheduler
            # ###########
                                    
            if process[0] == "scheduler":
                
                
                if process[1] == "time":
                    task = GET_SCHEDULER_TASK_BY_ID(process[2])
                    
                    SCHEDULER_TIME_PROCESS(task)
            
            
                if process[1] == "ping":
                    task = GET_SCHEDULER_TASK_BY_ID(process[2])
                    
                    SCHEDULER_PING_PROCESS(task)    
                        
                        
                if process[1] == "sensor":
                    task     = GET_SCHEDULER_TASK_BY_ID(process[2])
                    ieeeAddr = process[3]
                    
                    SCHEDULER_SENSOR_PROCESS(task, ieeeAddr)                 


            # ###############
            #  speechcontrol
            # ###############

            if process[0] == "speechcontrol":
                speech_recognition_answer = process[1]
                
                START_SPEECHCONTROL_TASK(speech_recognition_answer)                     
            
                
            # ##########
            #  watering
            # ##########
                
            if process[0] == "watering" and process[1] != "start":
                channel = process[1]
                msg     = process[2]
                
                MQTT_PUBLISH(channel, msg)  
                
                
        except Exception as e:
            
            try:
            
                if "index out of range" not in str(e):
                    WRITE_LOGFILE_SYSTEM("ERROR", "Process Management | Process - " + process + " | " + str(e))  
                    SEND_EMAIL("ERROR", "Process Management | Process - " + process + " | " + str(e))               
                    print(str(e))
                    
            except:
                pass
                
              
        time.sleep(0.2)
   
