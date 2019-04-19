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

   now = datetime.datetime.now()
   current_day    = now.strftime('%a')
   current_hour   = now.strftime('%H')
   current_minute = now.strftime('%M')

   # format data
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

   if current_hour[0] == "0":
      current_hour = current_hour[1:]   

   if current_minute[0] == "0":
      current_minute = current_minute[1:]                        

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
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + str(e))      

         try:
            # start program
            if "start_program" in entry.task:
               task = entry.task.split(":")
               START_PROGRAM(int(task[1]))
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + str(e))      

         try:
            # turn off leds
            if "led_off" in entry.task:
               task = entry.task.split(":")
               LED_OFF(int(task[1])) 
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + str(e))      

         try:
            # watering plants
            if "watering_plants" in entry.task:
               START_WATERING_THREAD()
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + str(e))      

         try:    
            # save database               
            if "save_database" in entry.task:
               SAVE_DATABASE()     
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + str(e))     

         try:
            # update mqtt devices
            if "update_mqtt_devices" in entry.task:
               UPDATE_MQTT_DEVICES("mqtt")
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + str(e))      

         # request mqtt sensor data
         try:
            if "request_mqtt_sensordata" in entry.task:
               task = entry.task.split(":")
               error_message = REQUEST_MQTT_SENSORDATA(int(task[1]))          
               if error_message == "":
                  WRITE_LOGFILE_SYSTEM("EVENT", "Task >>> " + entry.name + " >>> successful")
               else:
                  WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + error_message)
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + str(e))              
   
         # remove schedular task without repeat
         if entry.repeat == "":
            DELETE_TASKMANAGEMENT_TIME_TASK(entry.id)