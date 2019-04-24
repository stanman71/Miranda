import paho.mqtt.client as mqtt
import datetime
import time
import json

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.led_control import *

BROKER_ADDRESS = GET_CONFIG_MQTT_BROKER()


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
			if incoming_topic[3] == "get":
				incoming_ieeeAddr = ""   
		except:
			incoming_ieeeAddr = incoming_topic[2]

		# input sensor data 
		if FIND_SENSORDATA_JOB_INPUT(incoming_ieeeAddr) != "":
			list_jobs = FIND_SENSORDATA_JOB_INPUT(incoming_ieeeAddr)
			for job in list_jobs:
				MQTT_SAVE_SENSORDATA(job) 

		# schedular sensor
		SCHEDULER_SENSOR_TASKS(incoming_ieeeAddr, msg)

	def on_connect(client, userdata, flags, rc):
		client.subscribe("SmartHome/#")

	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	 
	client.connect(BROKER_ADDRESS)
	 
	print("Connected to MQTT Broker: " + BROKER_ADDRESS)
	WRITE_LOGFILE_SYSTEM("EVENT", "MQTT >>> started") 
	WRITE_LOGFILE_SYSTEM("EVENT", "MQTT >>> Broker '" + BROKER_ADDRESS + "' >>> connected") 
	 
	client.loop_forever()


def MQTT_PUBLISH(MQTT_TOPIC, MQTT_MSG):

   try:
      def on_publish(client, userdata, mid):
         print ("Message Published...")

      client = mqtt.Client()
      client.on_publish = on_publish
      client.connect(BROKER_ADDRESS) 
      client.publish(MQTT_TOPIC,MQTT_MSG)
      client.disconnect()

      return ""

   except:
      return "Keine Verbindung zu MQTT"
	

""" ################### """
"""    update devices   """
""" ################### """

def MQTT_UPDATE_DEVICES(gateway):
   
   if gateway == "mqtt":
      
      MQTT_PUBLISH("SmartHome/mqtt/devices", "")  
      time.sleep(2)

      try:
         messages = READ_LOGFILE_MQTT("mqtt", "SmartHome/mqtt/log",30)

         if messages != "Message nicht gefunden" and messages != "Keine Verbindung zu MQTT":

            for message in messages:
               
               message = str(message[2])

               data = json.loads(message)
               
               inputs_temp = str(data['inputs'])
               inputs_temp = inputs_temp[1:]
               inputs_temp = inputs_temp[:-1]
               inputs_temp = inputs_temp.replace("'", "")
               inputs_temp = inputs_temp.replace('"', "")

               outputs_temp = str(data['outputs'])
               outputs_temp = outputs_temp[1:]
               outputs_temp = outputs_temp[:-1]
               outputs_temp = outputs_temp.replace("'", "")
               outputs_temp = outputs_temp.replace('"', "")  

               name     = data['ieeeAddr']
               gateway  = "mqtt"
               ieeeAddr = data['ieeeAddr']
               model    = data['model']
               inputs   = inputs_temp
               outputs  = outputs_temp

               ADD_MQTT_DEVICE(name, gateway, ieeeAddr, model, inputs, outputs)
               
            return ""

         else: 
	         return messages

      except Exception as e:
         if str(e) == "string index out of range":
            WRITE_LOGFILE_SYSTEM("ERROR", "MQTT >>> No connection")    


   if gateway == "zigbee2mqtt":

      MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/devices", "")  
       
      for i in range (0,5):

         try:
            messages = READ_LOGFILE_MQTT("zigbee2mqtt", "SmartHome/zigbee2mqtt/bridge/log",30)
            
            if messages != "Message nicht gefunden" and messages != "Keine Verbindung zu ZigBee2MQTT":
                for message in messages:
		  		  
                    message = str(message[2])
                    message = message.replace("'","")

                    data = json.loads(message)
                  
                    if (data['type']) == "devices":
                        for device in (data['message']):

                           # add new device
                           if not GET_MQTT_DEVICE_BY_IEEEADDR(device['ieeeAddr']):
                              name     = device['friendly_name']
                              gateway  = "zigbee2mqtt"              
                              ieeeAddr = device['ieeeAddr']
                              model    = device['model']
			      
                              ADD_MQTT_DEVICE(name, gateway, ieeeAddr, model)

                           # get device informations
                           else:
                              gateway  = "zigbee2mqtt"
                              id       = GET_MQTT_DEVICE_BY_IEEEADDR(device['ieeeAddr']).id	      
                              name     = device['friendly_name']
                              inputs   = GET_MQTT_DEVICE_BY_IEEEADDR(device['ieeeAddr']).inputs	
			      	      	      
                              SET_MQTT_DEVICE(gateway, id, name, inputs)

         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT >>> " + str(e))            


