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
			WRITE_LOGFILE_MQTT("zigbee", message.topic, msg)
				
		device = message.topic
		device = device.split("/")
		device = device[2]
		
	   # input sensor data 
		if FIND_SENSORDATA_JOB_INPUT(device) != "":
			job_id = FIND_SENSORDATA_JOB_INPUT(device)
			SAVE_MQTT_SENSORDATA(job_id)   
			
			
		if FIND_TASKMANAGEMENT_SENSOR_TASK_INPUT(device) != "":
			task_id = FIND_TASKMANAGEMENT_SENSOR_TASK_INPUT(device)
			print(task_id)
			       

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
	
	
def CHECK_MQTT():
   MQTT_PUBLISH("SmartHome/mqtt/test", "") 


def UPDATE_MQTT_DEVICES(gateway):
   
   if gateway == "mqtt":
      
      MQTT_PUBLISH("SmartHome/mqtt/devices", "")  
      time.sleep(2)

      try:
         messages = READ_LOGFILE_MQTT("mqtt", "SmartHome/mqtt/log")

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

      except Exception as e:
         if str(e) == "string index out of range":
            WRITE_LOGFILE_SYSTEM("ERROR", "MQTT >>> No connection")    


   if gateway == "zigbee":

      MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/devices", "")  
       
      for i in range (0,5):

         try:
            messages = READ_LOGFILE_MQTT("zigbee", "SmartHome/zigbee2mqtt/bridge/log")
            
            if messages != "Message nicht gefunden" and messages != "Keine Verbindung zu ZigBee2MQTT":
               for message in messages:
                     message = str(message[2])
                     message = message.replace("'","")

                     data = json.loads(message)
                  
                     if (data['type']) == "devices":
                        for device in (data['message']):

                           name     = device['friendly_name']
                           gateway  = "zigbee"                        
                           ieeeAddr = device['ieeeAddr']
                           model    = device['model']

                           ADD_MQTT_DEVICE(name, gateway, ieeeAddr, model)
         
         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee >>> " + str(e))            


def REQUEST_MQTT_SENSORDATA(job_id):
   sensordata_job  = GET_SENSORDATA_JOB_BY_ID(job_id)
   device_gateway  = sensordata_job.mqtt_device.gateway
   device_ieeeAddr = sensordata_job.mqtt_device.ieeeAddr  
   sensor_key = sensordata_job.sensor_key
   sensor_key = sensor_key.replace(" ", "")
 
   channel = "SmartHome/" + device_gateway + "/" + device_ieeeAddr + "/get"
   MQTT_PUBLISH(channel, "")  

   time.sleep(2)

   input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr)

   for input_message in input_messages:
      input_message = str(input_message[2])
      
      data = json.loads(input_message)

   filename = sensordata_job.filename

   WRITE_SENSORDATA_FILE(filename, device_ieeeAddr, sensor_key, data[sensor_key])
   
   
def SAVE_MQTT_SENSORDATA(job_id):
   sensordata_job  = GET_SENSORDATA_JOB_BY_ID(job_id)
   device_gateway  = sensordata_job.mqtt_device.gateway
   device_ieeeAddr = sensordata_job.mqtt_device.ieeeAddr  
   sensor_key = sensordata_job.sensor_key
   sensor_key = sensor_key.replace(" ", "")

   input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr)

   for input_message in input_messages:
      input_message = str(input_message[2])
      
      data = json.loads(input_message)

   filename = sensordata_job.filename

   WRITE_SENSORDATA_FILE(filename, device_ieeeAddr, sensor_key, data[sensor_key])