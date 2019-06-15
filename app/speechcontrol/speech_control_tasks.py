
import heapq

from app import app
from app.components.control_led import *
from app.database.database import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL
from app.components.shared_resources import process_management_queue
from app.components.mqtt import *


""" #################### """
""" speech control tasks """
""" #################### """

def SPEECH_RECOGNITION_PROVIDER_TASKS(answer):

    print(answer)
    
    # exception
    if ("could not understand audio" in answer) or ("Could not request results" in answer):
        WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control | " + answer)
        
    else:
        WRITE_LOGFILE_SYSTEM("EVENT", 'Speech Control | Detection Task | ' + answer)
        
        START_LED_TASK(answer)
        START_DEVICE_TASK(answer)
        
        

# #########
# LED Tasks
# #########
    
def START_LED_TASK(answer):
    
    
    # ###########
    # start scene 
    # ###########
    
    keywords = GET_SPEECH_CONTROL_LED_TASK_BY_ID(1).keywords
        
    try:
        list_keywords = keywords.split(",")
    except:
        list_keywords = [keywords]

    for keyword in list_keywords:
        
        keyword = keyword.replace(" ", "")
        
        # keyword founded
        if keyword.lower() in answer:

            try:
                groups = GET_ALL_LED_GROUPS()
                scenes = GET_ALL_LED_SCENES() 

                group_id   = None
                scene_id   = None
                brightness = 100

                # search group
                for group in groups:
                    if group.name.lower() in answer:
                        group_id = group.id

                # search scene
                for scene in scenes:
                    if scene.name.lower() in answer:
                        scene_name = scene.name  

                # search brightness value
                for element in answer.split():
                    element = element.replace("%","")
                    
                    # check value
                    if element.isdigit() and (1 <= int(element) <= 100):
                        brightness = int(element)
                     
                # group and scene founded
                if group_id != None and scene_name != None:   
                    
                    group = GET_LED_GROUP_BY_ID(group_id)
                    scene = GET_LED_SCENE_BY_NAME(scene_name)  
                    
                    # new led setting ?
                    if group.current_setting != scene_name and int(group.current_brightness) != brightness:

                        LED_SET_SCENE(group_id, scene.id, brightness)
                        LED_ERROR_CHECKING_THREAD(group_id, scene.id, scene_name, brightness, 3, 15)      

                    else:
                        WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | " + scene_name + " : " + str(brightness) + " %")     
                                    
                    time.sleep(1)
                    break
       
            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control | LED Task | " + answer + " | " + str(e))  
                break
         
                
    # ##############
    # set brightness
    # ##############
    
    keywords = GET_SPEECH_CONTROL_LED_TASK_BY_ID(2).keywords
    
    try:
        list_keywords = keywords.split(",")
    except:
        list_keywords = [keywords]

    for keyword in list_keywords:
        
        keyword = keyword.replace(" ", "")
        
        # keyword founded
        if keyword.lower() in answer:

            try:
                groups = GET_ALL_LED_GROUPS()

                # search group
                for group in groups:
                    
                    # group founded
                    if group.name.lower() in answer:
                        
                        # search brightness value
                        for element in answer.split():
                            element = element.replace("%","")
                            if element.isdigit():
                                brightness = int(element)
                             
                        # check brightness value
                        if 1 <= brightness <= 100:
                            
                            # led_group off ?
                            if group.current_setting != "OFF":
                            
                                scene_name = group.current_setting
                                scene      = GET_LED_SCENE_BY_NAME(scene_name)                            
                            
                                # new led setting ?
                                if group.current_brightness != brightness:
                                    
                                    LED_SET_BRIGHTNESS(group.id, brightness)
                                    LED_ERROR_CHECKING_THREAD(group.id, scene.id, scene_name, brightness, 3, 15)       

                                else:
                                    WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | " + scene_name + " : " + str(brightness) + " %") 	
                                    
                            else:
                                WRITE_LOGFILE_SYSTEM("WARNING", "LED | Group - " + group.name + " | OFF : 0 %") 	                                   
                              
                            time.sleep(1)
                            break

            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control | LED Task | " + answer + " | " + str(e))    
                break
    
    
    # ##################
    # turn off led group
    # ##################
    
    keywords = GET_SPEECH_CONTROL_LED_TASK_BY_ID(3).keywords
    
    try:
        list_keywords = keywords.split(",")
    except:
        list_keywords = [keywords]

    for keyword in list_keywords:
        
        keyword = keyword.replace(" ", "")
                   
        # keyword founded
        if keyword.lower() in answer:

            try:
                groups = GET_ALL_LED_GROUPS()

                founded_groups = []

                # search group
                for group in groups:
                    if group.name.lower() in answer:
                        founded_groups.append(group)          

                # group founded
                if founded_groups != []:
                    
                    for group in founded_groups:
                        
                        scene_name = group.current_setting
                        scene      = GET_LED_SCENE_BY_NAME(scene_name)

                        # new led setting ?
                        if group.current_setting != "OFF":
                            
                            LED_TURN_OFF_GROUP(group.id)
                            LED_ERROR_CHECKING_THREAD(group.id, scene.id, "OFF", 0, 3, 15)       

                        else:
                            WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %") 	
                        
                time.sleep(1)
                break

            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control | LED Task | " + answer + " | " + str(e))    
                break
                    

    # #################
    # turn off all leds
    # #################
    
    keywords = GET_SPEECH_CONTROL_LED_TASK_BY_ID(4).keywords
    
    try:
        list_keywords = keywords.split(",")
    except:
        list_keywords = [keywords]

    for keyword in list_keywords:
        
        keyword = keyword.replace(" ", "")
                   
        # keyword founded           
        if keyword.lower() in answer:

            try:
                
                # check all led groups
                for group in GET_ALL_LED_GROUPS():

                    scene_name = group.current_setting
                    scene      = GET_LED_SCENE_BY_NAME(scene_name)

                    # new led setting ?
                    if group.current_setting != "OFF":

                        LED_TURN_OFF_GROUP(group.id)
                        LED_ERROR_CHECKING_THREAD(group.id, scene.id, "OFF", 0, 3, 15)       

                    else:
                        WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %") 
                    
                time.sleep(1)
                break

            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control | LED Task | " + answer + " | " + str(e))    
                break
                    
                
                    
