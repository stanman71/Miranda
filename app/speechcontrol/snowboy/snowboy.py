from app import app

from app.speechcontrol.snowboy import snowboydetect
from app.speechcontrol.snowboy import snowboydecoder
from app.speechcontrol.speech_recognition_provider import SPEECH_RECOGNITION_PROVIDER
from app.database.database import *
from app.components.file_management import *
from app.speechcontrol.speech_control_tasks import SNOWBOY_TASKS
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL

import sys
import signal

interrupted = False

def signal_handler(signal, frame):
   global interrupted
   interrupted = True

def interrupt_callback():
   global interrupted
   return interrupted


def SNOWBOY_START(modus):

   signal.signal(signal.SIGINT, signal_handler)

   sensitivity_value = GET_SNOWBOY_SETTINGS().sensitivity / 100
   
   
   #########
   # snowboy
   ######### 

   if modus == "snowboy":
      
      missing_hotwords = CHECK_HOTWORD_FILE_EXIST(GET_ALL_SNOWBOY_TASKS())
      
      # check hotword files exist
      if missing_hotwords == "":
         
         # voice models here:
         models = GET_HOTWORD_FILES_FROM_TASKS(GET_ALL_SNOWBOY_TASKS())

         sensitivity_value = GET_SNOWBOY_SETTINGS().sensitivity / 100

         # modify sensitivity for better detection / accuracy
         detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity_value)
         
         # put what should happen when snowboy detects hotword here:
         callback_list = [lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[0]), 
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[1]),
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[2]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[3]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[4]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[5]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[6]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[7]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[8]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[9]),
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[10]), 
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[11]),
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[12]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[13]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[14]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[15]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[16]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[17]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[18]),  
                          lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[19])]

         callbacks = callback_list[:len(GET_ALL_SNOWBOY_TASKS())]
         
         print('Listening...')
         WRITE_LOGFILE_SYSTEM("EVENT", "Snowboy | started") 
            
         # main loop
         detector.start(detected_callback=callbacks,
                        interrupt_check=interrupt_callback,
                        sleep_time=0.03)
         
         detector.terminate()
      
         
      else:
         WRITE_LOGFILE_SYSTEM("ERROR", "Snowboy | Hotwords - " + str(missing_hotwords) + " | not founded")


   #############################
   # speech_recognition_provider
   ############################# 

   if modus == "speech_recognition_provider":
      
      hotword_file = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().snowboy_hotword
      
      # check hotword files exist
      if hotword_file in GET_ALL_HOTWORD_FILES():
      
         # voice models here:
         models = GET_SPEECH_RECOGNITION_PROVIDER_HOTWORD(GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().snowboy_hotword)
         
         sensitivity_value = GET_SNOWBOY_SETTINGS().sensitivity / 100

         # modify sensitivity for better detection / accuracy
         detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity_value)  
         
         def detect_callback():
            detector.terminate()
            MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().microphone, "on")
            SPEECH_RECOGNITION_PROVIDER()
            time.sleep(GET_SNOWBOY_SETTINGS().delay)
            MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().microphone, "off")

            detector.start(detected_callback=detect_callback, interrupt_check=interrupt_callback, sleep_time=0.03)

         WRITE_LOGFILE_SYSTEM("EVENT", "Speech Recognition Provider | started") 

         # main loop
         detector.start(detected_callback=detect_callback,
                        interrupt_check=interrupt_callback,
                        sleep_time=0.03)

         detector.terminate()

      else:
         WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Provider | Snowboy Hotword - " + hotword_file + " | not founded")

  
