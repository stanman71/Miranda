import paho.mqtt.client as mqtt
import json
import time
import threading
import heapq

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.mqtt_functions import MQTT_SAVE_SENSORDATA, MQTT_UPDATE_DEVICES
from app.components.control_scheduler import SCHEDULER_TIME_PROCESS, SCHEDULER_SENSOR_PROCESS, SCHEDULER_PING_PROCESS, GET_SUNRISE_TIME, GET_SUNSET_TIME
from app.components.control_controller import CONTROLLER_PROCESS
from app.speechcontrol.speech_control_tasks import SPEECH_RECOGNITION_PROVIDER_TASKS

BROKER_ADDRESS = GET_CONFIG_MQTT_BROKER()


""" ################################ """
""" ################################ """
"""          process management      """
""" ################################ """
""" ################################ """


""" ################ """
""" management queue """
""" ################ """

# https://www.bogotobogo.com/python/python_PriorityQueue_heapq_Data_Structure.php

process_management_queue = []

def ADD_TASK_TO_PROCESS_MANAGEMENT(priority, task_type, task_id, ieeeAddr = "", msg = "", speech_recognition_answer = ""):
	global process_management_queue
   
	heapq.heappush(process_management_queue, (priority, task_type, task_id, ieeeAddr, msg, speech_recognition_answer))


def PROCESS_MANAGEMENT_THREAD():
	global process_management_queue
   
	while True:
      
		try:
			process = heapq.heappop(process_management_queue)[1:]
			
			if process[0] == "time":
				task = GET_SCHEDULER_TASK_BY_ID(process[1])
				SCHEDULER_TIME_PROCESS(task)
			
			if process[0] == "sensor":
				task     = GET_SCHEDULER_TASK_BY_ID(process[1])
				ieeeAddr = process[2]
				SCHEDULER_SENSOR_PROCESS(task, ieeeAddr)    	         
         
			if process[0] == "ping":
				task = GET_SCHEDULER_TASK_BY_ID(process[1])
				SCHEDULER_PING_PROCESS(task)    
							  
			if process[0] == "controller":
				ieeeAddr = process[2]
				msg      = process[3]
				CONTROLLER_PROCESS(ieeeAddr, msg)    	    

			if process[0] == "speech_control":
				speech_recognition_answer = process[4]
				SPEECH_RECOGNITION_PROVIDER_TASKS(speech_recognition_answer)  				     
			  
		except:
			pass
      
		time.sleep(0.25)
   
       
Thread = threading.Thread(target=PROCESS_MANAGEMENT_THREAD)
Thread.start() 


""" ################################ """
""" ################################ """
"""               mqtt               """
""" ################################ """
""" ################################ """


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


# start MQTT
if GET_GLOBAL_SETTING_VALUE("mqtt") == "True":
    try:
        print("###### Start MQTT ######")
        Thread = threading.Thread(target=MQTT_THREAD)	
        Thread.start()

    except Exception as e:
        print("Fehler in MQTT: " + str(e))
        WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | " + str(e)) 


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
					ADD_TASK_TO_PROCESS_MANAGEMENT(5, "sensor", task.id, ieeeAddr, "")

			# save sensor data of passive devices
			if FIND_SENSORDATA_JOB_INPUT(ieeeAddr) != "":
				list_jobs = FIND_SENSORDATA_JOB_INPUT(ieeeAddr)
				
				for job in list_jobs:
					MQTT_SAVE_SENSORDATA(job) 

		# controller inputs
		if device_type == "controller":
			ADD_TASK_TO_PROCESS_MANAGEMENT(1, "controller", "", ieeeAddr, msg, "")		
	

""" ################################ """
""" ################################ """
"""             zigbee               """
""" ################################ """
""" ################################ """

 
# start zigbee    
if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") == "True":
    
    time.sleep(3)
    
    if READ_LOGFILE_MQTT("zigbee2mqtt", "",5) != "Message nicht gefunden":
        WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | No connection") 
    
    # set pairing setting  
    pairing_setting = GET_ZIGBEE2MQTT_PAIRING()    
    if pairing_setting == "True":
        channel = "SmartHome/zigbee2mqtt/bridge/config/permit_join"
        MQTT_PUBLISH(channel, "true")   
    else:
        channel = "SmartHome/zigbee2mqtt/bridge/config/permit_join"
        MQTT_PUBLISH(channel, "false")

# disable pairing
if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") != "True":
    try:
        channel = "SmartHome/zigbee2mqtt/bridge/config/permit_join"
        MQTT_PUBLISH(channel, "false") 
    except:
        pass


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
			ADD_TASK_TO_PROCESS_MANAGEMENT(10, "time", task.id)
         

@scheduler.task('cron', id='scheduler_ping', second='0, 10, 20, 30, 40, 50')
def scheduler_ping():
   
	for task in GET_ALL_SCHEDULER_TASKS():
		if task.option_position == "checked":
			ADD_TASK_TO_PROCESS_MANAGEMENT(10, "ping", task.id)


""" ################################ """
""" ################################ """
"""          speech control          """
""" ################################ """
""" ################################ """


""" ######### """
"""  snowboy  """
""" ######### """


from app.speechcontrol.snowboy import snowboydetect
from app.speechcontrol.snowboy import snowboydecoder
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL
from app.speechcontrol.speech_recognition_provider import SPEECH_RECOGNITION_PROVIDER

import sys
import signal

interrupted = False

def signal_handler(signal, frame):
   global interrupted
   interrupted = True

def interrupt_callback():
   global interrupted
   return interrupted


def SNOWBOY_START():

	signal.signal(signal.SIGINT, signal_handler)

	sensitivity_value = GET_SNOWBOY_SETTINGS().sensitivity / 100

	hotword_file = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().snowboy_hotword

	# check hotword files exist
	if hotword_file in GET_ALL_HOTWORD_FILES():
   
		# voice models here:
		models = GET_SPEECH_RECOGNITION_PROVIDER_HOTWORD(GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().snowboy_hotword)
      
		sensitivity_value = GET_SNOWBOY_SETTINGS().sensitivity / 100

		# modify sensitivity for better detection / accuracy
		detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity_value)  
      
		def detect_callback():
			detector.terminate()
			MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().microphone, "on")
	 
			speech_recognition_answer = SPEECH_RECOGNITION_PROVIDER(GET_SNOWBOY_SETTINGS().timeout)
	 
			if speech_recognition_answer != None:
			
				if "could not" in speech_recognition_answer or "Could not" in speech_recognition_answer:	 
					WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control | " + speech_recognition_answer) 
				
				else:	 
					ADD_TASK_TO_PROCESS_MANAGEMENT(1, "speech_control", "", "", "", speech_recognition_answer)	 

			MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().microphone, "off")

			detector.start(detected_callback=detect_callback, interrupt_check=interrupt_callback, sleep_time=0.03)

		WRITE_LOGFILE_SYSTEM("EVENT", "Speech Control | started") 

		# main loop
		detector.start(detected_callback=detect_callback,
						interrupt_check=interrupt_callback,
						sleep_time=0.03)

		detector.terminate()

	else:
		WRITE_LOGFILE_SYSTEM("ERROR", "Speech Control | Snowboy Hotword - " + hotword_file + " | not founded")

