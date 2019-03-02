from app import app
from app.components.led_control import *
from app.database.database import *

import time
import datetime
import shutil
import os

from threading import Thread

PATH = "/home/pi/Python/SmartHome"

snowboy_detect_on = False

def SNOWBOY_TASKS(entry):
   
   global snowboy_detect_on
   
   # activate command mode
   if "snowboy_active" in entry.task:
      snowboy_detect_on = True

      # set snowboy_detect_on to False after 5 seconds
      class waiter(Thread):
         def run(self):
            global detect
            time.sleep(5)
            snowboy_detect_on = False
      waiter().start()
  
   # start scene
   if "start_scene" in entry.task and snowboy_detect_on == True:
      task = entry.task.split(":")
      try:
            LED_SET_SCENE(int(task[1]), int(task[2]))
            snowboy_detect_on = False
      except:
            LED_SET_SCENE(int(task[1]))
            snowboy_detect_on = False

   # start program
   if "start_program" in entry.task and snowboy_detect_on == True:
      task = entry.task.split(":")
      START_PROGRAM(int(task[1]))
      snowboy_detect_on = False

   # turn off leds
   if "led_off" in entry.task and snowboy_detect_on == True:
      task = entry.task.split(":")
      LED_OFF(int(task[1]))   
      snowboy_detect_on = False 


def SCHEDULAR_TASKS(entries):

   now    = datetime.datetime.now()
   day    = now.strftime('%a')
   hour   = now.strftime('%H')
   minute = now.strftime('%M')

   for entry in entries:
      if entry.day == day or entry.day == "*":
         if entry.hour == hour or entry.hour == "*":
            if entry.minute == minute or entry.minute == "*":
               print(entry.name)

               # start scene
               if "start_scene" in entry.task:
                  task = entry.task.split(":")
                  try:
                        LED_SET_SCENE(int(task[1]), int(task[2]))
                  except:
                        LED_SET_SCENE(int(task[1]))

               # start program
               if "start_program" in entry.task:
                  task = entry.task.split(":")
                  START_PROGRAM(int(task[1]))

               # turn off leds
               if "led_off" in entry.task:
                  task = entry.task.split(":")
                  LED_OFF(int(task[1])) 

               # save sensor
               if "save_sensor" in entry.task:
                  task = entry.task.split(":")
                  SAVE_SENSOR_GPIO(task[1])   

               # watering plants
               if "watering_plants" in entry.task:
                  START_WATERING_THREAD()

               # watering plants
               if "save_database" in entry.task:
                  SAVE_DATABASE()
                                                                                                                                                       
               # remove schedular task without repeat
               if entry.repeat == "":
                  DELETE_SCHEDULAR_TASK(entry.id)


def GET_BACKUP_FILES():
   file_list = []
   for files in os.walk(PATH + "/backup/"):  
      file_list.append(files)         
   return file_list[0][2]


def SAVE_DATABASE():  
      # delete old backup files
      if len(GET_BACKUP_FILES()) == 10:
            os.remove (PATH + '/backup/' + file_list[0])

      shutil.copyfile(PATH + '/app/database/smarthome.sqlite3', PATH + '/backup/' + str(datetime.datetime.now().date()) + '_smarthome.sqlite3')


def DETECT_SMARTPHONE():
   hostname = "google.com"
   if os.system("ping -n 1 " + hostname) == 0:
         print("ok")
         #if READ_SENSOR("GPIO_A07") < 600:
         #    LED_SET_SCENE(int(task[1]))  