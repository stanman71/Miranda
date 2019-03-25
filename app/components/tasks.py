from app import app
from app.components.led_control import *
from app.database.database import *
from app.components.pixel_ring import PIXEL_RING_CONTROL
from app.components.mqtt import MQTT_PUBLISH
from app.components.watering_control import START_WATERING_THREAD

import time
import datetime
import shutil
import os

from threading import Thread

PATH = "/home/pi/SmartHome"


""" #### """
""" mqtt """
""" #### """

def UPDATE_MQTT_DEVICES(devices):
   for device in devices:
      channel = "/SmartHome/" + device.channel_path + "/device"
      MQTT_PUBLISH(channel, "")


""" ####### """
""" snowboy """
""" ####### """

snowboy_detect_on = False

def SNOWBOY_TASKS(entry):
   
   global snowboy_detect_on
   
   # activate command mode
   if "snowboy_active" in entry.task:
      snowboy_detect_on = True
      PIXEL_RING_CONTROL("on")

      # set snowboy_detect_on to False after 5 seconds
      class waiter(Thread):
         def run(self):
            global detect
            time.sleep(1)
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")
      waiter().start()
  
   # start scene
   if "start_scene" in entry.task and snowboy_detect_on == True:
      task = entry.task.split(":")
      try:
            LED_SET_SCENE(int(task[1]), int(task[2]))
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")
      except:
            LED_SET_SCENE(int(task[1]))
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")

   # start program
   if "start_program" in entry.task and snowboy_detect_on == True:
      task = entry.task.split(":")
      START_PROGRAM(int(task[1]))
      snowboy_detect_on = False
      PIXEL_RING_CONTROL("off")

   # turn off leds
   if "led_off" in entry.task and snowboy_detect_on == True:
      task = entry.task.split(":")
      LED_OFF(int(task[1]))   
      snowboy_detect_on = False 
      PIXEL_RING_CONTROL("off")


""" ######### """
""" schedular """
""" ######### """

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

               # watering plants
               if "watering_plants" in entry.task:
                  START_WATERING_THREAD()

               # save database
               if "save_database" in entry.task:
                  SAVE_DATABASE()

               # update mqtt devices
               if "update_mqtt_devices" in entry.task:
                  UPDATE_MQTT_DEVICES(GET_ALL_MQTT_DEVICES())

               # remove schedular task without repeat
               if entry.repeat == "":
                  DELETE_SCHEDULAR_TASK(entry.id)


""" ######## """
""" database """
""" ######## """

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
