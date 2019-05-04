"""

https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py

"""

from app import app
from app.database.database import GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS
from app.components.led_control import *
from app.database.database import *

import speech_recognition as sr


def SPEECH_RECOGNITION_PROVIDER():

    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)


    ###########################
    ### Google Cloud Speech ###
    ###########################

    if GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider == "Google Cloud Speech":

        """INSERT THE CONTENTS OF THE GOOGLE CLOUD SPEECH JSON CREDENTIALS FILE HERE"""
        GOOGLE_CLOUD_SPEECH_CREDENTIALS = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_key

        try: 
            answer = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
            answer = answer.lower()
            answer = answer.replace("ß", "ss")  
            SPEECH_RECOGNITION_PROVIDER_TASKS(answer)
            return (answer)
            
        except sr.UnknownValueError:
            return ("Google Cloud Speech could not understand audio")

        except sr.RequestError as e:
            return ("Could not request results from Google Cloud Speech service; {0}".format(e))


    #################################
    ### Google Speech Recognition ###
    #################################

    if GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider == "Google Speech Recognition":

        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`

            answer = r.recognize_google(audio)
            answer = answer.lower()
            answer = answer.replace("ß", "ss")  
            SPEECH_RECOGNITION_PROVIDER_TASKS(answer)
            return (answer)
            
        except sr.UnknownValueError:
            return ("Google Speech Recognition could not understand audio")
            
        except sr.RequestError as e:
            return ("Could not request results from Google Speech Recognition service; {0}".format(e))


    ################
    ### Houndify ###
    ################

    if GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider == "Houndify":

        # Houndify client IDs are Base64-encoded strings
        HOUNDIFY_CLIENT_ID = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_username
        # Houndify client keys are Base64-encoded strings
        HOUNDIFY_CLIENT_KEY = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_key

        try:
            answer = r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID, client_key=HOUNDIFY_CLIENT_KEY)
            answer = answer.lower()
            answer = answer.replace("ß", "ss")  
            SPEECH_RECOGNITION_PROVIDER_TASKS(answer)
            return (answer)
            
        except sr.UnknownValueError:
            return ("Houndify could not understand audio")

        except sr.RequestError as e:
            return ("Could not request results from Houndify service; {0}".format(e))


    ##########################
    ### IBM Speech to Text ###
    ##########################

    if GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider == "IBM Speech to Text":

        # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
        IBM_USERNAME = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_username
        # IBM Speech to Text passwords are mixed-case alphanumeric strings
        IBM_PASSWORD = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_key   

        try:
            answer = r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD)
            answer = answer.lower()
            answer = answer.replace("ß", "ss")  
            SPEECH_RECOGNITION_PROVIDER_TASKS(answer)
            return (answer)
            
        except sr.UnknownValueError:
            return ("IBM Speech to Text could not understand audio")

        except sr.RequestError as e:
            return ("Could not request results from IBM Speech to Text service; {0}".format(e))


    ##############################
    ### Microsoft Azure Speech ###
    ##############################

    if GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider == "Microsoft Azure Speech":

        # Microsoft Speech API keys 32-character lowercase hexadecimal strings
        AZURE_SPEECH_KEY = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_key  

        try:
            answer = r.recognize_azure(audio, key=AZURE_SPEECH_KEY)
            answer = answer.lower()
            answer = answer.replace("ß", "ss")  
            SPEECH_RECOGNITION_PROVIDER_TASKS(answer)
            return (answer)

        except sr.UnknownValueError:
            return ("Microsoft Azure Speech could not understand audio")

        except sr.RequestError as e:
            return ("Could not request results from Microsoft Azure Speech service; {0}".format(e))


    ########################################
    ### Microsoft Bing Voice Recognition ###
    ########################################

    if GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider == "Microsoft Bing Voice Recognition":

        # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings
        BING_KEY = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_key  

        try:
            answer = r.recognize_bing(audio, key=BING_KEY)
            answer = answer.lower()
            answer = answer.replace("ß", "ss")            
            SPEECH_RECOGNITION_PROVIDER_TASKS(answer)
            return (answer)
            
        except sr.UnknownValueError:
            return ("Microsoft Bing Voice Recognition could not understand audio")

        except sr.RequestError as e:
            return ("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))


    ##############
    ### Wit.ai ###
    ##############

    if GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider == "Wit.ai":

        # Wit.ai keys are 32-character uppercase alphanumeric strings
        WIT_AI_KEY = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_key

        try:
            answer = r.recognize_wit(audio, key=WIT_AI_KEY)
            answer = answer.lower()
            answer = answer.replace("ß", "ss")
            SPEECH_RECOGNITION_PROVIDER_TASKS(answer)
            return (answer)

        except sr.UnknownValueError:
            return ("Wit.ai could not understand audio")

        except sr.RequestError as e:
            return ("Could not request results from Wit.ai service; {0}".format(e))


""" ######################## """
""" speech recognition tasks """
""" ######################## """


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

                    for group in groups:
                        if group.name.lower() in answer:
                            group_id = group.id

                    for scene in scenes:
                        if scene.name.lower() in answer:
                            scene_id = scene.id   

                    print(group_id)
                    print(scene_id)

                    if group_id != None and scene_id != None:                    
                        error_message = LED_START_SCENE(int(group_id), int(scene_id))            
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

                    for group in groups:
                        if group.name.lower() in answer:
                            group_id = group.id

                    for program in programs:
                        if program.name.lower() in answer:
                            program_id = program.id   

                    print(group_id)
                    print(program_id)

                    if group_id != None and program_id != None:                    
                        error_message = LED_START_PROGRAM_THREAD(int(group_id), int(program_id))            
                        if error_message != "":
                            WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + error_message) 
                            
                    break
           
                except Exception as e:
                    print(e)
                    WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Task | " + answer + " | " + str(e))  
                    
                    break


        # turn off led 
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
                        
                  
