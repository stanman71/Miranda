from app import app
from app.components.led_control import *
from app.database.database import *
from app.components.pixel_ring import PIXEL_RING_CONTROL
from app.components.mqtt import MQTT_PUBLISH
from app.components.watering_control import START_WATERING_THREAD
from app.components.file_management import SAVE_DATABASE, WRITE_LOGFILE_SYSTEM, READ_LOGFILE_MQTT
from app.components.mqtt import *

import datetime

from threading import Thread

""" ########## """
""" check task """
""" ########## """

def CHECK_TASKS(tasks, task_type):
   list_errors = []

   for element in tasks:
      task = element.task
      name = element.name

      # check snowboy_active
      if task == "snowboy_active" and task_type == "snowboy":
         continue

      # check start_scene
      if "start_scene" in task:
         try:
            task = task.split(":")
            continue

         except:
            list_errors.append("Aufgabe: " + name + " >>> Ungültige Eingabe")
            continue

      # check start_program
      if "start_program" in task:
         try:
            task = task.split(":") 
            if GET_PROGRAM_BY_ID(int(task[1])):
               continue
            else:
               list_errors.append("Aufgabe: " + name + " >>> Programm Nummer " + task[1] + " nicht vorhanden")
               continue
         except:
            list_errors.append("Aufgabe: " + name + " >>> Ungültige Eingabe")
            continue

      # check led_off
      if "led_off" in task:
         try:
            task = task.split(":")
            if task[1].isdigit():
               continue
            else:
               list_errors.append("Aufgabe: " + name + " >>> Ungültige Eingabe")
               continue
         except:
            list_errors.append("Aufgabe: " + name + " >>> Ungültige Eingabe")
            continue

      # check watering_plants
      if task == "watering_plants" and task_type == "timer":
         continue

      # check save_database         
      if task == "save_database" and task_type == "timer":
         continue

      # check update_mqtt_devices
      if task == "update_mqtt_devices" and task_type == "timer":
         continue

      # check get_mqtt_sensordata
      if "get_mqtt_sensordata" in task and (task_type == "timer" or task_type == "sensor"):
         try:
            task = task.split(":")
            if GET_SENSORDATA_JOB_BY_ID(int(task[1])):
               continue
            else:
               list_errors.append("Aufgabe: " + name + " >>> Job-ID " + task[1] + " nicht vorhanden")
               continue 
         except:
            list_errors.append("Aufgabe: " + name + " >>> Ungültige Eingabe")
            continue 

      # nothing found
      list_errors.append("Aufgabe: " + name + " >>> Ungültige Eingabe") 

   if list_errors == []:
      return ""
   else:
      return list_errors


""" ####### """
""" snowboy """
""" ####### """

snowboy_detect_on = False

def SNOWBOY_TASKS(entry):
   
   global snowboy_detect_on
   
   WRITE_LOGFILE_SYSTEM("EVENT", 'Snowboy >>> Detection >>> ' + str(entry.task))
   
   # activate command mode
   if "snowboy_active" in entry.task:
      snowboy_detect_on = True
      PIXEL_RING_CONTROL("on")

      # set snowboy_detect_on to False after 1 second
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

def TASKMANAGEMENT_TIME_TASKS(entries):

   now    = datetime.datetime.now()
   day    = now.strftime('%a')
   hour   = now.strftime('%H')
   minute = now.strftime('%M')

   for entry in entries:
      if entry.day == day or entry.day == "*":
         if entry.hour == hour or entry.hour == "*":
            if entry.minute == minute or entry.minute == "*":
               print(entry.name)

               WRITE_LOGFILE_SYSTEM("EVENT", 'Task >>> ' + entry.name + ' >>> started') 

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
                  UPDATE_MQTT_DEVICES("mqtt")

               # get mqtt sensor data
               if "get_mqtt_sensordata" in entry.task:
                  task = entry.task.split(":")
                  GET_MQTT_SENSORDATA(int(task[1])) 

               # remove schedular task without repeat
               if entry.repeat == "":
                  DELETE_TASKMANAGEMENT_TIME_TASK(entry.id)
