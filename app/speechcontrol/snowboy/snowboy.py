from app import app

from app.speechcontrol.snowboy import snowboydetect
from app.speechcontrol.snowboy import snowboydecoder
from app.speechcontrol.speech_recognition_provider import SPEECH_RECOGNITION_PROVIDER
from app.database.database import *
from app.components.file_management import *
from app.components.led_control import *
from app.components.pixel_ring import PIXEL_RING_CONTROL


import sys
import signal

from threading import Thread

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
            PIXEL_RING_CONTROL("on")
            SPEECH_RECOGNITION_PROVIDER()
            time.sleep(5)
            PIXEL_RING_CONTROL("off")
            detector.start(detected_callback=detect_callback, interrupt_check=interrupt_callback, sleep_time=0.03)

         WRITE_LOGFILE_SYSTEM("EVENT", "Speech Recognition Provider | started") 

         # main loop
         detector.start(detected_callback=detect_callback,
                        interrupt_check=interrupt_callback,
                        sleep_time=0.03)

         detector.terminate()

      else:
         WRITE_LOGFILE_SYSTEM("ERROR", "Speech Recognition Provider | Snowboy Hotword - " + hotword_file + " | not founded")

""" ############# """
""" snowboy tasks """
""" ############# """

snowboy_detect_on = False

def SNOWBOY_TASKS(entry):
   
   global snowboy_detect_on
   
   WRITE_LOGFILE_SYSTEM("EVENT", 'Snowboy | Detection | Task - ' + str(entry.task))
   
   # activate command mode
   if "snowboy_active" in entry.task:
      snowboy_detect_on = True
      PIXEL_RING_CONTROL("on")

      # set snowboy_detect_on to False after selected delay
      class waiter(Thread):
         def run(self):
            global detect
            time.sleep(GET_SNOWBOY_SETTINGS().delay)
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")
      waiter().start()
  
   try:  
      # start scene  
      if "scene" in entry.task and snowboy_detect_on == True:
         try:
            task = entry.task.split(":")
            group_id = GET_LED_GROUP_BY_NAME(task[1]).id
            scene_id = GET_LED_SCENE_BY_NAME(task[2]).id      
            error_message = LED_START_SCENE(int(group_id), int(scene_id), int(task[3]))  
               
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")         
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]
               WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy | Task - " + entry.name + " | " + error_message)     
         
         except:
            task = entry.task.split(":")
            group_id = GET_LED_GROUP_BY_NAME(task[1]).id
            scene_id = GET_LED_SCENE_BY_NAME(task[2]).id          
            error_message = LED_START_SCENE(int(group_id), int(scene_id))   
            
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")   
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]                    
               WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy | Task - " + entry.name + " | " + error_message)
               
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy | Task - " + entry.name + " | " + str(e))     
         
   try:
      # start program
      if "program" in entry.task and snowboy_detect_on == True:
         task = entry.task.split(":")
         group_id = GET_LED_GROUP_BY_NAME(task[1]).id
         program_id = GET_LED_PROGRAM_BY_NAME(task[2]).id
         error_message = LED_START_PROGRAM_THREAD(int(group_id), int(program_id))  
         
         snowboy_detect_on = False
         PIXEL_RING_CONTROL("off")   
         
         if error_message != "":
            error_message = str(error_message)
            error_message = error_message[1:]
            error_message = error_message[:-1]                    
            WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy | Task - " + entry.name + " | " + error_message)
         
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy | Task - " + entry.name + " | " + str(e))     
     

   # led off
   try:
      if "led_off" in entry.task:
         task = entry.task.split(":")
         if task[1] == "group":
            
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")             
            
            # get input group names and lower the letters
            try:
                list_groups = task[2].split(",")
            except:
                list_groups = [task[2]]

            for input_group_name in list_groups:
                
               input_group_name = input_group_name.replace(" ", "")
               input_group_name = input_group_name.lower()

               # get exist group names and lower the letters
               try:
                  all_exist_group = GET_ALL_LED_GROUPS()
                  
                  for exist_group in all_exist_group:
                     
                     exist_group_name       = exist_group.name
                     exist_group_name_lower = exist_group_name.lower()
                     
                     # compare the formated names
                     if input_group_name == exist_group_name_lower:                       
                        group_id = GET_LED_GROUP_BY_NAME(exist_group_name).id
                        error_message = LED_TURN_OFF_GROUP(int(group_id))
                  
                        if error_message != "":
                           error_message = str(error_message)
                           error_message = error_message[1:]
                           error_message = error_message[:-1]                    
                           WRITE_LOGFILE_SYSTEM("ERROR", "SSnowBoy | Task - " + entry.name + " | " + error_message)
                 
                     else:
                        WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy | Task - " + entry.name + " | Group - " + input_group_name + " | not founded")
                 
                     
               except:
                  WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy | Task - " + entry.name + " | Group - " + input_group_name + " | not founded")
                  
               
         if task[1] == "all":
            error_message = LED_TURN_OFF_ALL()   
            
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")            
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]                   
               WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy | Task - " + entry.name + " | " + error_message)
      
             
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy | Task - " + entry.name + " | " + str(e))      
