import paho.mqtt.client as mqtt
import datetime
import json

from app import app
from app.database.database import *
from app.components.file_management import *

BROKER_ADDRESS = GET_CONFIG_MQTT_BROKER()


moisture_current = 0

def SET_MOISTURE_CURRENT(value):
	global moisture_current
	moisture_current = value

def GET_MOISTURE_CURRENT():
	global moisture_current
	return moisture_current
	

def MQTT_START():
 
	def on_message(client, userdata, message):
		msg = str(message.payload.decode("utf-8"))
		print("message topic: ", message.topic)		
		print("message received: ", msg)

		WRITE_LOGFILE_MQTT(message.topic, msg)
		
		channel         = message.topic 
		channel_path    = channel.split("/")[2]	
		channel_content = channel.split("/")[3]	
		
		time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		# update device informations	
		for device in GET_ALL_MQTT_DEVICES():
			if channel_path == device.channel_path and channel_content == "deviceinformation":
				data = json.loads(msg)
				UPDATE_MQTT_DEVICE_INFORMATIONS(device.id, data["devicetype"], data["inputs"], data["outputs"], time)

		# get current moisture value	
		if channel_path == "data" and channel_content == "plant":
			SET_MOISTURE_CURRENT(int(msg))
					
		# write sensor data	
		if channel_path == "data" and channel_content == "sensor":
			msg = msg.split("/")
			# filename / device / sensor / value
			WRITE_SENSORDATA_FILE(msg[0], msg[1], msg[2], msg[3])			

	
	def on_connect(client, userdata, flags, rc):
		client.subscribe("/SmartHome/#")

	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	 
	client.connect(BROKER_ADDRESS)
	 
	print("Connected to MQTT Broker: " + BROKER_ADDRESS)
	WRITE_LOGFILE_SYSTEM("EVENT", "MQTT >>> started") 
	WRITE_LOGFILE_SYSTEM("EVENT", 'MQTT >>> Broker >>> ' + BROKER_ADDRESS + ' >>> connected') 
	 
	client.loop_forever()


def MQTT_PUBLISH(MQTT_TOPIC, MQTT_MSG):
	def on_publish(client, userdata, mid):
		print ("Message Published...")

	client = mqtt.Client()
	client.on_publish = on_publish
	client.connect(BROKER_ADDRESS) 
	client.publish(MQTT_TOPIC,MQTT_MSG)
	client.disconnect()