""" ################### """
"""    get sensordata   """
""" ################### """

def MQTT_GET_SENSORDATA(device_gateway, device_ieeeAddr, sensor_key):

   input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr, 30)

   print(input_messages)

   # message not found
   if input_messages == "Message nicht gefunden":
      channel = "SmartHome/" + device_gateway + "/" + device_ieeeAddr + "/get"
      MQTT_PUBLISH(channel, "")    

      input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr, 30)    


   if input_messages != "Message nicht gefunden":

      for input_message in input_messages:
         input_message = str(input_message[2])
         
         data = json.loads(input_message)
         sensor_key = sensor_key.replace(" ", "")
         return data[sensor_key]
   
   else:
      return input_messages
	  

def MQTT_REQUEST_SENSORDATA(job_id):
   sensordata_job  = GET_SENSORDATA_JOB_BY_ID(job_id)
   device_gateway  = sensordata_job.mqtt_device.gateway
   device_ieeeAddr = sensordata_job.mqtt_device.ieeeAddr  
   sensor_key = sensordata_job.sensor_key
   sensor_key = sensor_key.replace(" ", "")
 
   channel = "SmartHome/" + device_gateway + "/" + device_ieeeAddr + "/get"
   MQTT_PUBLISH(channel, "")  

   time.sleep(2)

   input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr, 30)

   if input_messages != "Message nicht gefunden":
      
      for input_message in input_messages:
         input_message = str(input_message[2])
         
         data = json.loads(input_message)

      filename = sensordata_job.filename

      WRITE_SENSORDATA_FILE(filename, device_ieeeAddr, sensor_key, data[sensor_key])

      return ""

   return "Message nicht gefunden"
   
   
def MQTT_SAVE_SENSORDATA(job_id):
   sensordata_job  = GET_SENSORDATA_JOB_BY_ID(job_id)
   device_gateway  = sensordata_job.mqtt_device.gateway
   device_ieeeAddr = sensordata_job.mqtt_device.ieeeAddr  
   sensor_key = sensordata_job.sensor_key
   sensor_key = sensor_key.replace(" ", "")

   input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr, 30)

   for input_message in input_messages:
      input_message = str(input_message[2])
      
      data = json.loads(input_message)

   filename = sensordata_job.filename

   WRITE_SENSORDATA_FILE(filename, device_ieeeAddr, sensor_key, data[sensor_key])
   
   
""" ################### """
"""     stop outputs    """
""" ################### """
   
def MQTT_STOP_ALL_OUTPUTS():
   devices = GET_ALL_MQTT_DEVICES("mqtt")
   
   for device in devices:

      if device.outputs != "" or device.outputs != None or device.outputs != "None":
         outputs = device.outputs
         outputs = outputs.replace(" ","")
         outputs = outputs.split(",")
	 
         for output in outputs:
            
            channel = "SmartHome/" + device.gateway + "/" + device.ieeeAddr + "/set"
            msg = output + ":off"

            MQTT_PUBLISH(channel, msg)
            
            time.sleep(1)
	    

""" ################ """
""" scheduler sensor """
""" ################ """

