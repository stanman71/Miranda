from app import app
from app.components.control_led import *
from app.database.database import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL


""" #################### """
""" speech control tasks """
""" #################### """

def SPEECH_RECOGNITION_PROVIDER_TASKS(answer):

    print(answer)
    
    # exception
    if ("could not understand audio" in answer) or ("Could not request results" in answer):
        WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition | " + answer)
        
    else:
        
        WRITE_LOGFILE_SYSTEM("EVENT", 'Speech Recognition | Detection Task | ' + answer)

        # start scene 
        keywords = GET_SPEECH_RECOGNITION_PROVIDER_TASK_BY_ID(1).keywords
            
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
                        error_message = LED_START_SCENE(int(group_id), int(scene_id), brightness)            
                        if error_message != "":
                            WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + error_message) 
                            
                    break
           
                except Exception as e:
                    print(e)
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + str(e))  
                    
                    break


        # start program 
        keywords = GET_SPEECH_RECOGNITION_PROVIDER_TASK_BY_ID(2).keywords
        
        try:
            list_keywords = keywords.split(",")
        except:
            list_keywords = [keywords]

        for keyword in list_keywords:
            
            keyword = keyword.replace(" ", "")
                       
            if keyword.lower() in answer:

                try:
                    groups   = GET_ALL_LED_GROUPS()
                    programs = GET_ALL_LED_PROGRAMS() 

                    group_id   = None
                    program_id = None

                    # search group
                    for group in groups:
                        if group.name.lower() in answer:
                            group_id = group.id

                    # search program
                    for program in programs:
                        if program.name.lower() in answer:
                            program_id = program.id   

                    if group_id != None and program_id != None:                    
                        error_message = LED_START_PROGRAM_THREAD(int(group_id), int(program_id))            
                        if error_message != "":
                            WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + error_message) 
                            
                    break
           
                except Exception as e:
                    print(e)
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + str(e))  
                    
                    break


        # set brightness
        keywords = GET_SPEECH_RECOGNITION_PROVIDER_TASK_BY_ID(3).keywords
        
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
                                error_message = LED_SET_BRIGHTNESS(int(group.id), int(brightness))     
                                                 
                                if error_message != "":            
                                    WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + error_message)                    
                       
                        break

                except Exception as e:
                    print(e)
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + str(e))    
                    
                    break


        # turn off led group
        keywords = GET_SPEECH_RECOGNITION_PROVIDER_TASK_BY_ID(4).keywords
        
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
                            error_message = LED_TURN_OFF_GROUP(int(group_id))
                            if error_message != "":            
                                WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + error_message)                    
                   
                    
                    else:
                        error_message = LED_TURN_OFF_ALL()   
                        if error_message != "":            
                            WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + error_message)
                            
                    break

                except Exception as e:
                    print(e)
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + str(e))    
                    
                    break
                        

        # turn off all leds
        keywords = GET_SPEECH_RECOGNITION_PROVIDER_TASK_BY_ID(5).keywords
        
        try:
            list_keywords = keywords.split(",")
        except:
            list_keywords = [keywords]

        for keyword in list_keywords:
            
            keyword = keyword.replace(" ", "")
                       
            if keyword.lower() in answer:

                try:
        
                    error_message = LED_TURN_OFF_ALL()   
                    if error_message != "":            
                        WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + error_message)
                            
                    break

                except Exception as e:
                    print(e)
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + str(e))    
                    
                    break
                        
