import paho.mqtt.client as mqtt
import datetime
import time
import json
import os
import requests
import heapq

from app import app
from app.database.database import *
from app.components.tasks import START_SCHEDULER_TASK
from app.components.mqtt import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM, GET_LOCATION_COORDINATES
from app.components.shared_resources import process_management_queue

from ping3 import ping



""" ################################ """
""" ################################ """
"""            scheduler             """
""" ################################ """
""" ################################ """


from flask_apscheduler import APScheduler

scheduler = APScheduler()
scheduler.start()   


@scheduler.task('cron', id='update_sunrise_sunset', hour='*')
def update_sunrise_sunset():

	for task in GET_ALL_SCHEDULER_TASKS():

		if task.option_sunrise == "checked" or task.option_sunset == "checked":

			# get coordinates
			coordinates = GET_LOCATION_COORDINATES(task.location)

			if coordinates != "None" and coordinates != None: 

				# update sunrise / sunset
				SET_SCHEDULER_TASK_SUNRISE(task.id, GET_SUNRISE_TIME(float(coordinates[0]), float(coordinates[1])))
				SET_SCHEDULER_TASK_SUNSET(task.id, GET_SUNSET_TIME(float(coordinates[0]), float(coordinates[1])))
							

@scheduler.task('cron', id='scheduler_time', minute='*')
def scheduler_time():
   
	for task in GET_ALL_SCHEDULER_TASKS():
		if task.option_time == "checked" or task.option_sun == "checked":
			heapq.heappush(process_management_queue, (20, ("scheduler", "time", task.id)))         


@scheduler.task('cron', id='scheduler_ping', second='0, 10, 20, 30, 40, 50')
def scheduler_ping():
   
	for task in GET_ALL_SCHEDULER_TASKS():
		if task.option_position == "checked":
			heapq.heappush(process_management_queue, (20, ("scheduler", "ping", task.id)))



""" ################################ """
""" ################################ """
"""         sunrise / sunset         """
""" ################################ """
""" ################################ """
   
   
# https://stackoverflow.com/questions/41072147/python-retrieve-the-sunrise-and-sunset-times-from-google

def GET_SUNRISE_TIME(lat, long):
   
   try:
   
      link     = "http://api.sunrise-sunset.org/json?lat=%f&lng=%f&formatted=0" % (lat, long)
      response = requests.get(link)
      data     = response.text
      
      # get sunrise data
      sunrise  = data[34:42]
      sunrise  = sunrise.split(":")
      
      # add one hour for CEST
      sunrise_hour   = str(int(sunrise[0]) + 1)
      sunrise_minute = str(sunrise[1])
      
      if len(sunrise_minute) == 1:
         sunrise_minute = str(0) + sunrise_minute
      
      sunrise = sunrise_hour + ":" + sunrise_minute

      return (sunrise)
      
      
   except Exception as e:    
      WRITE_LOGFILE_SYSTEM("ERROR", "Update Sunrise / Sunset | " + str(e))
           

def GET_SUNSET_TIME(lat, long):
 
   try:
      
      link     = "http://api.sunrise-sunset.org/json?lat=%f&lng=%f&formatted=0" % (lat, long)
      response = requests.get(link)
      data     = response.text
      
      # get sunset data
      sunset   = data[71:79]
      sunset   = sunset.split(":")
      
      # add one hour for CEST
      sunset_hour   = str(int(sunset[0]) + 1)
      sunset_minute = str(sunset[1]) 

      if len(sunset_minute) == 1:
         sunset_minute = str(0) + sunset_minute

      sunset = sunset_hour + ":" + sunset_minute

      return (sunset)


   except Exception as e:    
      WRITE_LOGFILE_SYSTEM("ERROR", "Update Sunrise / Sunset | " + str(e))



""" ################################ """
""" ################################ """
"""       scheduler processes        """
""" ################################ """
""" ################################ """


