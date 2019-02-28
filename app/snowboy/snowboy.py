from app import app

from app.snowboy import snowboydetect
from app.snowboy import snowboydecoder
from app.components.led_control import LED_SET_SCENE, START_PROGRAM, LED_OFF
from app.database.database import GET_SENSITIVITY, GET_ALL_SNOWBOY_TASKS

import sys
import signal
import os
import time

from threading import Thread

interrupted = False
detect = False

def signal_handler(signal, frame):
   global interrupted
   interrupted = True

def interrupt_callback():
   global interrupted
   return interrupted

def SNOWBOY_TASKS(entry):
   
   global detect
   
   # activate command mode
   if "snowboy_active" in entry.task:
      detect = True

      # set detect to False after 5 seconds
      class waiter(Thread):
         def run(self):
            global detect
            time.sleep(5)
            detect = False
      waiter().start()
  
   # start scene
   if "start_scene" in entry.task and detect == True:
      task = entry.task.split(":")
      try:
            LED_SET_SCENE(int(task[1]), int(task[2]))
            detect = False
      except:
            LED_SET_SCENE(int(task[1]))
            detect = False

   # start program
   if "start_program" in entry.task and detect == True:
      task = entry.task.split(":")
      START_PROGRAM(int(task[1]))
      detect = False

   # turn off leds
   if "led_off" in entry.task and detect == True:
      task = entry.task.split(":")
      LED_OFF(int(task[1]))   
      detect = False 


def SNOWBOY_START():

   signal.signal(signal.SIGINT, signal_handler)

   # get hotword files
   file_list = []
   for element in GET_ALL_SNOWBOY_TASKS():
      file_list.append("/home/pi/Python/SmartHome/app/snowboy/resources/" + element.name + ".pmdl")

   # voice models here:
   models = file_list

   sensitivity_value = int(GET_SENSITIVITY()) / 100

   # modify sensitivity for better detection / accuracy
   detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity_value)
   
   # put what should happen when snowboy detects hotword here:
   if len(GET_ALL_SNOWBOY_TASKS()) == 1:
      callbacks = [lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[0])]
   if len(GET_ALL_SNOWBOY_TASKS()) == 2:
      callbacks = [lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[0]), 
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[1])]
   if len(GET_ALL_SNOWBOY_TASKS()) == 3:
      callbacks = [lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[0]), 
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[1]),
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[2])]                
   if len(GET_ALL_SNOWBOY_TASKS()) == 4:
      callbacks = [lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[0]), 
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[1]),
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[2]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[3])]   
   if len(GET_ALL_SNOWBOY_TASKS()) == 5:
      callbacks = [lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[0]), 
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[1]),
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[2]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[3]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[4])] 
   if len(GET_ALL_SNOWBOY_TASKS()) == 6:
      callbacks = [lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[0]), 
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[1]),
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[2]), 
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[3]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[4]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[5])]  
   if len(GET_ALL_SNOWBOY_TASKS()) == 7:
      callbacks = [lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[0]), 
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[1]),
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[2]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[3]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[4]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[5]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[6])]
   if len(GET_ALL_SNOWBOY_TASKS()) == 8:
      callbacks = [lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[0]), 
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[1]),
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[2]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[3]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[4]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[5]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[6]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[7])] 
   if len(GET_ALL_SNOWBOY_TASKS()) == 9:
      callbacks = [lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[0]), 
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[1]),
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[2]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[3]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[4]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[5]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[6]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[7]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[8])] 
   if len(GET_ALL_SNOWBOY_TASKS()) == 10:
      callbacks = [lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[0]), 
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[1]),
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[2]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[3]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[4]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[5]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[6]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[7]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[8]),  
                   lambda: SNOWBOY_TASKS(GET_ALL_SNOWBOY_TASKS()[9])]
      
                
   #without "lambda", callback will run immediately on startup, 
   #and then after each hotword detection:
   #callbacks = [os.system("/home/pi/test.sh")]

   print('Listening...')

   # main loop
   detector.start(detected_callback=callbacks,
                  interrupt_check=interrupt_callback,
                  sleep_time=0.03)

   detector.terminate()

