import paho.mqtt.client as mqtt
import datetime
import time
import json

import threading

from threading import Thread

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.scheduler_tasks import SCHEDULER_SENSOR_TASKS
from app.components.mqtt_functions import MQTT_SAVE_SENSORDATA


BROKER_ADDRESS = GET_CONFIG_MQTT_BROKER()

saved_sensordata = []


""" #################### """
""" mqtt receive message """
""" #################### """


def MQTT_START():

	def on_message(client, userdata, message):  
		msg = str(message.payload.decode("utf-8"))
		print("message topic: ", message.topic)		
		print("message received: ", msg)

		if "zigbee" not in message.topic:
			WRITE_LOGFILE_MQTT("mqtt", message.topic, msg)
		else:
			WRITE_LOGFILE_MQTT("zigbee2mqtt", message.topic, msg)


		incoming_topic = message.topic
		incoming_topic = incoming_topic.split("/")

		try:
			if incoming_topic[3] == "get" or incoming_topic[3] == "log":
				pass  
		except:
			incoming_ieeeAddr = incoming_topic[2]

			# input sensor data 
			if FIND_SENSORDATA_JOB_INPUT(incoming_ieeeAddr) != "":
				list_jobs = FIND_SENSORDATA_JOB_INPUT(incoming_ieeeAddr)
				for job in list_jobs:
					MQTT_SAVE_SENSORDATA(job) 

			# save message
			MQTT_SAVE_SENSORDATA_TEMP(incoming_ieeeAddr, msg)   

			# schedular sensor thread
			SCHEDULER_SENSOR_THREAD(incoming_ieeeAddr)
   
         

	def on_connect(client, userdata, flags, rc):
		client.subscribe("SmartHome/#")

	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	 
	client.connect(BROKER_ADDRESS)
	 
	print("Connected to MQTT Broker: " + BROKER_ADDRESS)
	WRITE_LOGFILE_SYSTEM("EVENT", "MQTT | started") 
	WRITE_LOGFILE_SYSTEM("EVENT", "MQTT | Broker - " + BROKER_ADDRESS + " | connected") 
	 
	client.loop_forever()


""" #################### """
""" mqtt publish message """
""" #################### """


def MQTT_PUBLISH(MQTT_TOPIC, MQTT_MSG):

   try:
      def on_publish(client, userdata, mid):
         print ('Message Published...')

      client = mqtt.Client()
      client.on_publish = on_publish
      client.connect(BROKER_ADDRESS) 
      client.publish(MQTT_TOPIC,MQTT_MSG)
      client.disconnect()

      return ""

   except:
      return "Keine Verbindung zu MQTT"
	

""" ##################### """
"""  save sensordata temp """
""" ##################### """


def MQTT_SAVE_SENSORDATA_TEMP(incoming_ieeeAddr, msg):

   global saved_sensordata
   
   entry_exist = False
   
   for entry in saved_sensordata:
      if entry.split(">>>")[0] == incoming_ieeeAddr:
         entry_exist = True   

   if entry_exist == False:
      new_sensordata = incoming_ieeeAddr + ">>>" + msg
      saved_sensordata.append(new_sensordata)
      
   print("#######")
   print(saved_sensordata)
   print("#######")
   

""" ################ """
""" scheduler sensor """
""" ################ """

def SCHEDULER_SENSOR_THREAD(incoming_ieeeAddr):
   
   tasks = FIND_SCHEDULER_SENSOR_TASK_INPUT(incoming_ieeeAddr)
   
   print(tasks)
  
   for task in tasks:
      task = threading.Thread(target=SCHEDULER_SENSOR_TASK_CHECK, args=(task,))
      task.start()   

   # reset saved_sensordata after 10 seconds
   class waiter(Thread):
      def run(self):
         global saved_sensordata
         time.sleep(10)
         saved_sensordata = []
   waiter().start()      
      
      
      
