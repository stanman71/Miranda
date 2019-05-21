import paho.mqtt.client as mqtt
import datetime
import time
import json
import os
import threading
import requests

from app import app
from app.components.control_led import *
from app.database.database import *
from app.components.control_plants import START_WATERING_THREAD
from app.components.file_management import SAVE_DATABASE, WRITE_LOGFILE_SYSTEM, READ_LOGFILE_MQTT, GET_CONFIG_MQTT_BROKER
from app.components.mqtt_functions import *


""" #################### """
""" mqtt publish message """
""" #################### """

BROKER_ADDRESS = GET_CONFIG_MQTT_BROKER()

def MQTT_PUBLISH(MQTT_TOPIC, MQTT_MSG):


    def on_publish(client, userdata, mid):
        print ('Message Published...')

    client = mqtt.Client()
    client.on_publish = on_publish
    client.connect(BROKER_ADDRESS) 
    client.publish(MQTT_TOPIC,MQTT_MSG)
    client.disconnect()

    return ""


""" ################ """
"""  scheduler jobs  """
""" ################ """


from flask_apscheduler import APScheduler

scheduler = APScheduler()
scheduler.start()   

@scheduler.task('cron', id='update_sunrise_sunset', hour='*')
def update_sunrise_sunset():
   
   for task in GET_ALL_SCHEDULER_TASKS():
      
      if task.expanded_option_sunrise == "checked" or task.expanded_option_sunset == "checked":
         
         # get coordinates
         coordinates = GET_LOCATION_COORDINATES(task.expanded_location)
         
         if coordinates != "None" and coordinates != None: 
         
            # update sunrise / sunset
            SET_SCHEDULER_TASK_SUNRISE(task.id, GET_SUNRISE_TIME(float(coordinates[0]), float(coordinates[1])))
            SET_SCHEDULER_TASK_SUNSET(task.id, GET_SUNSET_TIME(float(coordinates[0]), float(coordinates[1])))
            

@scheduler.task('cron', id='scheduler_time', minute='*')
def scheduler_time():
   SCHEDULER_MAIN("time")


@scheduler.task('cron', id='scheduler_ping', second='0, 10, 20, 30, 40, 50')
def scheduler_ping():
   SCHEDULER_MAIN("ping")


""" ################ """
""" sunrise / sunset """
""" ################ """
   
# https://stackoverflow.com/questions/41072147/python-retrieve-the-sunrise-and-sunset-times-from-google

def GET_SUNRISE_TIME(lat, long):
   
   try:
   
      link = "http://api.sunrise-sunset.org/json?lat=%f&lng=%f&formatted=0" % (lat, long)
      f = requests.get(link)
      data = f.text
      sunrise = data[34:42]
      sunset = data[71:79]

      sunrise = sunrise.split(":")
      sunrise_hour   = int(sunrise[0]) + 1
      sunrise_minute = int(sunrise[1])
      
      sunrise = str(sunrise_hour) + ":" + str(sunrise_minute)

      return (sunrise)
      
   except Exception as e:    
      WRITE_LOGFILE_SYSTEM("ERROR", "Update Sunrise / Sunset | " + str(e))
           


def GET_SUNSET_TIME(lat, long):
 
   try:
      
      link = "http://api.sunrise-sunset.org/json?lat=%f&lng=%f&formatted=0" % (lat, long)
      f = requests.get(link)
      data = f.text
      sunrise = data[34:42]
      sunset = data[71:79]

      sunset = sunset.split(":")
      sunset_hour   = int(sunset[0]) + 1
      sunset_minute = int(sunset[1])    

      sunset = str(sunset_hour) + ":" + str(sunset_minute)

      return (sunset)

   except Exception as e:    
      WRITE_LOGFILE_SYSTEM("ERROR", "Update Sunrise / Sunset | " + str(e))



""" ############## """
""" scheduler main """
""" ############## """


