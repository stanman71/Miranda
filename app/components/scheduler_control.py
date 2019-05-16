import paho.mqtt.client as mqtt
import datetime
import time
import json
import os
import threading

from astral import Astral


from app import app
from app.components.led_control import *
from app.database.database import *
from app.components.watering_control import START_WATERING_THREAD
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


@scheduler.task('cron', id='scheduler_time', minute='*')
def scheduler_time():
   SCHEDULER_MAIN("time")


@scheduler.task('cron', id='scheduler_ping', second='0, 10, 20, 30, 40, 50')
def scheduler_ping():
   SCHEDULER_MAIN("ping")


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
         
      # check expanded
      if task.option_expanded == "checked":
         
         if task.expanded_home == "checked":
            if not CHECK_SCHEDULER_PING(task):
               return               
         
         if task.expanded_away == "checked":
            if CHECK_SCHEDULER_PING(task):
               return         
   
         if task.expanded_sunrise == "checked":
            if not CHECK_SCHEDULER_SUNRISE(task):
               return
            
         if task.expanded_sunset == "checked":
            if not CHECK_SCHEDULER_SUNSET(task):
               return
               
      START_SCHEDULER_TASK(task)



def SCHEDULER_SENSOR_THREAD(task, ieeeAddr):
      
   try:
      incoming_mqtt_device_id = GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr).id
   
      print(incoming_mqtt_device_id)


      # find sensor jobs with fitting ieeeAddr only
      if (task.mqtt_device_id_1 == incoming_mqtt_device_id or
          task.mqtt_device_id_2 == incoming_mqtt_device_id or
          task.mqtt_device_id_3 == incoming_mqtt_device_id):
             
         print("Start Scheduler input Sensor")
         
         # check time
         if task.option_time == "checked":
            if not CHECK_SCHEDULER_TIME(task):
               return

         # check sensors
         if task.option_sensors == "checked":
            if not CHECK_SCHEDULER_SENSORS(task):
               return
           
         # check expanded
         if task.option_expanded == "checked":

            if task.expanded_home == "checked":
               if not CHECK_SCHEDULER_PING(task):
                  return               
            
            if task.expanded_away == "checked":
               if CHECK_SCHEDULER_PING(task):
                  return         
            
            if task.expanded_sunrise == "checked":
               if not CHECK_SCHEDULER_SUNRISE(task):
                  return
               
            if task.expanded_sunset == "checked":
               if not CHECK_SCHEDULER_SUNSET(task):
                  return

         START_SCHEDULER_TASK(task)          
         
   except:
      pass



def SCHEDULER_PING_THREAD(task):
   
   # find ping jobs only (home / away)
   if ((task.expanded_home == "checked" and CHECK_SCHEDULER_PING(task) == True) or
       (task.expanded_away == "checked" and CHECK_SCHEDULER_PING(task) == False)):

      print("Start Scheduler input Ping")

      # check time
      if task.option_time == "checked":
         if not CHECK_SCHEDULER_TIME(task):
            return

      # check sensors
      if task.option_sensors == "checked":
         if not CHECK_SCHEDULER_SENSORS(task):
            return
        
      # check expanded
      if task.option_expanded == "checked":
         
         if task.expanded_sunrise == "checked":
            if not CHECK_SCHEDULER_SUNRISE(task):
               return
            
         if task.expanded_sunset == "checked":
            if not CHECK_SCHEDULER_SUNSET(task):
               return

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

      device_id_1  = task.mqtt_device_id_1
      sensor_key_1 = task.sensor_key_1
      value_1      = task.value_1
    
      ##################
      # get sensordata 1
      ##################     

      data_1 = json.loads(GET_MQTT_DEVICE_BY_ID(device_id_1).last_values)
   
      sensor_key_1   = sensor_key_1.replace(" ","")          
      sensor_value_1 = data_1[sensor_key_1]

      print(sensor_value_1)
      print(value_1)

      
      ####################
      # compare conditions
      ####################
      
      passing_1 = False


      if task.operator_1 == "=" and not task.value_1.isdigit():
         if sensor_value_1 == task.value_1:
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
          
          
      device_id_1  = task.mqtt_device_id_1
      device_id_2  = task.mqtt_device_id_2
      sensor_key_1 = task.sensor_key_1
      sensor_key_2 = task.sensor_key_2
      value_1      = task.value_1
      value_2      = task.value_2
      
      
      ##################
      # get sensordata 1
      ##################     

      data_1 = json.loads(GET_MQTT_DEVICE_BY_ID(device_id_1).last_values)
   
      sensor_key_1   = sensor_key_1.replace(" ","")          
      sensor_value_1 = data_1[sensor_key_1]

      print(sensor_value_1)
      print(value_1)
      
      
      ##################
      # get sensordata 2
      ##################     

      data_2 = json.loads(GET_MQTT_DEVICE_BY_ID(device_id_2).last_values)
   
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
               if sensor_value_1 == sensor_value_2:
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
               if sensor_value_1 == task.value_1:
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
               if sensor_value_2 == task.value_2:
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

      device_id_1  = task.mqtt_device_id_1
      device_id_2  = task.mqtt_device_id_2
      device_id_3  = task.mqtt_device_id_3           
      sensor_key_1 = task.sensor_key_1
      sensor_key_2 = task.sensor_key_2
      sensor_key_3 = task.sensor_key_3
      value_1      = task.value_1
      value_2      = task.value_2
      value_3      = task.value_3
      
      
      ##################
      # get sensordata 1
      ##################     

      data_1 = json.loads(GET_MQTT_DEVICE_BY_ID(device_id_1).last_values)
   
      sensor_key_1   = sensor_key_1.replace(" ","")          
      sensor_value_1 = data_1[sensor_key_1]

      print(sensor_value_1)
      print(value_1)
      
      
      ##################
      # get sensordata 2
      ##################     
      
      data_2 = json.loads(GET_MQTT_DEVICE_BY_ID(device_id_2).last_values)
   
      sensor_key_2   = sensor_key_2.replace(" ","")          
      sensor_value_2 = data_2[sensor_key_2]

      print(sensor_value_2)
      print(value_2)


      ##################
      # get sensordata 3
      ##################     

      data_3 = json.loads(GET_MQTT_DEVICE_BY_ID(device_id_3).last_values)
   
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
                  if sensor_value_1 == sensor_value_2 and sensor_value_1 != "Message nicht gefunden":
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
                  if sensor_value_3 == task.value_3:
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
                  if sensor_value_1 == task.value_1:
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
                  if sensor_value_2 == sensor_value_3:
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
                  if sensor_value_1 == sensor_value_2 == sensor_value_3:
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
               if sensor_value_1 == task.value_1:
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
               if sensor_value_2 == task.value_2:
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
               if sensor_value_3 == task.value_3:
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

   # calculate sunrise
   city_name = 'Berlin'
   a = Astral()
   a.solar_depression = 'civil'
   city = a[city_name]

   timezone = city.timezone
   sun = city.sun(date=datetime.date.today(), local=True)

   # format sunrise
   sunrise = str(sun['sunrise']).split("+")[0]
   sunrise = sunrise.split(" ")[1]
   
   sunrise_hour   = sunrise.split(":")[0]
   sunrise_minute = sunrise.split(":")[1]
   
   if current_hour == sunrise_hour and current_minute == sunrise_minute:
      return True
      
   else:
      return False
   
   
   
