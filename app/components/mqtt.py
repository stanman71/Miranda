import paho.mqtt.client as mqtt
import heapq
import threading

from app import app
from app.database.database import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM, WRITE_LOGFILE_MQTT, GET_CONFIG_MQTT_BROKER
from app.components.mqtt_functions import *
from app.components.config import process_management_queue

BROKER_ADDRESS = GET_CONFIG_MQTT_BROKER()


""" #################### """
""" mqtt receive message """
""" #################### """
	
def MQTT_THREAD():

	def on_message(client, userdata, message): 
      
		msg = str(message.payload.decode("utf-8"))
      
		print("message topic: ", message.topic)		
		print("message received: ", msg)	
		
		# write data in logs
		if "zigbee" not in message.topic:
			WRITE_LOGFILE_MQTT("mqtt", message.topic, msg)
		else:
			WRITE_LOGFILE_MQTT("zigbee2mqtt", message.topic, msg)
		
		
		channel = message.topic
		
		if channel != "" and channel != None:		
			Thread = threading.Thread(target=MQTT_MESSAGE_THREAD, args=(channel, msg, ))
			Thread.start()    
		
	
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
"""  mqtt message thread  """
""" ##################### """

def MQTT_MESSAGE_THREAD(channel, msg):
	
	ieeeAddr = ""
	device_type = ""

	# get ieeeAddr and device_type
	incoming_topic   = channel
	incoming_topic   = incoming_topic.split("/")
	mqtt_device_name = incoming_topic[2]
 
	mqtt_devices = GET_ALL_MQTT_DEVICES("")
 
	try:
		for device in mqtt_devices:
			if device.name == mqtt_device_name:				
				ieeeAddr = device.ieeeAddr
	except:
		ieeeAddr = mqtt_device_name

	try:
		for device in mqtt_devices:
			if device.name == mqtt_device_name:				
				device_type = device.device_type			
	except:
		device_type = ""


	# start function networkmap
	try:        
		if incoming_topic[3] == "networkmap" and incoming_topic[4] == "graphviz":

			# generate graphviz diagram
			from graphviz import Source, render

			src = Source(msg)
			src.render(filename = GET_PATH() + '/app/static/images/zigbee_topology', format='png', cleanup=True) 
	except:
		pass

	# filter sended messages
	try:
		
		if incoming_topic[3] == "get":
			pass
		if incoming_topic[3] == "set":
			pass			
		if incoming_topic[3] == "log":
			
			data = json.loads(msg)
			
			# update zigbee device table
			if data["type"] == "device_connected":
				time.sleep(1)
				MQTT_UPDATE_DEVICES("zigbee2mqtt")
					
	except:
		
		# save last values
		if ieeeAddr != "":
			SET_MQTT_DEVICE_LAST_VALUES(ieeeAddr, msg) 
		
		# sensor inputs
		if device_type == "sensor_passiv" or device_type == "sensor_active" or device_type == "watering_array" :
			
			# schedular
			for task in GET_ALL_SCHEDULER_TASKS():
				if task.option_sensors == "checked":
					heapq.heappush(process_management_queue, (5, ("sensor", task.id, ieeeAddr)))

			# save sensor data of passive devices
			if FIND_SENSORDATA_JOB_INPUT(ieeeAddr) != "":
				list_jobs = FIND_SENSORDATA_JOB_INPUT(ieeeAddr)
				
				for job in list_jobs:
					MQTT_SAVE_SENSORDATA(job) 

		# controller inputs
		if device_type == "controller":
			heapq.heappush(process_management_queue, (1, ("controller", ieeeAddr, msg)))		
	


