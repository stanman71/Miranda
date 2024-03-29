from app.speechcontrol.snowboy import snowboydetect
from app.speechcontrol.snowboy import snowboydecoder
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL
from app.speechcontrol.speech_recognition_provider import SPEECH_RECOGNITION_PROVIDER

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.shared_resources import process_management_queue

import sys
import signal
import heapq
import time

interrupted = False

def signal_handler(signal, frame):
   global interrupted
   interrupted = True

def interrupt_callback():
   global interrupted
   return interrupted


def SNOWBOY_THREAD():

    signal.signal(signal.SIGINT, signal_handler)

    hotword_file = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().snowboy_hotword

    # check hotword files exist
    if hotword_file in GET_ALL_HOTWORD_FILES():
   
        # voice models here:
        models = GET_SPEECH_RECOGNITION_PROVIDER_HOTWORD(GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().snowboy_hotword)
      
        sensitivity_value = GET_SNOWBOY_SETTINGS().snowboy_sensitivity / 100

        # modify sensitivity for better detection / accuracy
        detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity_value)  
      
        def detect_callback():
            detector.terminate()
            MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().snowboy_microphone, "on")
     
            speech_recognition_answer = SPEECH_RECOGNITION_PROVIDER(GET_SNOWBOY_SETTINGS().snowboy_timeout)
     
            if speech_recognition_answer != None and speech_recognition_answer != "":
                
                if "could not" in speech_recognition_answer or "Could not" in speech_recognition_answer:     
                    pass
                    #WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | " + speech_recognition_answer) 
                
                else:    
                    heapq.heappush(process_management_queue, (1, ("speechcontrol", speech_recognition_answer)))

            MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().snowboy_microphone, "off")
            
            # pause snowboy
            set_led = True
            while GET_SNOWBOY_SETTINGS().snowboy_pause == "checked":

                if set_led:
                    MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().snowboy_microphone, "pause")
                    set_led = False
                time.sleep(1)
                
            MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().snowboy_microphone, "off") 

            detector.start(detected_callback=detect_callback, interrupt_check=interrupt_callback, sleep_time=0.03)


        WRITE_LOGFILE_SYSTEM("EVENT", "Speechcontrol | Started") 

        # pause snowboy
        set_led = True
        while GET_SNOWBOY_SETTINGS().snowboy_pause == "checked":

            if set_led:
                MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().snowboy_microphone, "pause")
                set_led = False
            time.sleep(1)
            
        MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().snowboy_microphone, "off") 

        # main loop
        detector.start(detected_callback=detect_callback,
                        interrupt_check=interrupt_callback,
                        sleep_time=0.03)

        detector.terminate()

    else:
        WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Snowboy Hotword - " + hotword_file + " | Not founded")