def START_DEVICE_TASK(answer):
    
    
    # ############
    # Device Tasks
    # ############       
    
    for task in GET_ALL_SPEECH_CONTROL_DEVICE_TASKS():
        
        try:
            list_keywords = task.keywords.split(",")
        except:
            list_keywords = [keywords]

        for keyword in list_keywords:
            
            keyword = keyword.replace(" ", "")
                       
            if keyword.lower() in answer:
                
                try:      
                    device = GET_MQTT_DEVICE_BY_IEEEADDR(task.mqtt_device_ieeeAddr)
                    
                    # new device setting ?
                    if task.command != device.previous_command:

                        if device.gateway == "mqtt":

                            channel = "SmartHome/mqtt/" + device.ieeeAddr + "/set"
                            msg     = '{"state": "' + task.command + '"}'

                            MQTT_PUBLISH(channel, msg) 
                            MQTT_CHECK_SETTING_THREAD(device.ieeeAddr, "state", task.command, 5, 20)


                        if device.gateway == "zigbee2mqtt":

                            channel = "SmartHome/zigbee2mqtt/" + device.name + "/set"
                            msg     = '{"state": "' + task.command + '"}'

                            MQTT_PUBLISH(channel, msg) 
                            ZIGBEE2MQTT_CHECK_SETTING_THREAD(device.name, "state", task.command, 5, 20)

                    else:

                        if device.gateway == "mqtt":
                            WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + device.name + " | " + task.command) 

                        if device.gateway == "zigbee2mqtt":
                            WRITE_LOGFILE_SYSTEM("STATUS", "Zigbee2MQTT | Device - " + device.name + " | " + task.command)  
                            
                                
                    time.sleep(1)
                    break
                    
                except Exception as e:
                    print(e)
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control | Device Task | " + answer + " | " + str(e))      
                    break                    
                    
