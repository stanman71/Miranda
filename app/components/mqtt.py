import paho.mqtt.client as mqtt
import datetime

from app import app
from app.database.database import *
from app.components.file_management import WRITE_SENSORDATA_FILE


BROKER_ADDRESS = "localhost"

def MQTT_START():
 
	def on_message(client, userdata, message):
		msg = str(message.payload.decode("utf-8"))
		print("message received: ", msg)
		print("message topic: ", message.topic)
		
		channel         = message.topic 
		channel_path    = channel.split("/")[2]	
		channel_content = channel.split("/")[3]	
		
		time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		# update device informations	
		for device in GET_ALL_MQTT_DEVICES():
			if channel_path == device.channel_path and channel_content == "deviceinformation":
				msg = msg.split("/")
				UPDATE_MQTT_DEVICE_INFORMATIONS(device.id, msg[0], msg[1], msg[2], time)

		# get current moisture value	
		if channel_path == "data" and channel_content == "plant":
			msg = msg.split("/")
			SET_PLANT_MOISTURE_CURRENT(int(msg[0]), int(msg[1]))
			
		# write sensor data	
		if channel_path == "data" and channel_content == "sensor":
			msg = msg.split("/")
			WRITE_SENSORDATA_FILE(msg[0], msg[1])			

	
	def on_connect(client, userdata, flags, rc):
		client.subscribe("/SmartHome/#")

	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	 
	client.connect(BROKER_ADDRESS)
	 
	print("Connected to MQTT Broker: " + BROKER_ADDRESS)
	 
	client.loop_forever()


def MQTT_PUBLISH(MQTT_TOPIC, MQTT_MSG):

	def on_publish(client, userdata, mid):
		print ("Message Published...")

	client = mqtt.Client()
	client.on_publish = on_publish
	client.connect(BROKER_ADDRESS) 
	client.publish(MQTT_TOPIC,MQTT_MSG)
	client.disconnect()
