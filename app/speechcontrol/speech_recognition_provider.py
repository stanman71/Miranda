
# https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py

import speech_recognition as sr

from app import app
from app.database.database import *


def SPEECH_RECOGNITION_PROVIDER(timeout_value):

    try:
        
        # obtain audio from the microphone
        r = sr.Recognizer()
        
        # set volume level
        r.dynamic_energy_threshold = False
        r.energy_threshold = 400

        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source, timeout=timeout_value)


        ###########################
        ### Google Cloud Speech ###
        ###########################

        if GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider == "Google Cloud Speech":

            """INSERT THE CONTENTS OF THE GOOGLE CLOUD SPEECH JSON CREDENTIALS FILE HERE"""
            GOOGLE_CLOUD_SPEECH_CREDENTIALS = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_key

            try: 
                speech_recognition_answer = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)
                speech_recognition_answer = speech_recognition_answer.lower()
                speech_recognition_answer = speech_recognition_answer.replace("ß", "ss")  
                return (speech_recognition_answer)
                
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

                speech_recognition_answer = r.recognize_google(audio)
                speech_recognition_answer = speech_recognition_answer.lower()
                speech_recognition_answer = speech_recognition_answer.replace("ß", "ss")  
                return (speech_recognition_answer)
                
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
                speech_recognition_answer = r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID, client_key=HOUNDIFY_CLIENT_KEY)
                speech_recognition_answer = speech_recognition_answer.lower()
                speech_recognition_answer = speech_recognition_answer.replace("ß", "ss")  
                return (speech_recognition_answer)
                
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
                speech_recognition_answer = r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD)
                speech_recognition_answer = speech_recognition_answer.lower()
                speech_recognition_answer = speech_recognition_answer.replace("ß", "ss")  
                return (speech_recognition_answer)
                
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
                speech_recognition_answer = r.recognize_azure(audio, key=AZURE_SPEECH_KEY)
                speech_recognition_answer = speech_recognition_answer.lower()
                speech_recognition_answer = speech_recognition_answer.replace("ß", "ss")  
                return (speech_recognition_answer)

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
                speech_recognition_answer = r.recognize_bing(audio, key=BING_KEY)
                speech_recognition_answer = speech_recognition_answer.lower()
                speech_recognition_answer = speech_recognition_answer.replace("ß", "ss")            
                return (speech_recognition_answer)
                
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
                speech_recognition_answer = r.recognize_wit(audio, key=WIT_AI_KEY)
                speech_recognition_answer = speech_recognition_answer.lower()
                speech_recognition_answer = speech_recognition_answer.replace("ß", "ss")
                return (speech_recognition_answer)

            except sr.UnknownValueError:
                return ("Wit.ai could not understand audio")

            except sr.RequestError as e:
                return ("Could not request results from Wit.ai service; {0}".format(e))

    except:
        pass
