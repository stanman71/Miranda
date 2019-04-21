import paho.mqtt.client as mqtt
import datetime
import time
import json

from app import app
from app.database.database import *
from app.components.file_management import *

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
				
		incoming_ieeeAddr = message.topic
		incoming_ieeeAddr = incoming_ieeeAddr.split("/")
		incoming_ieeeAddr = incoming_ieeeAddr[2]
		
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
	WRITE_LOGFILE_SYSTEM("EVENT", 'MQTT >>> Broker >>> ' + BROKER_ADDRESS + ' >>> connected') 
	 
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
         messages = READ_LOGFILE_MQTT("mqtt", "SmartHome/mqtt/log",5)

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
            messages = READ_LOGFILE_MQTT("zigbee2mqtt", "SmartHome/zigbee2mqtt/bridge/log",5)
            
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

   input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr, 5)

   # message not found
   if input_messages == "Message nicht gefunden":
      channel = "SmartHome/" + device_gateway + "/" + device_ieeeAddr + "/get"
      MQTT_PUBLISH(channel, "")    

      time.sleep(1)

      input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr, 5)    


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

   input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr, 5)

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

   input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr, 5)

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

   for task in FIND_SCHEDULER_SENSOR_TASK_INPUT(incoming_ieeeAddr):

      print("!!!!!!!")
      print(task)
      print(msg)      
      
      entry = GET_SCHEDULER_SENSOR_TASK_BY_ID(task)
      
      print(entry)
			
      # one row
      if entry.operator_main_1 == "None" or entry.operator_main_1 == None:
         device = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_1)

         print(device)
	 
         data = json.loads(msg)
         sensor_key_1   = entry.sensor_key_1.replace(" ","")        
         sensor_value_1 = data[sensor_key_1]

         print(sensor_value_1)
         print(entry.value_1)

         if entry.operator_1 == "=" and not entry.value_1.isdigit():
            if sensor_value_1 == entry.value_1:
               passing = True
               print("1")
         if entry.operator_1 == "=" and entry.value_1.isdigit():
            if int(sensor_value_1) == int(entry.value_1):
               passing = True    
               print("2")
         if entry.operator_1 == "<" and entry.value_1.isdigit():
            if int(sensor_value_1) < int(entry.value_1):
               passing = True
               print("3")
         if entry.operator_1 == ">" and entry.value_1.isdigit():
            if int(sensor_value_1) > int(entry.value_1):
               passing = True 
               print("4")

         print(passing)

         if passing == True:
            
            print(entry.name)

            WRITE_LOGFILE_SYSTEM("EVENT", 'Scheduler >>> Sensor Task >>> ' + entry.name + ' >>> started') 

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
                        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task >>> " + entry.name + " >>> " + error_message)
                        
                  except:
                     task = entry.task.split(":")
                     group_id = GET_LED_GROUP_BY_NAME(task[1]).id
                     scene_id = GET_LED_SCENE_BY_NAME(task[2]).id          
                     error_message = LED_START_SCENE(int(group_id), int(scene_id))   
                     
                     if error_message != "":
                        error_message = str(error_message)
                        error_message = error_message[1:]
                        error_message = error_message[:-1]                    
                        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task >>> " + entry.name + " >>> " + error_message)
                           
            except Exception as e:
               print(e)
               WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task >>> " + entry.name + " >>> " + str(e))      

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
                     WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task >>> " + entry.name + " >>> " + error_message)
                     
            except Exception as e:
               print(e)
               WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task >>> " + entry.name + " >>> " + str(e))      

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
                        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task >>> " + entry.name + " >>> " + error_message)              
                     
                  if task[1] == "all":
                     error_message = LED_TURN_OFF_ALL()   
                     
                     if error_message != "":
                        error_message = str(error_message)
                        error_message = error_message[1:]
                        error_message = error_message[:-1]                    
                        WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task >>> " + entry.name + " >>> " + error_message)
                        
            except Exception as e:
               print(e)
               WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task >>> " + entry.name + " >>> " + str(e))      


            # request sensordata
            try:
               if "request_sensordata" in entry.task:
                  task = entry.task.split(":")
                  error_message = MQTT_REQUEST_SENSORDATA(int(task[1]))          
                  if error_message == "":
                     WRITE_LOGFILE_SYSTEM("SUCCESS", "Scheduler >>> Sensor Task >>> " + entry.name + " >>> successful")
                  else:
                     WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task >>> " + entry.name + " >>> " + error_message)
            except Exception as e:
               print(e)
               WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler >>> Sensor Task >>> " + entry.name + " >>> " + str(e))              