def SCHEDULER_SENSOR_TASKS(incoming_ieeeAddr, msg):

   passing = False

   tasks = FIND_SCHEDULER_SENSOR_TASK_INPUT(incoming_ieeeAddr)
   
   print(tasks)
   
   for task in tasks:
      
      print("!!!!!!!")
      print(task)
      print(msg)      
      
      entry = GET_SCHEDULER_SENSOR_TASK_BY_ID(task)
      
      print(entry.name)
      

      # #######
      # one row
      # #######
      
      if entry.operator_main_1 == "None" or entry.operator_main_1 == None:
         
         data = json.loads(msg)
         sensor_key_1   = entry.sensor_key_1.replace(" ","")        
         sensor_value_1 = data[sensor_key_1]

         print(sensor_value_1)
         print(entry.value_1)

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
         
         sensor_value_1 = MQTT_GET_SENSORDATA(device_gateway_1, device_ieeeAddr_1, sensor_key_1)
         sensor_value_2 = MQTT_GET_SENSORDATA(device_gateway_2, device_ieeeAddr_2, sensor_key_2)
         
         
         print("Sensor_1: " + str(sensor_value_1))
         print("Sesnor_2: " + str(sensor_value_2))
         
         
         if sensor_value_1 == "Message nicht gefunden":
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + 
                                 "' >>> Sensor '" +  device_ieeeAddr_1 + "' >>> Message nicht gefunden")  
            passing = False
                                 
         if sensor_value_2 == "Message nicht gefunden":
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + 
                                 "' >>> Sensor '" +  device_ieeeAddr_2 + "' >>> Message nicht gefunden")  
            passing = False
      
            
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
         
         sensor_value_1 = MQTT_GET_SENSORDATA(device_gateway_1, device_ieeeAddr_1, sensor_key_1)
         sensor_value_2 = MQTT_GET_SENSORDATA(device_gateway_2, device_ieeeAddr_2, sensor_key_2)
         sensor_value_3 = MQTT_GET_SENSORDATA(device_gateway_3, device_ieeeAddr_3, sensor_key_3)
         
         print("Sensor_1: " + str(sensor_value_1))
         print("Sesnor_2: " + str(sensor_value_2))
         print("Sesnor_3: " + str(sensor_value_3))
         
         
         if sensor_value_1 == "Message nicht gefunden":
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + 
                                 "' >>> Sensor '" +  device_ieeeAddr_1 + "' >>> Message nicht gefunden")  
            passing = False
                                 
         if sensor_value_2 == "Message nicht gefunden":
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + 
                                 "' >>> Sensor '" +  device_ieeeAddr_2 + "' >>> Message nicht gefunden")  
            passing = False
            
         if sensor_value_3 == "Message nicht gefunden":
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + 
                                 "' >>> Sensor '" +  device_ieeeAddr_3 + "' >>> Message nicht gefunden")  
            passing = False           
            
         
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
                  if int(sensor_value_1) == int(sensor_value_2) > int(sensor_value_3):
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
                  if int(sensor_value_1) == int(sensor_value_2) < int(sensor_value_3):
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
                  if int(sensor_value_1) < int(sensor_value_2) == int(sensor_value_3):
                     passing = True
                  else:
                     passing = False                                
            except:
               pass
               
            try:                     
               if entry.operator_main_1 == ">" and entry.operator_main_2 == "=":
                  if int(sensor_value_1) > int(sensor_value_2) == int(sensor_value_3):
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
               if entry.operator_2 == "=" and not entry.value_2.isdigit():
                  try:
                     if int(sensor_value_2) == int(entry.value_2):
                        passing_2 = True    
                     else:
                        passing_2 = False      
                  except:
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
                  try:
                     if int(sensor_value_3) == int(entry.value_3):
                        passing_3 = True    
                     else:
                        passing_3 = False      
                  except:
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
         
         print(entry.name)

         WRITE_LOGFILE_SYSTEM("EVENT", "Scheduler >>> Sensor Task '" + entry.name + "' >>> started") 

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
                     WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + "' >>> " + error_message)
                     
               except:
                  task = entry.task.split(":")
                  group_id = GET_LED_GROUP_BY_NAME(task[1]).id
                  scene_id = GET_LED_SCENE_BY_NAME(task[2]).id          
                  error_message = LED_START_SCENE(int(group_id), int(scene_id))   
                  
                  if error_message != "":
                     error_message = str(error_message)
                     error_message = error_message[1:]
                     error_message = error_message[:-1]                    
                     WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + "' >>> " + error_message)
                        
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + "' >>> " + str(e))      

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
                  WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + "' >>> " + error_message)
                  
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + "' >>> " + str(e))      

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
                     WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + "' >>> " + error_message)              
                  
               if task[1] == "all":
                  error_message = LED_TURN_OFF_ALL()   
                  
                  if error_message != "":
                     error_message = str(error_message)
                     error_message = error_message[1:]
                     error_message = error_message[:-1]                    
                     WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + "' >>> " + error_message)
                     
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + "' >>> " + str(e))      


         # request sensordata
         try:
            if "request_sensordata" in entry.task:
               task = entry.task.split(":")
               error_message = MQTT_REQUEST_SENSORDATA(int(task[1]))          
               if error_message == "":
                  WRITE_LOGFILE_SYSTEM("SUCCESS", "Scheduler >>> Sensor Task '" + entry.name + "' >>> successful")
               else:
                  WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + "' >>> " + error_message)
                  
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task '" + entry.name + "' >>> " + str(e))    
            