def SCHEDULER_MAIN(input_source, ieeeAddr = ""):
   
   if input_source == "time":
      
      for task in GET_ALL_SCHEDULER_TASKS():
         
         Thread = threading.Thread(target=SCHEDULER_TIME_THREAD, args=(task,))
         Thread.start()            
            

   if input_source == "sensor":   
      
      for task in GET_ALL_SCHEDULER_TASKS():
         
         Thread = threading.Thread(target=SCHEDULER_SENSOR_THREAD, args=(task, ieeeAddr, ))
         Thread.start()           
   
      
   if input_source == "ping":   
      
      for task in GET_ALL_SCHEDULER_TASKS():
         
         Thread = threading.Thread(target=SCHEDULER_PING_THREAD, args=(task, ))
         Thread.start()     


""" ################# """
""" scheduler threads """
""" ################# """


def SCHEDULER_TIME_THREAD(task):
   
   # check time
   if task.option_time == "checked":
      if not CHECK_SCHEDULER_TIME(task):
         return
         
      print("Start Scheduler input Time")

      # check sensors
      if task.option_sensors == "checked":
         if not CHECK_SCHEDULER_SENSORS(task):
            return
         
      # check expanded options
      if task.option_expanded == "checked":
         
         if task.expanded_option_home == "checked":
            if not CHECK_SCHEDULER_PING(task):
               return               
         
         if task.expanded_option_away == "checked":
            if CHECK_SCHEDULER_PING(task):
               return         
   
      START_SCHEDULER_TASK(task)


   # check sunrise / sunset option
   if (task.expanded_option_sunrise == "checked" or task.expanded_option_sunset == "checked"):
       
      print("Start Scheduler input Time")

      # check sensors
      if task.option_sensors == "checked":
         if not CHECK_SCHEDULER_SENSORS(task):
            return
         
      # check expanded options
      if task.option_expanded == "checked":
         
         if task.expanded_option_home == "checked":
            if not CHECK_SCHEDULER_PING(task):
               return               
         
         if task.expanded_option_away == "checked":
            if CHECK_SCHEDULER_PING(task):
               return         
         
         if task.expanded_option_sunrise == "checked":
            if CHECK_SCHEDULER_SUNRISE(task):
               START_SCHEDULER_TASK(task) 
            
         if task.expanded_option_sunset == "checked":
            if CHECK_SCHEDULER_SUNSET(task):
               START_SCHEDULER_TASK(task)          
               


def SCHEDULER_SENSOR_THREAD(task, ieeeAddr):
   
   try:
      
      # find sensor jobs with fitting ieeeAddr only
      if (task.mqtt_device_ieeeAddr_1 == ieeeAddr or
          task.mqtt_device_ieeeAddr_2 == ieeeAddr or
          task.mqtt_device_ieeeAddr_3 == ieeeAddr):
             
         print("Start Scheduler input Sensor")
         
         # check time
         if task.option_time == "checked":
            if not CHECK_SCHEDULER_TIME(task):
               return

         # check sensors
         if task.option_sensors == "checked":
            if not CHECK_SCHEDULER_SENSORS(task):
               return
           
         # check expanded options
         if task.option_expanded == "checked":

            if task.expanded_option_home == "checked":
               if not CHECK_SCHEDULER_PING(task):
                  return               
            
            if task.expanded_option_away == "checked":
               if CHECK_SCHEDULER_PING(task):
                  return         
            
            if task.expanded_option_sunrise == "checked":
               if CHECK_SCHEDULER_SUNRISE(task):
                  START_SCHEDULER_TASK(task) 
               
            if task.expanded_option_sunset == "checked":
               if CHECK_SCHEDULER_SUNSET(task):
                  START_SCHEDULER_TASK(task) 

         START_SCHEDULER_TASK(task)          

   except:
      pass


def SCHEDULER_PING_THREAD(task):
   
   # find ping jobs only (home / away)
   if ((task.expanded_option_home == "checked" and CHECK_SCHEDULER_PING(task) == True) or
       (task.expanded_option_away == "checked" and CHECK_SCHEDULER_PING(task) == False)):

      print("Start Scheduler input Ping")

      # check time
      if task.option_time == "checked":
         if not CHECK_SCHEDULER_TIME(task):
            return

      # check sensors
      if task.option_sensors == "checked":
         if not CHECK_SCHEDULER_SENSORS(task):
            return
        
      # check expanded options
      if task.option_expanded == "checked":
         
         if task.expanded_option_sunrise == "checked":
            if CHECK_SCHEDULER_SUNRISE(task):
               START_SCHEDULER_TASK(task)
            
         if task.expanded_option_sunset == "checked":
            if CHECK_SCHEDULER_SUNSET(task):
               START_SCHEDULER_TASK(task)

      START_SCHEDULER_TASK(task)      



