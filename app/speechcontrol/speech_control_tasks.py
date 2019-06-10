
import heapq

from app import app
from app.components.control_led import *
from app.database.database import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL
from app.components.mqtt import MQTT_SET_DEVICE_SETTING
from app.components.shared_resources import process_management_queue


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
    
    # start scene 
    keywords = GET_SPEECH_CONTROL_LED_TASK_BY_ID(1).keywords
        
    try:
        list_keywords = keywords.split(",")
    except:
        list_keywords = [keywords]

    for keyword in list_keywords:
        
        keyword = keyword.replace(" ", "")
        
        if keyword.lower() in answer:

            try:
                groups = GET_ALL_LED_GROUPS()
                scenes = GET_ALL_LED_SCENES() 

                group_id = None
                scene_id = None
                brightness = 100

                # search group
                for group in groups:
                    if group.name.lower() in answer:
                        group_id = group.id

                # search scene
                for scene in scenes:
                    if scene.name.lower() in answer:
                        scene_id = scene.id   

                # search brightness value
                for element in answer.split():
                    element = element.replace("%","")
                    
                    # check value
                    if element.isdigit() and (1 <= int(element) <= 100):
                        brightness = int(element)
                     
                if group_id != None and scene_id != None:   
                    heapq.heappush(process_management_queue, (5, ("led_scene", int(group_id), int(scene_id), brightness)))                   
                    time.sleep(1)
                    break
       
            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control LED Task | " + answer + " | " + str(e))  
                break
                

    # set brightness
    keywords = GET_SPEECH_CONTROL_LED_TASK_BY_ID(2).keywords
    
    try:
        list_keywords = keywords.split(",")
    except:
        list_keywords = [keywords]

    for keyword in list_keywords:
        
        keyword = keyword.replace(" ", "")
                   
        if keyword.lower() in answer:

            try:
                groups = GET_ALL_LED_GROUPS()

                for group in groups:
                    if group.name.lower() in answer:
                        
                        # search brightness value
                        for element in answer.split():
                            element = element.replace("%","")
                            if element.isdigit():
                                brightness = element
                             
                        # check brightness value
                        if 1 <= int(brightness) <= 100:      
                            heapq.heappush(process_management_queue, (5, ("led_brightness", int(group.id), int(brightness))))    
                            time.sleep(1)
                            break

            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control LED Task | " + answer + " | " + str(e))    
                break


    # turn off led group
    keywords = GET_SPEECH_CONTROL_LED_TASK_BY_ID(3).keywords
    
    try:
        list_keywords = keywords.split(",")
    except:
        list_keywords = [keywords]

    for keyword in list_keywords:
        
        keyword = keyword.replace(" ", "")
                   
        if keyword.lower() in answer:

            try:
                groups = GET_ALL_LED_GROUPS()

                group_ids = []

                for group in groups:
                    if group.name.lower() in answer:
                        group_ids.append(group.id)          

              
                if group_ids != []:
                    
                    for group_id in group_ids:
                        heapq.heappush(process_management_queue, (5, ("led_off_group", int(group_id))))
                        time.sleep(1)
                
                else:
                    heapq.heappush(process_management_queue, (5, ("led_off_all", 0)))
                    time.sleep(1)
                    break

            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control LED Task | " + answer + " | " + str(e))    
                break
                    

    # turn off all leds
    keywords = GET_SPEECH_CONTROL_LED_TASK_BY_ID(4).keywords
    
    try:
        list_keywords = keywords.split(",")
    except:
        list_keywords = [keywords]

    for keyword in list_keywords:
        
        keyword = keyword.replace(" ", "")
                   
        if keyword.lower() in answer:

            try:
                heapq.heappush(process_management_queue, (5, ("led_off_all", 0)))
                time.sleep(1)
                break

            except Exception as e:
                print(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control LED Task | " + answer + " | " + str(e))    
                break
                    
            
# ############
# Device Tasks
# ############            
                    
def START_DEVICE_TASK(answer):
    
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
                    
                    if task.command != device.previous_command:
                        heapq.heappush(process_management_queue, (5, ("device", device.ieeeAddr, task.command.replace(" ",""))))
                        time.sleep(1)
                        break
                    
                except Exception as e:
                    print(e)
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control Device Task | " + answer + " | " + str(e))      
                    break                    
                    