def SCHEDULER_SENSOR_TASK_CHECK(task):
   
   passing = False   
   
   global saved_sensordata   
   
   entry = GET_SCHEDULER_SENSOR_TASK_BY_ID(task)
   
   print("!!!!!!!")
   print(entry.name)
   

   # #######
   # one row
   # #######
   
   if entry.operator_main_1 == "None" or entry.operator_main_1 == None:
      
      device_gateway_1  = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_1).gateway
      device_ieeeAddr_1 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_1).ieeeAddr
      sensor_key_1      = entry.sensor_key_1
      value_1           = entry.value_1
    
      
      ##################
      # get sensordata 1
      ##################     
      
      msg_1 = ""  

      for sensordata in saved_sensordata:
         if sensordata.split(">>>")[0] == device_ieeeAddr_1:
            msg_1 = sensordata.split(">>>")[1]
            
      # if value not found repeat process
      
      if msg_1 == "":
         channel = "SmartHome/" + device_gateway_1 + "/" + device_ieeeAddr_1 + "/get"
         MQTT_PUBLISH(channel, "")              

         time.sleep(2)
         
         for sensordata in saved_sensordata:
            if sensordata.split(">>>")[0] == device_ieeeAddr_1:
               msg_1 = sensordata.split(">>>")[1]
            
         if msg_1 == "":
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Sensor Task - " + entry.name + 
                                 " | Sensor - " + device_ieeeAddr_1 + " | Message not founded")     
            

      data_1 = json.loads(msg_1)
   
      sensor_key_1   = sensor_key_1.replace(" ","")          
      sensor_value_1 = data_1[sensor_key_1]

      print(sensor_value_1)
      print(value_1)

      
      ####################
      # compare conditions
      ####################
      
      passing_1 = False
           
      
      if entry.operator_1 == "=" and not entry.value_1.isdigit():
         if sensor_value_1 == entry.value_1:
            passing = True
         else:
            passing = False
      if entry.operator_1 == "=" and entry.value_1.isdigit():
         if int(sensor_value_1) == int(entry.value_1):
            passing = True    
         else:
            passing = False
      if entry.operator_1 == "<" and entry.value_1.isdigit():
         if int(sensor_value_1) < int(entry.value_1):
            passing = True
         else:
            passing = False
      if entry.operator_1 == ">" and entry.value_1.isdigit():
         if int(sensor_value_1) > int(entry.value_1):
            passing = True 
         else:
            passing = False


   # ########
   # two rows
   # ########
   
   if ((entry.operator_main_1 != "None" and entry.operator_main_1 != None) and 
       (entry.operator_main_2 == "None" or entry.operator_main_2 == None)):
          
      device_gateway_1 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_1).gateway
      device_gateway_2 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_2).gateway

      device_ieeeAddr_1 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_1).ieeeAddr
      device_ieeeAddr_2 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_2).ieeeAddr
      
      sensor_key_1 = entry.sensor_key_1
      sensor_key_2 = entry.sensor_key_2
      value_1      = entry.value_1
      value_2      = entry.value_2
      
      
      ##################
      # get sensordata 1
      ##################     
      
      msg_1 = ""  

      for sensordata in saved_sensordata:
         if sensordata.split(">>>")[0] == device_ieeeAddr_1:
            msg_1 = sensordata.split(">>>")[1]
            
      # if value not found repeat process
      
      if msg_1 == "":
         channel = "SmartHome/" + device_gateway_1 + "/" + device_ieeeAddr_1 + "/get"
         MQTT_PUBLISH(channel, "")              

         time.sleep(3)
         
         for sensordata in saved_sensordata:
            if sensordata.split(">>>")[0] == device_ieeeAddr_1:
               msg_1 = sensordata.split(">>>")[1]
            
         if msg_1 == "":
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Sensor Task - " + entry.name + 
                                 " | Sensor - " + device_ieeeAddr_1 + " | Message not founded")     
            

      data_1 = json.loads(msg_1)
   
      sensor_key_1   = sensor_key_1.replace(" ","")          
      sensor_value_1 = data_1[sensor_key_1]

      print(sensor_value_1)
      print(value_1)
      
      
      ##################
      # get sensordata 2
      ##################     
      
      msg_2 = ""  

      for sensordata in saved_sensordata:
         if sensordata.split(">>>")[0] == device_ieeeAddr_2:
            msg_2 = sensordata.split(">>>")[1]
            
      # if value not found repeat process
      
      if msg_2 == "":
         channel = "SmartHome/" + device_gateway_2 + "/" + device_ieeeAddr_2 + "/get"
         MQTT_PUBLISH(channel, "")              

         time.sleep(3)

         for sensordata in saved_sensordata:
            if sensordata.split(">>>")[0] == device_ieeeAddr_2:
               msg_2 = sensordata.split(">>>")[1]
            
         if msg_2 == "":
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Sensor Task - " + entry.name + 
                                 " | Sensor - " + device_ieeeAddr_2 + " | Message not founded")     

      data_2 = json.loads(msg_2)
   
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
   
      if ((entry.operator_main_1 == ">" or entry.operator_main_1 == "<" or entry.operator_main_1 == "=") and
          (sensor_value_1 != "Message nicht gefunden" and sensor_value_2 != "Message nicht gefunden")):
         
         if entry.operator_main_1 == "=":
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
                  
         if entry.operator_main_1 == "<":
            if int(sensor_value_1) < int(sensor_value_2):
               passing = True
            else:
               passing = False
               
         if entry.operator_main_1 == ">":
            if int(sensor_value_1) > int(sensor_value_2):
               passing = True 
            else:
               passing = False         
     
      # Options: and, or
               
      if entry.operator_main_1 == "and" or entry.operator_main_1 == "or":
         
         # get passing value one
         
         passing_1 = False
         
         try:
            if entry.operator_1 == "=" and not entry.value_1.isdigit() and sensor_value_1 != "Message nicht gefunden":
               if sensor_value_1 == entry.value_1:
                  passing_1 = True
               else:
                  passing_1 = False
         except:
            pass
            
         try:  
            if entry.operator_1 == "=" and entry.value_1.isdigit():
               if int(sensor_value_1) == int(entry.value_1):
                  passing_1 = True    
               else:
                  passing_1 = False
         except:
            pass
            
         try:                   
            if entry.operator_1 == "<" and entry.value_1.isdigit():
               if int(sensor_value_1) < int(entry.value_1):
                  passing_1 = True
               else:
                  passing_1 = False
         except:
            pass
            
         try:                       
            if entry.operator_1 == ">" and entry.value_1.isdigit():
               if int(sensor_value_1) > int(entry.value_1):
                  passing_1 = True 
               else:
                  passing_1 = False   
         except:
            pass                    
               
         print("Passing_1:" + str(passing_1))
                 
         
         # get passing value two
         
         passing_2 = False
            
         try:             
            if entry.operator_2 == "=" and not entry.value_2.isdigit() and sensor_value_1 != "Message nicht gefunden":
               if sensor_value_2 == entry.value_2:
                  passing_2 = True
               else:
                  passing_2 = False
         except:
            pass
            
         try: 
            if entry.operator_2 == "=" and entry.value_2.isdigit():
               if int(sensor_value_2) == int(entry.value_2):
                  passing_2 = True    
               else:
                  passing_2 = False
         except:
            pass
            
         try: 
            if entry.operator_2 == "<" and entry.value_2.isdigit():
               if int(sensor_value_2) < int(entry.value_2):
                  passing_2 = True
               else:
                  passing_2 = False
         except:
            pass
            
         try:                                
            if entry.operator_2 == ">" and entry.value_2.isdigit():
               if int(sensor_value_2) > int(entry.value_2):
                  passing_2 = True 
               else:
                  passing_2 = False   
         except:
            pass                    
               
               
         print("Passing_2:" + str(passing_2))
         
               
         # get result
         
         if entry.operator_main_1 == "and":
            if passing_1 == True and passing_2 == True:
               passing = True
            else:
               passing = False
                     
         if entry.operator_main_1 == "or":
            if passing_1 == True or passing_2 == True:
               passing = True         
            else:
               passing = False
      
   
   # ##########
   # three rows
   # ##########
   
   if ((entry.operator_main_1 != "None" and entry.operator_main_1 != None) and 
       (entry.operator_main_2 != "None" and entry.operator_main_2 != None)):
          
      device_gateway_1 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_1).gateway
      device_gateway_2 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_2).gateway
      device_gateway_3 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_3).gateway

      device_ieeeAddr_1 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_1).ieeeAddr
      device_ieeeAddr_2 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_2).ieeeAddr
      device_ieeeAddr_3 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_3).ieeeAddr
      
      sensor_key_1 = entry.sensor_key_1
      sensor_key_2 = entry.sensor_key_2
      sensor_key_3 = entry.sensor_key_3
      value_1      = entry.value_1
      value_2      = entry.value_2
      value_3      = entry.value_3
      
      
      ##################
      # get sensordata 1
      ##################     
      
      msg_1 = ""  

      for sensordata in saved_sensordata:
         if sensordata.split(">>>")[0] == device_ieeeAddr_1:
            msg_1 = sensordata.split(">>>")[1]
            
      # if value not found repeat process
      
      if msg_1 == "":
         channel = "SmartHome/" + device_gateway_1 + "/" + device_ieeeAddr_1 + "/get"
         MQTT_PUBLISH(channel, "")              

         time.sleep(3)
         
         for sensordata in saved_sensordata:
            if sensordata.split(">>>")[0] == device_ieeeAddr_1:
               msg_1 = sensordata.split(">>>")[1]
            
         if msg_1 == "":
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Sensor Task - " + entry.name + 
                                 " | Sensor - " + device_ieeeAddr_1 + " | Message not founded")   

      data_1 = json.loads(msg_1)
   
      sensor_key_1   = sensor_key_1.replace(" ","")          
      sensor_value_1 = data_1[sensor_key_1]

      print(sensor_value_1)
      print(value_1)
      
      
      ##################
      # get sensordata 2
      ##################     
      
      msg_2 = ""  

      for sensordata in saved_sensordata:
         if sensordata.split(">>>")[0] == device_ieeeAddr_2:
            msg_2 = sensordata.split(">>>")[1]
            
      # if value not found repeat process
      
      if msg_2 == "":
         channel = "SmartHome/" + device_gateway_2 + "/" + device_ieeeAddr_2 + "/get"
         MQTT_PUBLISH(channel, "")              

         time.sleep(3)
         
         for sensordata in saved_sensordata:
            if sensordata.split(">>>")[0] == device_ieeeAddr_2:
               msg_2 = sensordata.split(">>>")[1]
            
         if msg_2 == "":
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Sensor Task - " + entry.name + 
                                 " | Sensor - " + device_ieeeAddr_2 + " | Message not founded")  

      data_2 = json.loads(msg_2)
   
      sensor_key_2   = sensor_key_2.replace(" ","")          
      sensor_value_2 = data_2[sensor_key_2]

      print(sensor_value_2)
      print(value_2)


      ##################
      # get sensordata 3
      ##################     
      
      msg_3 = ""  

      for sensordata in saved_sensordata:
         if sensordata.split(">>>")[0] == device_ieeeAddr_3:
            msg_3 = sensordata.split(">>>")[1]
            
      # if value not found repeat process
      
      if msg_3 == "":
         channel = "SmartHome/" + device_gateway_3 + "/" + device_ieeeAddr_3 + "/get"
         MQTT_PUBLISH(channel, "")              

         time.sleep(3)
         
         for sensordata in saved_sensordata:
            if sensordata.split(">>>")[0] == device_ieeeAddr_3:
               msg_3 = sensordata.split(">>>")[1]
            
         if msg_3 == "":
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Sensor Task - " + entry.name + 
                                 " | Sensor - " + device_ieeeAddr_3 + " | Message not founded")  

      data_3 = json.loads(msg_3)
   
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
      
      if ((entry.operator_main_1 == ">" or entry.operator_main_1 == "<" or entry.operator_main_1 == "=") and
          (entry.operator_main_2 == "and" or entry.operator_main_2 == "or")):
         
         # passing value 1

         try:               
            if entry.operator_main_1 == "=":
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
            if entry.operator_main_1 == "<":
               if int(sensor_value_1) < int(sensor_value_2):
                  passing_1 = True
               else:
                  passing_1 = False      
         except:
            pass
            
         try:                    
            if entry.operator_main_1 == ">":
               if int(sensor_value_1) > int(sensor_value_2):
                  passing_1 = True 
               else:
                  passing_1 = False            
         except:
            pass
                              
         # passing value 2
         
         try:   
            if entry.operator_3 == "=" and not entry.value_3.isdigit():
               try:
                  if int(sensor_value_3) == int(entry.value_3):
                     passing_2 = True    
                  else:
                     passing_2 = False      
               except:
                  if sensor_value_3 == entry.value_3:
                     passing_2 = True    
                  else:
                     passing_2 = False                  
         except:
            pass
            
         try:                       
            if entry.operator_3 == "<" and entry.value_3.isdigit():
               if int(sensor_value_3) < int(entry.value_3):
                  passing_2 = True
               else:
                  passing_2 = False      
         except:
            pass
            
         try:                     
            if entry.operator_3 == ">" and entry.value_3.isdigit():
               if int(sensor_value_3) > int(entry.value_3):
                  passing_2 = True 
               else:
                  passing_2 = False                               
         except:
            pass
            
            
         print(passing_1)
         print(passing_2)  
            
                
         # get result
        
         if entry.operator_main_2 == "and":
            if passing_1 == True and passing_2 == True:
               passing = True
            else:
               passing = False
                     
         if entry.operator_main_2 == "or":
            if passing_1 == True or passing_2 == True:
               passing = True         
            else:
               passing = False   

      # Options: and, or /// <, >, =                   

      if ((entry.operator_main_1 == "and" or entry.operator_main_1 == "or") and
          (entry.operator_main_2 == "<" or entry.operator_main_2 == ">" or entry.operator_main_2 == "=")):
         
         # passing value 1
            
         try:   
            if entry.operator_1 == "=" and not entry.value_1.isdigit():
               try:
                  if int(sensor_value_1) == int(entry.value_1):
                     passing_1 = True    
                  else:
                     passing_1 = False      
               except:
                  if sensor_value_1 == entry.value_1:
                     passing_1 = True    
                  else:
                     passing_1 = False                 
         except:
            pass
            
         try:                       
            if entry.operator_1 == "<" and entry.value_1.isdigit():
               if int(sensor_value_1) < int(entry.value_1):
                  passing_1 = True
               else:
                  passing_1 = False      
         except:
            pass
            
         try:                     
            if entry.operator_1 == ">" and entry.value_1.isdigit():
               if int(sensor_value_1) > int(entry.value_1):
                  passing_1 = True 
               else:
                  passing_1 = False          
         except:
            pass
            
         # passing value 2
            
         try:              
            if entry.operator_main_2 == "=":
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
            if entry.operator_main_2 == "<":
               if int(sensor_value_2) < int(sensor_value_3):
                  passing_2 = True
               else:
                  passing_2 = False      
         except:
            pass
            
         try:                     
            if entry.operator_main_2 == ">":
               if int(sensor_value_2) > int(sensor_value_3):
                  passing_2 = True 
               else:
                  passing_2 = False                               
         except:
            pass
            
            
         print(passing_1)
         print(passing_2)
            
               
         # get result
         
         if entry.operator_main_1 == "and":
            if passing_1 == True and passing_2 == True:
               passing = True
            else:
               passing = False
                     
         if entry.operator_main_1 == "or":
            if passing_1 == True or passing_2 == True:
               passing = True         
            else:
               passing = False   

      # Options: <, >, = /// <, >, =          
               
      if ((entry.operator_main_1 == "<" or entry.operator_main_1 == ">" or entry.operator_main_1 == "=") and
          (entry.operator_main_2 == "<" or entry.operator_main_2 == ">" or entry.operator_main_2 == "=")):
         
         try:              
            if entry.operator_main_1 == "=" and entry.operator_main_2 == "=":
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
            if entry.operator_main_1 == "=" and entry.operator_main_2 == ">":
               if (int(sensor_value_1) == int(sensor_value_2)) > int(sensor_value_3):
                  passing = True
               else:
                  passing = False                         
         except:
            pass
            
         try:                    
            if entry.operator_main_1 == "<" and entry.operator_main_2 == ">":
               if int(sensor_value_1) < int(sensor_value_2) > int(sensor_value_3):
                  passing = True
               else:
                  passing = False      
         except:
            pass
            
         try:                     
            if entry.operator_main_1 == ">" and entry.operator_main_2 == ">":
               if int(sensor_value_1) > int(sensor_value_2) > int(sensor_value_3):
                  passing = True
               else:
                  passing = False                         
         except:
            pass
            
         try:                                         
            if entry.operator_main_1 == "=" and entry.operator_main_2 == "<":
               if (int(sensor_value_1) == int(sensor_value_2)) < int(sensor_value_3):
                  passing = True
               else:
                  passing = False                         
         except:
            pass
            
         try:                   
            if entry.operator_main_1 == "<" and entry.operator_main_2 == "<":
               if int(sensor_value_1) < int(sensor_value_2) < int(sensor_value_3):
                  passing = True
               else:
                  passing = False      
         except:
            pass
            
         try:                    
            if entry.operator_main_1 == ">" and entry.operator_main_2 == "<":
               if int(sensor_value_1) > int(sensor_value_2) < int(sensor_value_3):
                  passing = True
               else:
                  passing = False                             
         except:
            pass
            
         try:                     
            if entry.operator_main_1 == "<" and entry.operator_main_2 == "=":
               if int(sensor_value_1) < (int(sensor_value_2) == int(sensor_value_3)):
                  passing = True
               else:
                  passing = False                                
         except:
            pass
            
         try:                     
            if entry.operator_main_1 == ">" and entry.operator_main_2 == "=":
               if int(sensor_value_1) > (int(sensor_value_2) == int(sensor_value_3)):
                  passing = True
               else:
                  passing = False        
         except:
            pass
            
            
      # Options: and, or /// and, or
               
      if ((entry.operator_main_1 == "and" or entry.operator_main_1 == "or") and 
          (entry.operator_main_1 == "and" or entry.operator_main_1 == "or") and
          (sensor_value_1 != "Message nicht gefunden" or sensor_value_2 != "Message nicht gefunden" 
           or sensor_value_3 != "Message nicht gefunden")):
              
         # passing value 1

         try:              
            if entry.operator_1 == "=" and not entry.value_1.isdigit():
               if int(sensor_value_1) == int(entry.value_1):
                  passing_1 = True    
               else:
                  passing_1 = False      
            else:
               if sensor_value_1 == entry.value_1:
                  passing_1 = True    
               else:
                  passing_1 = False               
         except:
            pass
            
         try:                       
            if entry.operator_1 == "<" and entry.value_1.isdigit():
               if int(sensor_value_1) < int(entry.value_1):
                  passing_1 = True
               else:
                  passing_1 = False      
         except:
            pass
            
         try:                     
            if entry.operator_1 == ">" and entry.value_1.isdigit():
               if int(sensor_value_1) > int(entry.value_1):
                  passing_1 = True 
               else:
                  passing_1 = False       
         except:
            pass
             
         # passing value 2

         try:              
            if entry.operator_2 == "=" and not entry.value_2.isdigit():
               if int(sensor_value_2) == int(entry.value_2):
                  passing_2 = True    
               else:
                  passing_2 = False      
            else:
               if sensor_value_2 == entry.value_2:
                  passing_2 = True    
               else:
                  passing_2 = False   
         except:
            pass
            
         try:                       
            if entry.operator_2 == "<" and entry.value_2.isdigit():
               if int(sensor_value_2) < int(entry.value_2):
                  passing_2 = True
               else:
                  passing_2 = False      
         except:
            pass
            
         try:                    
            if entry.operator_2 == ">" and entry.value_2.isdigit():
               if int(sensor_value_2) > int(entry.value_2):
                  passing_2 = True 
               else:
                  passing_2 = False        
         except:
            pass
               
         # passing value 3

         try:              
            if entry.operator_3 == "=" and not entry.value_3.isdigit():
               if int(sensor_value_3) == int(entry.value_3):
                  passing_3 = True    
               else:
                  passing_3 = False      
            else:
               if sensor_value_3 == entry.value_3:
                  passing_3 = True    
               else:
                  passing_3 = False                  
         except:
            pass
            
         try:                       
            if entry.operator_3 == "<" and entry.value_3.isdigit():
               if int(sensor_value_3) < int(entry.value_3):
                  passing_3 = True
               else:
                  passing_3 = False      
         except:
            pass
            
         try:                     
            if entry.operator_3 == ">" and entry.value_3.isdigit():
               if int(sensor_value_3) > int(entry.value_3):
                  passing_3 = True 
               else:
                  passing_3 = False       
         except:
            pass
            
            
         print(passing_1)
         print(passing_2)
         print(passing_3)
         

         # get result

         try:              
            if entry.operator_main_1 == "and" and entry.operator_main_2 == "and":
               if passing_1 == True and passing_2 == True and passing_3 == True:
                  passing = True
               else:
                  passing = False
         except:
            pass
            
         try:                           
            if entry.operator_main_1 == "and" and entry.operator_main_2 == "or":
               if passing_1 == True and (passing_2 == True or passing_3 == True):
                  passing = True         
               else:
                  passing = False    
         except:
            pass
            
         try:                    
            if entry.operator_main_1 == "or" and entry.operator_main_2 == "and":
               if (passing_1 == True or passing_2 == True) and passing_3 == True:
                  passing = True         
               else:
                  passing = False                         
         except:
            pass
            
         try:                                 
            if entry.operator_main_1 == "or" and entry.operator_main_2 == "or":
               if passing_1 == True or passing_2 == True or passing_3 == True:
                  passing = True         
               else:
                  passing = False    
         except:
            pass                                      
        
               
   # Options ended
                                          
   print(passing)
   
   if passing == True:
      
      SCHEDULER_SENSOR_TASKS(entry)