""" #################### """
""" check scheduler time """
""" #################### """


def CHECK_SCHEDULER_TIME(task):

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

   # check day
   if "," in task.day:
      days = task.day.split(",")
      for element in days:
         if element == current_day:
            passing = True
            break
   else:
      if task.day == current_day or task.day == "*":
         passing = True

   # check minute
   if passing == True:

      if "," in task.hour:
         hours = task.hour.split(",")
         for element in hours:
            if element == current_hour:
               passing = True
               break
            else:
               passing = False
      else:
         if task.hour == current_hour or task.hour == "*":
            passing = True 
         else:
            passing = False              

   # check minute
   if passing == True:

      if "," in task.minute:
         minutes = task.minute.split(",")
         for element in minutes:
            if element == current_minute:
               passing = True
               break
            else:
               passing = False
      else:
         if task.minute == current_minute or task.minute == "*":
            passing = True 
         else:
            passing = False  

   return passing


      
def CHECK_SCHEDULER_SENSORS(task):
   
   passing = False   
   
   print("!!!!!!!")
   print(task.name)
   
   # #######
   # one row
   # #######
   
   if task.operator_main_1 == "None" or task.operator_main_1 == None:

      device_ieeeAddr_1  = task.mqtt_device_ieeeAddr_1
      sensor_key_1       = task.sensor_key_1
      value_1            = task.value_1
    
      ##################
      # get sensordata 1
      ##################     

      data_1 = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device_ieeeAddr_1).last_values)
   
      sensor_key_1   = sensor_key_1.replace(" ","")          
      sensor_value_1 = data_1[sensor_key_1]

      print(sensor_value_1)
      print(value_1)

      
      ####################
      # compare conditions
      ####################
      
      passing_1 = False


      if task.operator_1 == "=" and not task.value_1.isdigit():
         if str(sensor_value_1) == str(task.value_1):
            passing = True
         else:
            passing = False
      if task.operator_1 == "=" and task.value_1.isdigit():
         if int(sensor_value_1) == int(task.value_1):
            passing = True    
         else:
            passing = False
      if task.operator_1 == "<" and task.value_1.isdigit():
         if int(sensor_value_1) < int(task.value_1):
            passing = True
         else:
            passing = False
      if task.operator_1 == ">" and task.value_1.isdigit():
         if int(sensor_value_1) > int(task.value_1):
            passing = True 
         else:
            passing = False



   # ########
   # two rows
   # ########
   
   if ((task.operator_main_1 != "None" and task.operator_main_1 != None) and 
       (task.operator_main_2 == "None" or task.operator_main_2 == None)):
          
          
      device_ieeeAddr_1 = task.mqtt_device_ieeeAddr_1
      device_ieeeAddr_2 = task.mqtt_device_ieeeAddr_2
      sensor_key_1      = task.sensor_key_1
      sensor_key_2      = task.sensor_key_2
      value_1           = task.value_1
      value_2           = task.value_2
      
      
      ##################
      # get sensordata 1
      ##################     

      data_1 = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device_ieeeAddr_1).last_values)
   
      sensor_key_1   = sensor_key_1.replace(" ","")          
      sensor_value_1 = data_1[sensor_key_1]

      print(sensor_value_1)
      print(value_1)
      
      
      ##################
      # get sensordata 2
      ##################     

      data_2 = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device_ieeeAddr_2).last_values)
   
      sensor_key_2   = sensor_key_2.replace(" ","")          
      sensor_value_2 = data_2[sensor_key_2]

      print(sensor_value_2)
      print(value_2)
      
      
      ####################
      # compare conditions
      ####################
      
      passing_1 = False
      passing_2 = False
      
      # Options: <, >, =
   
      if ((task.operator_main_1 == ">" or task.operator_main_1 == "<" or task.operator_main_1 == "=") and
          (sensor_value_1 != "Message nicht gefunden" and sensor_value_2 != "Message nicht gefunden")):
         
         if task.operator_main_1 == "=":
            try:
               if int(sensor_value_1) == int(sensor_value_2):
                  passing = True    
               else:
                  passing = False
            except:
               if str(sensor_value_1) == str(sensor_value_2):
                  passing = True    
               else:
                  passing = False           
                  
         if task.operator_main_1 == "<":
            if int(sensor_value_1) < int(sensor_value_2):
               passing = True
            else:
               passing = False
               
         if task.operator_main_1 == ">":
            if int(sensor_value_1) > int(sensor_value_2):
               passing = True 
            else:
               passing = False         
     
      # Options: and, or
               
      if task.operator_main_1 == "and" or task.operator_main_1 == "or":
         
         # get passing value one
         
         passing_1 = False
         
         try:
            if task.operator_1 == "=" and not task.value_1.isdigit() and sensor_value_1 != "Message nicht gefunden":
               if str(sensor_value_1) == str(task.value_1):
                  passing_1 = True
               else:
                  passing_1 = False
         except:
            pass
            
         try:  
            if task.operator_1 == "=" and task.value_1.isdigit():
               if int(sensor_value_1) == int(task.value_1):
                  passing_1 = True    
               else:
                  passing_1 = False
         except:
            pass
            
         try:                   
            if task.operator_1 == "<" and task.value_1.isdigit():
               if int(sensor_value_1) < int(task.value_1):
                  passing_1 = True
               else:
                  passing_1 = False
         except:
            pass
            
         try:                       
            if task.operator_1 == ">" and task.value_1.isdigit():
               if int(sensor_value_1) > int(task.value_1):
                  passing_1 = True 
               else:
                  passing_1 = False   
         except:
            pass                    
               
         print("Passing_1:" + str(passing_1))
                 
         
         # get passing value two
         
         passing_2 = False
            
         try:             
            if task.operator_2 == "=" and not task.value_2.isdigit() and sensor_value_1 != "Message nicht gefunden":
               if str(sensor_value_2) == str(task.value_2):
                  passing_2 = True
               else:
                  passing_2 = False
         except:
            pass
            
         try: 
            if task.operator_2 == "=" and task.value_2.isdigit():
               if int(sensor_value_2) == int(task.value_2):
                  passing_2 = True    
               else:
                  passing_2 = False
         except:
            pass
            
         try: 
            if task.operator_2 == "<" and task.value_2.isdigit():
               if int(sensor_value_2) < int(task.value_2):
                  passing_2 = True
               else:
                  passing_2 = False
         except:
            pass
            
         try:                                
            if task.operator_2 == ">" and task.value_2.isdigit():
               if int(sensor_value_2) > int(task.value_2):
                  passing_2 = True 
               else:
                  passing_2 = False   
         except:
            pass                    
               
               
         print("Passing_2:" + str(passing_2))
         
               
         # get result
         
         if task.operator_main_1 == "and":
            if passing_1 == True and passing_2 == True:
               passing = True
            else:
               passing = False
                     
         if task.operator_main_1 == "or":
            if passing_1 == True or passing_2 == True:
               passing = True         
            else:
               passing = False
      
   
   # ##########
   # three rows
   # ##########
   
   if ((task.operator_main_1 != "None" and task.operator_main_1 != None) and 
       (task.operator_main_2 != "None" and task.operator_main_2 != None)):

      device_ieeeAddr_1 = task.mqtt_device_ieeeAddr_1
      device_ieeeAddr_2 = task.mqtt_device_ieeeAddr_2
      device_ieeeAddr_3 = task.mqtt_device_ieeeAddr_3           
      sensor_key_1      = task.sensor_key_1
      sensor_key_2      = task.sensor_key_2
      sensor_key_3      = task.sensor_key_3
      value_1           = task.value_1
      value_2           = task.value_2
      value_3           = task.value_3
      
      
      ##################
      # get sensordata 1
      ##################     

      data_1 = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device_ieeeAddr_1).last_values)
   
      sensor_key_1   = sensor_key_1.replace(" ","")          
      sensor_value_1 = data_1[sensor_key_1]

      print(sensor_value_1)
      print(value_1)
      
      
      ##################
      # get sensordata 2
      ##################     
      
      data_2 = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device_ieeeAddr_2).last_values)
   
      sensor_key_2   = sensor_key_2.replace(" ","")          
      sensor_value_2 = data_2[sensor_key_2]

      print(sensor_value_2)
      print(value_2)


      ##################
      # get sensordata 3
      ##################     

      data_3 = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device_ieeeAddr_3).last_values)
   
      sensor_key_3   = sensor_key_3.replace(" ","")          
      sensor_value_3 = data_3[sensor_key_3]

      print(sensor_value_3)
      print(value_3)

      
      ####################
      # compare conditions
      ####################
      
      passing_1 = False
      passing_2 = False
      passing_3 = False
      
      
      # Options: <, >, = /// and, or
      
      if ((task.operator_main_1 == ">" or task.operator_main_1 == "<" or task.operator_main_1 == "=") and
          (task.operator_main_2 == "and" or task.operator_main_2 == "or")):
         
         # passing value 1

         try:               
            if task.operator_main_1 == "=":
               try:
                  if int(sensor_value_1) == int(sensor_value_2):
                     passing_1 = True 
                  else:
                     passing_1 = False                                 
               except:
                  if str(sensor_value_1) == str(sensor_value_2) and str(sensor_value_1) != "Message nicht gefunden":
                     passing_1 = True 
                  else:
                     passing_1 = False                    
         except:
            pass
            
         try:                        
            if task.operator_main_1 == "<":
               if int(sensor_value_1) < int(sensor_value_2):
                  passing_1 = True
               else:
                  passing_1 = False      
         except:
            pass
            
         try:                    
            if task.operator_main_1 == ">":
               if int(sensor_value_1) > int(sensor_value_2):
                  passing_1 = True 
               else:
                  passing_1 = False            
         except:
            pass
                              
         # passing value 2
         
         try:   
            if task.operator_3 == "=" and not task.value_3.isdigit():
               try:
                  if int(sensor_value_3) == int(task.value_3):
                     passing_2 = True    
                  else:
                     passing_2 = False      
               except:
                  if str(sensor_value_3) == str(task.value_3):
                     passing_2 = True    
                  else:
                     passing_2 = False                  
         except:
            pass
            
         try:                       
            if task.operator_3 == "<" and task.value_3.isdigit():
               if int(sensor_value_3) < int(task.value_3):
                  passing_2 = True
               else:
                  passing_2 = False      
         except:
            pass
            
         try:                     
            if task.operator_3 == ">" and task.value_3.isdigit():
               if int(sensor_value_3) > int(task.value_3):
                  passing_2 = True 
               else:
                  passing_2 = False                               
         except:
            pass
            
         print("Passing_1:" + str(passing_1)) 
         print("Passing_2:" + str(passing_2))
     
         # get result
        
         if task.operator_main_2 == "and":
            if passing_1 == True and passing_2 == True:
               passing = True
            else:
               passing = False
                     
         if task.operator_main_2 == "or":
            if passing_1 == True or passing_2 == True:
               passing = True         
            else:
               passing = False   


      # Options: and, or /// <, >, =                   

      if ((task.operator_main_1 == "and" or task.operator_main_1 == "or") and
          (task.operator_main_2 == "<" or task.operator_main_2 == ">" or task.operator_main_2 == "=")):
         
         # passing value 1
            
         try:   
            if task.operator_1 == "=" and not task.value_1.isdigit():
               try:
                  if int(sensor_value_1) == int(task.value_1):
                     passing_1 = True    
                  else:
                     passing_1 = False      
               except:
                  if str(sensor_value_1) == str(task.value_1):
                     passing_1 = True    
                  else:
                     passing_1 = False                 
         except:
            pass
            
         try:                       
            if task.operator_1 == "<" and task.value_1.isdigit():
               if int(sensor_value_1) < int(task.value_1):
                  passing_1 = True
               else:
                  passing_1 = False      
         except:
            pass
            
         try:                     
            if task.operator_1 == ">" and task.value_1.isdigit():
               if int(sensor_value_1) > int(task.value_1):
                  passing_1 = True 
               else:
                  passing_1 = False          
         except:
            pass
            
         # passing value 2
            
         try:              
            if task.operator_main_2 == "=":
               try:
                  if int(sensor_value_2) == int(sensor_value_3):
                     passing_2 = True    
                  else:
                     passing_2 = False      
               except:
                  if str(sensor_value_2) == str(sensor_value_3):
                     passing_2 = True    
                  else:
                     passing_2 = False                 
         except:
            pass
            
         try:                       
            if task.operator_main_2 == "<":
               if int(sensor_value_2) < int(sensor_value_3):
                  passing_2 = True
               else:
                  passing_2 = False      
         except:
            pass
            
         try:                     
            if task.operator_main_2 == ">":
               if int(sensor_value_2) > int(sensor_value_3):
                  passing_2 = True 
               else:
                  passing_2 = False                               
         except:
            pass
            
         print("Passing_1:" + str(passing_1)) 
         print("Passing_2:" + str(passing_2))

         # get result
         
         if task.operator_main_1 == "and":
            if passing_1 == True and passing_2 == True:
               passing = True
            else:
               passing = False
                     
         if task.operator_main_1 == "or":
            if passing_1 == True or passing_2 == True:
               passing = True         
            else:
               passing = False   


      # Options: <, >, = /// <, >, =          
               
      if ((task.operator_main_1 == "<" or task.operator_main_1 == ">" or task.operator_main_1 == "=") and
          (task.operator_main_2 == "<" or task.operator_main_2 == ">" or task.operator_main_2 == "=")):
         
         try:              
            if task.operator_main_1 == "=" and task.operator_main_2 == "=":
               try:
                  if int(sensor_value_1) == int(sensor_value_2) == int(sensor_value_3):
                     passing = True    
                  else:
                     passing = False      
               except:
                  if str(sensor_value_1) == str(sensor_value_2) == str(sensor_value_3):
                     passing = True    
                  else:
                     passing = False                  
         except:
            pass
            
         try:                    
            if task.operator_main_1 == "=" and task.operator_main_2 == ">":
               if (int(sensor_value_1) == int(sensor_value_2)) > int(sensor_value_3):
                  passing = True
               else:
                  passing = False                         
         except:
            pass
            
         try:                    
            if task.operator_main_1 == "<" and task.operator_main_2 == ">":
               if int(sensor_value_1) < int(sensor_value_2) > int(sensor_value_3):
                  passing = True
               else:
                  passing = False      
         except:
            pass
            
         try:                     
            if task.operator_main_1 == ">" and task.operator_main_2 == ">":
               if int(sensor_value_1) > int(sensor_value_2) > int(sensor_value_3):
                  passing = True
               else:
                  passing = False                         
         except:
            pass
            
         try:                                         
            if task.operator_main_1 == "=" and task.operator_main_2 == "<":
               if (int(sensor_value_1) == int(sensor_value_2)) < int(sensor_value_3):
                  passing = True
               else:
                  passing = False                         
         except:
            pass
            
         try:                   
            if task.operator_main_1 == "<" and task.operator_main_2 == "<":
               if int(sensor_value_1) < int(sensor_value_2) < int(sensor_value_3):
                  passing = True
               else:
                  passing = False      
         except:
            pass
            
         try:                    
            if task.operator_main_1 == ">" and task.operator_main_2 == "<":
               if int(sensor_value_1) > int(sensor_value_2) < int(sensor_value_3):
                  passing = True
               else:
                  passing = False                             
         except:
            pass
            
         try:                     
            if task.operator_main_1 == "<" and task.operator_main_2 == "=":
               if int(sensor_value_1) < (int(sensor_value_2) == int(sensor_value_3)):
                  passing = True
               else:
                  passing = False                                
         except:
            pass
            
         try:                     
            if task.operator_main_1 == ">" and task.operator_main_2 == "=":
               if int(sensor_value_1) > (int(sensor_value_2) == int(sensor_value_3)):
                  passing = True
               else:
                  passing = False        
         except:
            pass
            
            
      # Options: and, or /// and, or
               
      if ((task.operator_main_1 == "and" or task.operator_main_1 == "or") and 
          (task.operator_main_1 == "and" or task.operator_main_1 == "or") and
          (sensor_value_1 != "Message nicht gefunden" or sensor_value_2 != "Message nicht gefunden" 
           or sensor_value_3 != "Message nicht gefunden")):
              
         # passing value 1

         try:              
            if task.operator_1 == "=" and not task.value_1.isdigit():
               if int(sensor_value_1) == int(task.value_1):
                  passing_1 = True    
               else:
                  passing_1 = False      
            else:
               if str(sensor_value_1) == str(task.value_1):
                  passing_1 = True    
               else:
                  passing_1 = False               
         except:
            pass
            
         try:                       
            if task.operator_1 == "<" and task.value_1.isdigit():
               if int(sensor_value_1) < int(task.value_1):
                  passing_1 = True
               else:
                  passing_1 = False      
         except:
            pass
            
         try:                     
            if task.operator_1 == ">" and task.value_1.isdigit():
               if int(sensor_value_1) > int(task.value_1):
                  passing_1 = True 
               else:
                  passing_1 = False       
         except:
            pass
             
         # passing value 2

         try:              
            if task.operator_2 == "=" and not task.value_2.isdigit():
               if int(sensor_value_2) == int(task.value_2):
                  passing_2 = True    
               else:
                  passing_2 = False      
            else:
               if str(sensor_value_2) == str(task.value_2):
                  passing_2 = True    
               else:
                  passing_2 = False   
         except:
            pass
            
         try:                       
            if task.operator_2 == "<" and task.value_2.isdigit():
               if int(sensor_value_2) < int(task.value_2):
                  passing_2 = True
               else:
                  passing_2 = False      
         except:
            pass
            
         try:                    
            if task.operator_2 == ">" and task.value_2.isdigit():
               if int(sensor_value_2) > int(task.value_2):
                  passing_2 = True 
               else:
                  passing_2 = False        
         except:
            pass
               
         # passing value 3

         try:              
            if task.operator_3 == "=" and not task.value_3.isdigit():
               if int(sensor_value_3) == int(task.value_3):
                  passing_3 = True    
               else:
                  passing_3 = False      
            else:
               if str(sensor_value_3) == str(task.value_3):
                  passing_3 = True    
               else:
                  passing_3 = False                  
         except:
            pass
            
         try:                       
            if task.operator_3 == "<" and task.value_3.isdigit():
               if int(sensor_value_3) < int(task.value_3):
                  passing_3 = True
               else:
                  passing_3 = False      
         except:
            pass
            
         try:                     
            if task.operator_3 == ">" and task.value_3.isdigit():
               if int(sensor_value_3) > int(task.value_3):
                  passing_3 = True 
               else:
                  passing_3 = False       
         except:
            pass
            
         print("Passing_1:" + str(passing_1)) 
         print("Passing_2:" + str(passing_2))
         print("Passing_3:" + str(passing_3))         
         
         # get result

         try:              
            if task.operator_main_1 == "and" and task.operator_main_2 == "and":
               if passing_1 == True and passing_2 == True and passing_3 == True:
                  passing = True
               else:
                  passing = False
         except:
            pass
            
         try:                           
            if task.operator_main_1 == "and" and task.operator_main_2 == "or":
               if passing_1 == True and (passing_2 == True or passing_3 == True):
                  passing = True         
               else:
                  passing = False    
         except:
            pass
            
         try:                    
            if task.operator_main_1 == "or" and task.operator_main_2 == "and":
               if (passing_1 == True or passing_2 == True) and passing_3 == True:
                  passing = True         
               else:
                  passing = False                         
         except:
            pass
            
         try:                                 
            if task.operator_main_1 == "or" and task.operator_main_2 == "or":
               if passing_1 == True or passing_2 == True or passing_3 == True:
                  passing = True         
               else:
                  passing = False    
         except:
            pass                                      
        
               
   # Options ended
   
   print("SENSORTASK_RESULT: " + passing)  
                                          
   return passing



