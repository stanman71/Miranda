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
         if ":" in task:
            task = task.split(":") 
            try:
               if GET_PROGRAM_BY_ID(int(task[1])):
                  continue
               else:
                  list_errors.append(name + " >>> Programm Nummer " + task[1] + " nicht vorhanden")
                  continue
            except:
               list_errors.append(name + " >>> Programm Nummer " + task[1] + " nicht vorhanden")
               continue
         else:
            list_errors.append(name + " >>> Ungültige Formatierung")
            continue

      # check led_off
      if "led_off" in task:
         if ":" in task:
            task = task.split(":")
            if task[1].isdigit():
               continue
            else:
               list_errors.append(name + " >>> Ungültiger Verzögerungswert")
               continue
         else:
            print("OK")
            list_errors.append(name + " >>> Ungültige Formatierung")
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

      # check request_mqtt_sensordata
      if "request_mqtt_sensordata" in task and (task_type == "timer" or task_type == "sensor"):
         if ":" in task:
            task = task.split(":")
            try:
               if GET_SENSORDATA_JOB_BY_ID(int(task[1])):
                  continue
            except:
               list_errors.append(name + " >>> Job-ID " + task[1] + " nicht vorhanden")
               continue 
         else:
            list_errors.append(name + " >>> Ungültige Formatierung")
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

   if list_errors_settings == []:
      error_message_settings = ""
   else:
      error_message_settings = list_errors_settings

   return error_message_settings


def CHECK_ALL_SENSOR_SETTINGS(sensor_tasks): 
   list_errors_settings = []  

   for task in sensor_tasks:

      # check mqtt devices
      if task.mqtt_device_id_1 == "None" or task.mqtt_device_id_1 == "" or task.mqtt_device_id_1 == None:
         list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> MQTT-Gerät 1") 

      if task.mqtt_device_id_2 == "None" or task.mqtt_device_id_2 == "" or task.mqtt_device_id_2 == None:
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> MQTT-Gerät 2") 

      if task.mqtt_device_id_3 == "None" or task.mqtt_device_id_3 == "" or task.mqtt_device_id_3 == None:
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.operator_main_2 != "None" and task.operator_main_2 != None:
               list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> MQTT-Gerät 3")             

      # check sensors
      if ((task.mqtt_device_id_1 != "None" or task.mqtt_device_id_1 != "") and 
          (task.sensor_key_1 == "None" or task.sensor_key_1 == "")):
         list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Sensor 1") 
         
      if ((task.mqtt_device_id_2 != "None" or task.mqtt_device_id_2 != "") and 
          (task.sensor_key_2 == "None" or task.sensor_key_2 == "" )):
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Sensor 2")  

      if ((task.mqtt_device_id_3 != "None" or task.mqtt_device_id_3 != "") and 
          (task.sensor_key_3 == "None" or task.sensor_key_3 == "" )):
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.operator_main_2 != "None" and task.operator_main_2 != None:
               list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Sensor 3")  

      # check operators
      if task.operator_1 == "None" or task.operator_1 == "" or task.operator_1 == None: 
         list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Operator 1") 
         
      if task.operator_2 == "None" or task.operator_2 == "" or task.operator_2 == None: 
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.operator_main_1 != "<" and task.operator_main_1 != ">" and task.operator_main_1 != "=":
               list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Operator 2")  

      if task.operator_3 == "None" or task.operator_3 == "" or task.operator_3 == None: 
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.operator_main_2 != "None" and task.operator_main_2 != None:
               if task.operator_main_2 != "<" and task.operator_main_2 != ">" and task.operator_main_2 != "=":
                  list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Operator 3")  

      # check values
      if ((task.operator_1 == "<" or task.operator_1 == ">" or task.operator_1 == "=" or task.operator_1 == "None" or task.operator_1 == None) and 
          (task.value_1 == "" or task.value_1 == "None" or task.value_1 == None)):
         list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Vergleichswert 1")         

      if ((task.operator_2 == "<" or task.operator_2 == ">" or task.operator_2 == "=" or task.operator_1 == "None" or task.operator_2 == None) and 
          (task.value_2 == "" or task.value_2 == "None" or task.value_2 == None)):
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.operator_main_1 != "<" and task.operator_main_1 != ">" and task.operator_main_1 != "=":
               list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Vergleichswert 2") 

      if ((task.operator_3 == "<" or task.operator_3 == ">" or task.operator_3 == "=" or task.operator_1 == "None" or task.operator_3 == None) and 
          (task.value_3 == "" or task.value_3 == "None" or task.value_3 == None)):
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.operator_main_2 != "None" and task.operator_main_2 != None:
               if task.operator_main_2 != "<" and task.operator_main_2 != ">" and task.operator_main_2 != "=":
                  list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Vergleichswert 3") 

   if list_errors_settings == []:
      error_message_settings = ""
   else:
      error_message_settings = list_errors_settings

   return error_message_settings