def SCHEDULER_TIME_PROCESS(task):
   
   # ######
   #  time
   # ######
   
   if task.option_time == "checked":
      if not CHECK_SCHEDULER_TIME(task):
         return
         
      print("Start Scheduler Time")

      # check sensors
      if task.option_sensors == "checked":
         if not CHECK_SCHEDULER_SENSORS(task):
            return
         
      # check position
      if task.option_position == "checked":
         
         if task.option_home == "checked":
            if CHECK_SCHEDULER_PING(task) == "False":
               return               
         
         if task.option_away == "checked":
            if CHECK_SCHEDULER_PING(task) == "True":
               return         
   
      START_SCHEDULER_TASK(task)


   # ##################
   #  sunrise / sunset
   # ##################
   
   if task.option_sun == "checked":
       
      print("Start Scheduler Sun")

      # check sensors
      if task.option_sensors == "checked":
         if not CHECK_SCHEDULER_SENSORS(task):
            return
         
      # check position 
      if task.option_position == "checked":

         if task.option_home == "checked":
            if CHECK_SCHEDULER_PING(task) == "False":
               return               
         
         if task.option_away == "checked":
            if CHECK_SCHEDULER_PING(task) == "True":
               return         

      # check sun
      if task.option_sunrise == "checked":
         if CHECK_SCHEDULER_SUNRISE(task):
            START_SCHEDULER_TASK(task) 
         
      if task.option_sunset == "checked":
         if CHECK_SCHEDULER_SUNSET(task):
            START_SCHEDULER_TASK(task)       
               

def SCHEDULER_SENSOR_PROCESS(task, ieeeAddr):
   
   try:
      
      # find sensor jobs with fitting ieeeAddr only
      if (task.mqtt_device_ieeeAddr_1 == ieeeAddr or
          task.mqtt_device_ieeeAddr_2 == ieeeAddr or
          task.mqtt_device_ieeeAddr_3 == ieeeAddr):
             
         print("Start Scheduler Sensor")
         
         # check time
         if task.option_time == "checked":
            if not CHECK_SCHEDULER_TIME(task):
               return

         # check sensors
         if task.option_sensors == "checked":
            if not CHECK_SCHEDULER_SENSORS(task):
               return
           
         # check position 
         if task.option_position == "checked":

            if task.option_home == "checked":
               if CHECK_SCHEDULER_PING(task) == "False":
                  return               
            
            if task.option_away == "checked":
               if CHECK_SCHEDULER_PING(task) == "True":
                  return         

         # check sun
         if task.option_sun == "checked":
            
            if task.option_sunrise == "checked":
               if CHECK_SCHEDULER_SUNRISE(task):
                  START_SCHEDULER_TASK(task) 
               
            if task.option_sunset == "checked":
               if CHECK_SCHEDULER_SUNSET(task):
                  START_SCHEDULER_TASK(task) 

         START_SCHEDULER_TASK(task)          

   except:
      pass


def SCHEDULER_PING_PROCESS(task):
   
   # find ping jobs only (home / away)
   if task.option_home == "checked" or task.option_away == "checked":

      ping_result = CHECK_SCHEDULER_PING(task)
      
      # update last ping, if nessanrry     
      if task.option_home == "checked" and ping_result == "False":
         SET_SCHEDULER_LAST_PING_RESULT(task.id, "False")
         return
         
      if task.option_away == "checked" and ping_result == "True":
         SET_SCHEDULER_LAST_PING_RESULT(task.id, "True")
         return

      # start job, if ping result changed first
      if GET_SCHEDULER_LAST_PING_RESULT(task.id) != ping_result:

         print("Start Scheduler Ping")
         
         # check time
         if task.option_time == "checked":
            if not CHECK_SCHEDULER_TIME(task):
               return

         # check sensors
         if task.option_sensors == "checked":
            if not CHECK_SCHEDULER_SENSORS(task):
               return
           
         # check sun options
         if task.option_sun == "checked":
            
            if task.option_sunrise == "checked":
               if CHECK_SCHEDULER_SUNRISE(task):
                  START_SCHEDULER_TASK(task)
               
            if task.option_sunset == "checked":
               if CHECK_SCHEDULER_SUNSET(task):
                  START_SCHEDULER_TASK(task)

         START_SCHEDULER_TASK(task)     
         SET_SCHEDULER_LAST_PING_RESULT(task.id, ping_result)