def CHECK_SCHEDULER_PING(task):

      ip_addresses = task.expanded_ip_adresses.split(",")

      for ip_address in ip_addresses:
      
         if os.system("ping -c 1 " + ip_address) == 0:
             return True
             
      return False

         

def CHECK_SCHEDULER_SUNRISE(task):

   # get current time
   now = datetime.datetime.now()
   current_hour   = now.strftime('%H')
   current_minute = now.strftime('%M')

   # get sunrise time
   sunrise_data = GET_SCHEDULER_TASK_SUNRISE(task.id)
   
   try:
      sunrise_data = sunrise_data.split(":")
      
      if int(current_hour) == int(sunrise_data[0]) and int(current_minute) == int(sunrise_data[1]):
         return True
         
      else:
         return False
         
   except:
      return False
   
   
def CHECK_SCHEDULER_SUNSET(task):

   # get current time
   now = datetime.datetime.now()
   current_hour   = now.strftime('%H')
   current_minute = now.strftime('%M')

   # get sunset time
   sunset_data = GET_SCHEDULER_TASK_SUNSET(task.id)
   
   try:
      sunset_data = sunset_data.split(":")
      
      if int(current_hour) == int(sunset_data[0]) and int(current_minute) == int(sunset_data[1]):
         return True
         
      else:
         return False
         
   except:
      return False



