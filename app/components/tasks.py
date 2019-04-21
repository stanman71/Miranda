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
               WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy >>> Task >>> " + entry.name + " >>> " + error_message)     
         
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
               WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy >>> Task >>> " + entry.name + " >>> " + error_message)
               
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy >>> Task >>> " + entry.name + " >>> " + str(e))     
         
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
            WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy >>> Task >>> " + entry.name + " >>> " + error_message)
         
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy >>> Task >>> " + entry.name + " >>> " + str(e))     

          
   try:
      # led off
      if "led_off" in entry.task and snowboy_detect_on == True:
         task = entry.task.split(":")
         if task[1] == "group":
            group_id = GET_LED_GROUP_BY_NAME(task[2]).id
            error_message = LED_TURN_OFF_GROUP(int(group_id))
            
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")   
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]                    
               WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy >>> Task >>> " + entry.name + " >>> " + error_message)   
            
         if task[1] == "all":
            error_message = LED_TURN_OFF_ALL()   
            
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")   
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]                    
               WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy >>> Task >>> " + entry.name + " >>> " + error_message)

   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "SnowBoy >>> Task >>> " + entry.name + " >>> " + str(e))     
         

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
                     WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + error_message)
                   
               except:
                  task = entry.task.split(":")
                  group_id = GET_LED_GROUP_BY_NAME(task[1]).id
                  scene_id = GET_LED_SCENE_BY_NAME(task[2]).id          
                  error_message = LED_START_SCENE(int(group_id), int(scene_id))   
                  
                  if error_message != "":
                     error_message = str(error_message)
                     error_message = error_message[1:]
                     error_message = error_message[:-1]                    
                     WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + error_message)
                      
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + str(e))      

         try:
            # start program
            if "program" in entry.task:
               task = entry.task.split(":")
               group_id = GET_LED_GROUP_BY_NAME(task[1]).id
               program_id = GET_LED_PROGRAM_BY_NAME(task[2]).id
               error_message = LED_START_PROGRAM_THREAD(int(group_id), int(program_id))  
               
               if error_message != "":
                  error_message = str(error_message)
                  error_message = error_message[1:]
                  error_message = error_message[:-1]                    
                  WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + error_message)
                
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + str(e))      

         try:
            # led off
            if "led_off" in entry.task:
               task = entry.task.split(":")
               if task[1] == "group":
                  group_id = GET_LED_GROUP_BY_NAME(task[2]).id
                  error_message = LED_TURN_OFF_GROUP(int(group_id))
                  
                  if error_message != "":
                     error_message = str(error_message)
                     error_message = error_message[1:]
                     error_message = error_message[:-1]                    
                     WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + error_message)              
                  
               if task[1] == "all":
                  error_message = LED_TURN_OFF_ALL()   
                  
                  if error_message != "":
                     error_message = str(error_message)
                     error_message = error_message[1:]
                     error_message = error_message[:-1]                    
                     WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + error_message)
                   
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
               error_message = SAVE_DATABASE()  
               if error_message == "":
                  WRITE_LOGFILE_SYSTEM("SUCCESS", "Task >>> " + entry.name + " >>> successful")
               else:
                  WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + error_message)                   
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + str(e))     

         try:
            # update mqtt devices
            if "mqtt_update_devices" in entry.task:
               error_message = MQTT_UPDATE_DEVICES("mqtt")
               if error_message == "":
                  WRITE_LOGFILE_SYSTEM("SUCCESS", "Task >>> " + entry.name + " >>> successful")
               else:
                  WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + error_message)              
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + str(e))      

         # request sensordata
         try:
            if "request_sensordata" in entry.task:
               task = entry.task.split(":")
               error_message = MQTT_REQUEST_SENSORDATA(int(task[1]))          
               if error_message == "":
                  WRITE_LOGFILE_SYSTEM("SUCCESS", "Task >>> " + entry.name + " >>> successful")
               else:
                  WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + error_message)
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Task >>> " + entry.name + " >>> " + str(e))              
   
         # remove schedular task without repeat
         if entry.repeat == "":
            DELETE_TASKMANAGEMENT_TIME_TASK(entry.id)
