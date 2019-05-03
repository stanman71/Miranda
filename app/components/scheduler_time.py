from app import app
from app.components.led_control import *
from app.database.database import *
from app.components.watering_control import START_WATERING_THREAD
from app.components.file_management import SAVE_DATABASE, WRITE_LOGFILE_SYSTEM, READ_LOGFILE_MQTT
from app.components.mqtt import *

import datetime


from flask_apscheduler import APScheduler

scheduler = APScheduler()
scheduler.start()   

@scheduler.task('cron', id='scheduler_time', minute='*')
def scheduler_time():
    entries = GET_ALL_SCHEDULER_TIME_TASKS()
    SCHEDULER_TIME_TASKS(entries)


""" ############## """
""" scheduler time """
""" ############## """

def SCHEDULER_TIME_TASKS(entries):

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

         WRITE_LOGFILE_SYSTEM("EVENT", 'Scheduler | Time Task > ' + entry.name + ' | started') 


         # start scene
         try:
            if "scene" in entry.task:
               try:
                  task = entry.task.split(":")
                  group_id = GET_LED_GROUP_BY_NAME(task[1]).id
                  scene_id = GET_LED_SCENE_BY_NAME(task[2]).id      
                  error_message = LED_START_SCENE(int(group_id), int(scene_id), int(task[3]))  
                  
                  if error_message != "":
                     error_message = str(error_message)
                     error_message = error_message[1:]
                     error_message = error_message[:-1]
                     WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + error_message)
                   
               except:
                  task = entry.task.split(":")
                  group_id = GET_LED_GROUP_BY_NAME(task[1]).id
                  scene_id = GET_LED_SCENE_BY_NAME(task[2]).id          
                  error_message = LED_START_SCENE(int(group_id), int(scene_id))   
                  
                  if error_message != "":
                     error_message = str(error_message)
                     error_message = error_message[1:]
                     error_message = error_message[:-1]                    
                     WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + error_message)
                      
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + str(e))      


         # start program
         try:
            if "program" in entry.task:
               task = entry.task.split(":")
               group_id = GET_LED_GROUP_BY_NAME(task[1]).id
               program_id = GET_LED_PROGRAM_BY_NAME(task[2]).id
               error_message = LED_START_PROGRAM_THREAD(int(group_id), int(program_id))  
               
               if error_message != "":
                  error_message = str(error_message)
                  error_message = error_message[1:]
                  error_message = error_message[:-1]                    
                  WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + error_message)
                
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + str(e))      


         # led off
         try:
            if "led_off" in entry.task:
               task = entry.task.split(":")
               if task[1] == "group":
                  
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
                                 WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + error_message)
                       
                           else:
                              WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | Gruppe > " + input_group_name + " | not founded")
                       
                           
                     except:
                        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | Gruppe > " + input_group_name + " | not founded")
                        
                     
               if task[1] == "all":
                  error_message = LED_TURN_OFF_ALL()   
                  
                  if error_message != "":
                     error_message = str(error_message)
                     error_message = error_message[1:]
                     error_message = error_message[:-1]                    
                     WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + error_message)
                   
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + str(e))      


         # watering plants
         try:
            if "watering_plants" in entry.task:
               START_WATERING_THREAD()
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + str(e))      


         # save database 
         try:    
            if "save_database" in entry.task:
               error_message = SAVE_DATABASE()  
               if error_message == "":
                  WRITE_LOGFILE_SYSTEM("SUCCESS", "Scheduler | Time Task > " + entry.name + " | successful")
               else:
                  WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + error_message)                   
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + str(e))     


         # update mqtt devices
         try:
            if "mqtt_update_devices" in entry.task:
               error_message = MQTT_UPDATE_DEVICES("mqtt")
               if error_message == "":
                  WRITE_LOGFILE_SYSTEM("SUCCESS", "Scheduler | Time Task > " + entry.name + " | successful")
               else:
                  WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + error_message)              
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " >>> " + str(e))      


         # request sensordata
         try:
            if "request_sensordata" in entry.task:
               task = entry.task.split(":")
               error_message = MQTT_REQUEST_SENSORDATA(int(task[1]))          
               if error_message == "":
                  WRITE_LOGFILE_SYSTEM("SUCCESS", "Scheduler >>> Time Task > " + entry.name + " | successful")
               else:
                  WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + error_message)
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task > " + entry.name + " | " + str(e))              
   
         # remove scheduler task without repeat
         if entry.repeat == "":
            DELETE_SCHEDULER_TIME_TASK(entry.id)