""" ##################### """
""" start scheduler tasks """
""" ##################### """


def START_SCHEDULER_TASK(task_object):
   
   WRITE_LOGFILE_SYSTEM("EVENT", 'Scheduler | Task - ' + task_object.name + ' | started') 

   # start scene
   try:
      if "scene" in task_object.task:
         try:
            task = task_object.task.split(":")
            group_id = GET_LED_GROUP_BY_NAME(task[1]).id
            scene_id = GET_LED_SCENE_BY_NAME(task[2]).id      
            error_message = LED_START_SCENE(int(group_id), int(scene_id), int(task[3]))  
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]
               WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + error_message)
               
         except:
            task = task_object.task.split(":")
            group_id = GET_LED_GROUP_BY_NAME(task[1]).id
            scene_id = GET_LED_SCENE_BY_NAME(task[2]).id          
            error_message = LED_START_SCENE(int(group_id), int(scene_id))   
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]                    
               WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + error_message)
                  
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


   # start program
   try:
      if "program" in task_object.task:
         task = task_object.task.split(":")
         group_id = GET_LED_GROUP_BY_NAME(task[1]).id
         program_id = GET_LED_PROGRAM_BY_NAME(task[2]).id
         error_message = LED_START_PROGRAM_THREAD(int(group_id), int(program_id))  
         
         if error_message != "":
            error_message = str(error_message)
            error_message = error_message[1:]
            error_message = error_message[:-1]                    
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + error_message)
            
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


   # led off
   try:
      if "led_off" in task_object.task:
         task = task_object.task.split(":")
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
                           WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + error_message)
                  
                     else:
                        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Group - " + input_group_name + " | not founded")
                  
                     
               except:
                  WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Group - " + input_group_name + " | not founded")
                  
               
         if task[1] == "all":
            error_message = LED_TURN_OFF_ALL()   
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]                    
               WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + error_message)
               
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


   # watering plants
   try:
      if "watering_plants" in task_object.task:
         START_WATERING_THREAD()
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


   # save database 
   try:    
      if "save_database" in task_object.task:
         error_message = SAVE_DATABASE()  
         if error_message == "":
            WRITE_LOGFILE_SYSTEM("SUCCESS", "Scheduler | Task - " + task_object.name + " | successful")
         else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + error_message)                   
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))     


   # update mqtt devices
   try:
      if "mqtt_update_devices" in task_object.task:
         error_message = MQTT_UPDATE_DEVICES("mqtt")
         if error_message == "":
            WRITE_LOGFILE_SYSTEM("SUCCESS", "Scheduler | Task - " + task_object.name + " | successful")
         else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + error_message)              
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


   # request sensordata
   try:
      if "request_sensordata" in task_object.task:
         task = task_object.task.split(":")
         error_message = MQTT_REQUEST_SENSORDATA(int(task[1]))          
         if error_message == "":
            WRITE_LOGFILE_SYSTEM("SUCCESS", "Scheduler | Task - " + task_object.name + " | successful")
         else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + error_message)
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))              


   # remove scheduler task without repeat
   if task_object.option_repeat != "checked":
      DELETE_SCHEDULER_TASK(task_object.id)
