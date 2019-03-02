from app import app

from app.snowboy import snowboydetect
from app.snowboy import snowboydecoder
from app.database.database import *
from app.components.tasks import SNOWBOY_TASKS

import sys
import signal
import os

PATH = "/home/pi/Python/SmartHome"

interrupted = False

def signal_handler(signal, frame):
   global interrupted
   interrupted = True

def interrupt_callback():
   global interrupted
   return interrupted


def SNOWBOY_START():
   signal.signal(signal.SIGINT, signal_handler)

   # get hotword files
   file_list = []
   for element in GET_ALL_SNOWBOY_TASKS():
      file_list.append(PATH + "/app/snowboy/resources/" + element.name + ".pmdl")

   # voice models here:
   models = file_list

   # modify sensitivity for better detection / accuracy
   sensitivity_value = int(GET_SENSITIVITY()) / 100
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

   # cut callback_list as needed
   callbacks = callback_list[:len(GET_ALL_SNOWBOY_TASKS())]
         
   print('Listening...')

   # main loop
   detector.start(detected_callback=callbacks,
                  interrupt_check=interrupt_callback,
                  sleep_time=0.03)

   detector.terminate()

