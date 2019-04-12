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
   current_day    = now.strftime('%a')
   current_hour   = now.strftime('%H')
   current_minute = now.strftime('%M')

   if current_day == "Mon":
      current_day = "Mo"
   if current_day == "Tue":
      current_day = "Tu"
   if current_day == "Wed":
      current_day = "We"
   if current_day == "Thu":
      current_day = "Th"
   if current_day == "Fri":
      current_day = "Fr"
   if current_day == "Sat":
      current_day = "Sa"
   if current_day == "Sun":
      current_day = "Su"                                 

   passing = False

   for entry in entries:

      # check day
      if "," in entry.day:
         days = entry.day.split(",")
         for element in days:
            if element == current_day:
               passing = True
               break
      else:
         if entry.day == current_day or entry.day == "*":
            passing = True

      # check minute
      if passing == True:

         if "," in entry.hour:
            hours = entry.hour.split(",")
            for element in hours:
               if element == current_hour:
                  passing = True
                  break
               else:
                  passing = False
         else:
            if entry.hour == current_hour or entry.hour == "*":
               passing = True 
            else:
               passing = False              

      # check minute
      if passing == True:

         if "," in entry.minute:
            minutes = entry.minute.split(",")
            for element in minutes:
               if element == current_minute:
                  passing = True
                  break
               else:
                  passing = False
         else:
            if entry.minute == current_minute or entry.minute == "*":
               passing = True 
            else:
               passing = False  

      # start task
      if passing == True:

         print(entry.name)

         WRITE_LOGFILE_SYSTEM("EVENT", 'Task >>> ' + entry.name + ' >>> started') 

         try:

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

         except:
            pass


""" ############### """
""" check functions """
""" ############### """

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
            list_errors.append(name + " >>> Ungültige Aufgabe")
            continue

      # check start_program
      if "start_program" in task:
         try:
            task = task.split(":") 
            if GET_PROGRAM_BY_ID(int(task[1])):
               continue
            else:
               list_errors.append(name + " >>> Programm Nummer " + task[1] + " nicht vorhanden")
               continue
         except:
            list_errors.append(name + " >>> Ungültige Aufgabe")
            continue

      # check led_off
      if "led_off" in task:
         try:
            task = task.split(":")
            if task[1].isdigit():
               continue
            else:
               list_errors.append(name + " >>> Ungültige Aufgabe")
               continue
         except:
            list_errors.append(name + " >>> Ungültige Aufgabe")
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
               list_errors.append(name + " >>> Job-ID " + task[1] + " nicht vorhanden")
               continue 
         except:
            list_errors.append(name + " >>> Ungültige Aufgabe")
            continue 

      # nothing found
      list_errors.append(name + " >>> Ungültige Aufgabe") 

   if list_errors == []:
      return ""
   else:
      return list_errors


def CHECK_ALL_TIMER_SETTINGS(timer_tasks): 
   list_errors_settings = []  

   for task in timer_tasks:

      ### check day
      if "," in task.day:
            day = task.day.split(",")
            for element in day:
               if element not in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
                  list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Tag") 
                  break                                 
      else:
            if task.day not in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su", "*"] and task.day != "*":
               list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Tag") 

      ### check hour
      if "," in task.hour:
            hour = task.hour.split(",")
            for element in hour:
               try:                                   
                  if not (0 <= int(element) <= 24):
                        list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Stunde") 
                        break   
               except:
                  list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Stunde") 
                  break   
      else:
            try:
               if not (0 <= int(task.hour) <= 24) and task.hour != "*":
                        list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Stunde") 
            except:
               if task.hour != "*":
                  list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Stunde")    

      ### check minute
      if "," in task.minute:
            minute = task.minute.split(",")
            for element in minute:
               try:                                   
                  if not (0 <= int(element) <= 60):
                        list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Minute") 
                        break   
               except:
                  list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Minute") 
                  break   
      else:
            try:
               if not (0 <= int(task.minute) <= 60) and task.minute != "*":
                        list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Minute") 
            except:
               if task.minute != "*":
                  list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Minute") 

   return list_errors_settings