""" ################################ """
""" ################################ """
"""     check scheduler processes    """
""" ################################ """
""" ################################ """


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
      value_1            = task.value_1.lower()

      try:
         value_1 = str(value_1).lower()
      except:
         pass
      
    
      ##################
      # get sensordata 1
      ##################     

      data_1 = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device_ieeeAddr_1).last_values)
   
      sensor_key_1   = sensor_key_1.replace(" ","")          
      sensor_value_1 = data_1[sensor_key_1].lower()

      try:
         sensor_value_1 = str(sensor_value_1).lower()
      except:
         pass
      
      
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
      
      try:
         value_1 = str(value_1).lower()
      except:
         pass
         
      try:
         value_2 = str(value_2).lower()
      except:
         pass     
      
      ##################
      # get sensordata 1
      ##################     

      data_1 = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device_ieeeAddr_1).last_values)
   
      sensor_key_1   = sensor_key_1.replace(" ","")          
      sensor_value_1 = data_1[sensor_key_1]
      
      try:
         sensor_value_1 = str(sensor_value_1).lower()
      except:
         pass

      ##################
      # get sensordata 2
      ##################     

      data_2 = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device_ieeeAddr_2).last_values)
   
      sensor_key_2   = sensor_key_2.replace(" ","")          
      sensor_value_2 = data_2[sensor_key_2]

      try:
         sensor_value_2 = str(sensor_value_2).lower()
      except:
         pass
         

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
 
      try:
         value_1 = str(value_1).lower()
      except:
         pass
         
      try:
         value_2 = str(value_2).lower()
      except:
         pass     
      
      try:
         value_3 = str(value_3).lower()
      except:
         pass   
                    
              
      ##################
      # get sensordata 1
      ##################     

      data_1 = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device_ieeeAddr_1).last_values)
   
      sensor_key_1   = sensor_key_1.replace(" ","")          
      sensor_value_1 = data_1[sensor_key_1]
      
      try:
         sensor_value_1 = str(sensor_value_1).lower()
      except:
         pass
      
      ##################
      # get sensordata 2
      ##################     
      
      data_2 = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device_ieeeAddr_2).last_values)
   
      sensor_key_2   = sensor_key_2.replace(" ","")          
      sensor_value_2 = data_2[sensor_key_2]

      try:
         sensor_value_2 = str(sensor_value_2).lower()
      except:
         pass

      ##################
      # get sensordata 3
      ##################     

      data_3 = json.loads(GET_MQTT_DEVICE_BY_IEEEADDR(device_ieeeAddr_3).last_values)
   
      sensor_key_3   = sensor_key_3.replace(" ","")          
      sensor_value_3 = data_3[sensor_key_3]

      try:
         sensor_value_3 = str(sensor_value_3).lower()
      except:
         pass

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
            if task.operator_3 == "=" and task.value_3.isdigit():
               if int(sensor_value_3) == int(task.value_3):
                  passing_2 = True    
               else:
                  passing_2 = False      
            else:
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
            if task.operator_1 == "=" and task.value_1.isdigit():
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
          (task.operator_main_1 == "and" or task.operator_main_1 == "or")):
              
         # passing value 1

         try:              
            if task.operator_1 == "=" and task.value_1.isdigit():
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
            if task.operator_2 == "=" and task.value_2.isdigit():
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
            if task.operator_3 == "=" and task.value_3.isdigit():
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
   
   print("SENSORTASK_RESULT: " + str(passing))
                                          
   return passing


def CHECK_SCHEDULER_PING(task):

   ip_addresses = task.ip_addresses.split(",")

   for ip_address in ip_addresses:
      
      if ping(ip_address, timeout=1) != None:
          return "True"
      if ping(ip_address, timeout=1) != None:
          return "True"
      if ping(ip_address, timeout=1) != None:
          return "True"                
   
   return "False"

         
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

