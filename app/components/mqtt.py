import paho.mqtt.client as mqtt
import datetime
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
      return "Keine Verbindung zu ZigBee2MQTT"
	
	
def CHECK_MQTT():
   MQTT_PUBLISH("SmartHome/mqtt/devices", "") 


def UPDATE_MQTT_DEVICES():
   MQTT_PUBLISH("SmartHome/mqtt/devices", "")  
   time.sleep(2)

   try:
      messages = READ_LOGFILE_MQTT("mqtt", "SmartHome/mqtt/log")

      if messages != "Message nicht gefunden" and messages != "Keine Verbindung zu MQTT":
         for message in messages:

            message = str(message[2])

            data = json.loads(message)

            name     = data['ieeeAddr']
            ieeeAddr = data['ieeeAddr']
            gateway  = "mqtt"
            model    = data['model']
            inputs   = data['input']
            outputs  = data['output']

            ADD_MQTT_DEVICE(name, ieeeAddr, gateway, model, inputs, outputs)    
   except:
      pass


def GET_MQTT_SENSORDATA(job_id):
   sensordata_job  = GET_SENSORDATA_JOB(job_id)
   device_gateway  = sensordata_job.mqtt_device.gateway
   device_ieeeAddr = sensordata_job.mqtt_device.ieeeAddr  
   sensor_id = sensordata_job.sensor_id
 
   channel = "SmartHome/" + device_gateway + "/" + device_ieeeAddr + "/get"
   MQTT_PUBLISH(channel, "")  

   time.sleep(2)

   input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr)

   for input_message in input_messages:
      input_message = str(input_message[2])
      
      data = json.loads(input_message)
      