def CHECK_SCHEDULER_SUNSET(task):

   # get current time
   now = datetime.datetime.now()
   current_hour   = now.strftime('%H')
   current_minute = now.strftime('%M')

   # calculate sunset
   city_name = 'Berlin'
   a = Astral()
   a.solar_depression = 'civil'
   city = a[city_name]

   timezone = city.timezone
   sun = city.sun(date=datetime.date.today(), local=True)
   
   # format sunset
   sunset = str(sun['sunset']).split("+")[0]
   sunset = sunset.split(" ")[1]
   
   sunset_hour   = sunset.split(":")[0]
   sunset_minute = sunset.split(":")[1]   
   
   if current_hour == sunset_hour and current_minute == sunset_minute:
      return True
      
   else:
      return False




""" ##################### """
""" start scheduler tasks """
""" ##################### """


def START_SCHEDULER_TASK(task):

   WRITE_LOGFILE_SYSTEM("EVENT", 'Scheduler | Time Task - ' + task.name + ' | started') 

   # start scene
   try:
      if "scene" in task.task:
         try:
            task = task.task.split(":")
            group_id = GET_LED_GROUP_BY_NAME(task[1]).id
            scene_id = GET_LED_SCENE_BY_NAME(task[2]).id      
            error_message = LED_START_SCENE(int(group_id), int(scene_id), int(task[3]))  
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]
               WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + error_message)
               
         except:
            task = task.task.split(":")
            group_id = GET_LED_GROUP_BY_NAME(task[1]).id
            scene_id = GET_LED_SCENE_BY_NAME(task[2]).id          
            error_message = LED_START_SCENE(int(group_id), int(scene_id))   
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]                    
               WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + error_message)
                  
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + str(e))      


   # start program
   try:
      if "program" in task.task:
         task = task.task.split(":")
         group_id = GET_LED_GROUP_BY_NAME(task[1]).id
         program_id = GET_LED_PROGRAM_BY_NAME(task[2]).id
         error_message = LED_START_PROGRAM_THREAD(int(group_id), int(program_id))  
         
         if error_message != "":
            error_message = str(error_message)
            error_message = error_message[1:]
            error_message = error_message[:-1]                    
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + error_message)
            
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + str(e))      


   # led off
   try:
      if "led_off" in task.task:
         task = task.task.split(":")
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
                           WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + error_message)
                  
                     else:
                        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | Group - " + input_group_name + " | not founded")
                  
                     
               except:
                  WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | Group - " + input_group_name + " | not founded")
                  
               
         if task[1] == "all":
            error_message = LED_TURN_OFF_ALL()   
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]                    
               WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + error_message)
               
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + str(e))      


   # watering plants
   try:
      if "watering_plants" in task.task:
         START_WATERING_THREAD()
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + str(e))      


   # save database 
   try:    
      if "save_database" in task.task:
         error_message = SAVE_DATABASE()  
         if error_message == "":
            WRITE_LOGFILE_SYSTEM("SUCCESS", "Scheduler | Time Task - " + task.name + " | successful")
         else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + error_message)                   
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + str(e))     


   # update mqtt devices
   try:
      if "mqtt_update_devices" in task.task:
         error_message = MQTT_UPDATE_DEVICES("mqtt")
         if error_message == "":
            WRITE_LOGFILE_SYSTEM("SUCCESS", "Scheduler | Time Task - " + task.name + " | successful")
         else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + error_message)              
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + str(e))      


   # request sensordata
   try:
      if "request_sensordata" in task.task:
         task = task.task.split(":")
         error_message = MQTT_REQUEST_SENSORDATA(int(task[1]))          
         if error_message == "":
            WRITE_LOGFILE_SYSTEM("SUCCESS", "Scheduler | Time Task - " + task.name + " | successful")
         else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + error_message)
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Time Task - " + task.name + " | " + str(e))              


   # remove scheduler task without repeat
   if task.option_repeat != "checked":
      DELETE_SCHEDULER_TASK(task.id)
