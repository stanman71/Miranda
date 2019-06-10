import paho.mqtt.client as mqtt
import heapq
import threading
import json
import datetime
import time

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.shared_resources import process_management_queue

BROKER_ADDRESS = GET_CONFIG_MQTT_BROKER()


""" ################################ """
""" ################################ """
"""              mqtt main           """
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
		if ieeeAddr != "" and msg != "connected" and "state" not in msg:
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
	

""" ################################ """
""" ################################ """
"""           mqtt functions         """
""" ################################ """
""" ################################ """


""" ################### """
"""    update devices   """
""" ################### """


def MQTT_UPDATE_DEVICES(gateway):
   
	if gateway == "mqtt":

		MQTT_PUBLISH("SmartHome/mqtt/devices", "")  
		time.sleep(2)

		try:
			messages = READ_LOGFILE_MQTT("mqtt", "SmartHome/mqtt/log",10)

			if messages != "Message nicht gefunden" and messages != "Keine Verbindung zu MQTT":

				for message in messages:
               
					message = str(message[2])
				   
					data = json.loads(message)
				   
					inputs_temp = str(data['inputs'])
					inputs_temp = inputs_temp[1:]
					inputs_temp = inputs_temp[:-1]
					inputs_temp = inputs_temp.replace("'", "")
					inputs_temp = inputs_temp.replace('"', "")

					commands_temp = str(data['commands'])
					commands_temp = commands_temp[1:]
					commands_temp = commands_temp[:-1]
					commands_temp = commands_temp.replace("'", "")
					commands_temp = commands_temp.replace('"', "")  

					name        = data['ieeeAddr']
					gateway     = "mqtt"
					ieeeAddr    = data['ieeeAddr']
					model       = data['model']
               
					try:
						device_type = data['device_type']
					except:
						device_type = ""                 
					  
					try:
						description = data['description']
					except:
						description = ""

					try:
						inputs = inputs_temp
					except:
						inputs = ""
					  
					try:
						commands = commands_temp
					except:
						commands = ""
                  
					# add new device
					if not GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr):
						ADD_MQTT_DEVICE(name, gateway, ieeeAddr, model, device_type, description, inputs, commands)
					  
					# update existing device
					else:
						id   = GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr).id
						name = GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr).name
										
						UPDATE_MQTT_DEVICE(id, name, gateway, device_type, description, inputs, commands)
						SET_MQTT_DEVICE_LAST_CONTACT(ieeeAddr)
					  
					# update input values
					MQTT_PUBLISH("SmartHome/mqtt/" + ieeeAddr + "/get", "")  

				return ""

			else: 
				return messages

		except Exception as e:
			if str(e) == "string index out of range":
				WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | No connection") 
				return ("Error: " + str(e))   
	

	if gateway == "zigbee2mqtt":

		error = ""
	
		MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/devices", "")  
		time.sleep(2)
      
		try:
         
			messages = READ_LOGFILE_MQTT("zigbee2mqtt", "SmartHome/zigbee2mqtt/bridge/log",10)
         
			if messages != "Message nicht gefunden" and messages != "Keine Verbindung zu ZigBee2MQTT":
				
				for message in messages:
           
					message = str(message[2])
					message = message.replace("'","")

					data = json.loads(message)	
                 
					if (data['type']) == "devices":
						
						devices = (data['message'])
                     
						for i in range(0, len(devices)):
                        
							device = devices[i]
                        
							# add new device
                        
							if not GET_MQTT_DEVICE_BY_IEEEADDR(device['ieeeAddr']):
                           
								name         = device['friendly_name']
								gateway      = "zigbee2mqtt"              
								ieeeAddr     = device['ieeeAddr']
								model        = device['model']

								try:
									new_device = GET_MQTT_DEVICE_INFORMATIONS(model)
								except:
									new_device = ["", "", "", ""]
                           
								device_type = new_device[0]
								description = new_device[1]
								inputs      = new_device[2]
								commands    = new_device[3]  

								ADD_MQTT_DEVICE(name, gateway, ieeeAddr, model, device_type, description, inputs, commands)

							# update device informations
                        
							else:
                           
								device_data = GET_MQTT_DEVICE_BY_IEEEADDR(device['ieeeAddr'])

								id       = device_data.id	      
								name     = device['friendly_name']
								gateway  = "zigbee2mqtt"
								model    = device_data.model                
                        
								try:                  
									existing_device = GET_MQTT_DEVICE_INFORMATIONS(model)
                              
									device_type = existing_device[0]
									description = existing_device[1]
									inputs      = existing_device[2]
									commands    = existing_device[3]  

								except Exception as e:
									device_type = device_data.device_type
									description = device_data.description 
									inputs      = device_data.inputs
									commands    = device_data.commands	
                             
									error = "Error: >>> " + str(model) + " not founded >>> " + str(e)
                           
                                                                     
								UPDATE_MQTT_DEVICE(id, name, gateway, device_type, description, inputs, commands)
								SET_MQTT_DEVICE_LAST_CONTACT(device['ieeeAddr'])
                           
							if error != "":
								return error
							else:
								return ""
      
		except Exception as e:
			WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | " + str(e))  
			return ("Error: " + str(e))
      

""" ################### """
"""    get sensordata   """
""" ################### """


def MQTT_REQUEST_SENSORDATA(job_name):
	sensordata_job  = GET_SENSORDATA_JOB_BY_NAME(job_name)
	device_gateway  = sensordata_job.mqtt_device.gateway
	device_ieeeAddr = sensordata_job.mqtt_device.ieeeAddr  
	sensor_key = sensordata_job.sensor_key
	sensor_key = sensor_key.replace(" ", "")
 
	channel = "SmartHome/" + device_gateway + "/" + device_ieeeAddr + "/get"
	MQTT_PUBLISH(channel, "")  

	time.sleep(2)
	
	input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr, 10)

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

	input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr, 10)

	try:

		for input_message in input_messages:
			input_message = str(input_message[2])
		  
			data = json.loads(input_message)

		filename = sensordata_job.filename
		
		WRITE_SENSORDATA_FILE(filename, device_ieeeAddr, sensor_key, data[sensor_key])
	except:
		pass

                
""" ################### """
"""      set device     """
""" ################### """
   
def MQTT_SET_DEVICE_SETTING(ieeeAddr, command):
	
	gateway = GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr).gateway
	name    = GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr).name

	# create channel
	if gateway == "mqtt":
		channel = "SmartHome/" + gateway + "/" + ieeeAddr + "/set"
	else:
		channel = "SmartHome/" + gateway + "/" + name + "/set"

	# create message
	if command == "POWER_ON":
		msg           = '{"state": "ON"}'
		setting_value = "ON"
      
	if command == "POWER_OFF":
		msg           = '{"state": "OFF"}'
		setting_value = "OFF"
      
	if command == "PUMP_ON":
		msg           = '{"state": "PUMP_ON"}'
		setting_value = "PUMP_ON"
      
	if command == "PUMP_OFF":
		msg           = '{"state": "PUMP_OFF"}'
		setting_value = "PUMP_OFF"      
      
	MQTT_PUBLISH(channel, msg)   
	
	time.sleep(2)
	
	# start check function
	if gateway == "mqtt":
		check_setting = MQTT_CHECK_SETTING(ieeeAddr, "state", setting_value)
	else:
		check_setting = MQTT_CHECK_SETTING(name, "state", setting_value)
   
  
	if check_setting:
		SET_MQTT_DEVICE_PREVIOUS_COMMAND_AND_STATUS(ieeeAddr, command, setting_value)
		return ""
      
	else:
		WRITE_LOGFILE_SYSTEM("WARNING", "MQTT | Setting not confirmed >>> " + name)
	

""" ################### """
"""  mqtt check setting """
""" ################### """
 
def MQTT_CHECK_SETTING(ieeeAddr, setting_key, setting_value):
	
	try:
		gateway = GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr).gateway
	except:
		gateway = GET_MQTT_DEVICE_BY_NAME(ieeeAddr).gateway
	
	         
	input_messages = READ_LOGFILE_MQTT(gateway, "SmartHome/" + gateway + "/" + ieeeAddr, 5)
	
	if input_messages != "Message nicht gefunden":
		for input_message in input_messages:
			input_message = str(input_message[2])

			data = json.loads(input_message)
			
			if data[setting_key] == setting_value:
				return True
     
	return False
   

""" ################### """
"""      check mqtt     """
""" ################### """
 
def MQTT_CHECK():
	MQTT_PUBLISH("SmartHome/mqtt/test", "") 


def MQTT_CHECK_NAME_CHANGED():
            
	input_messages = READ_LOGFILE_MQTT("zigbee2mqtt", "SmartHome/zigbee2mqtt/bridge/log", 5)
	
	if input_messages != "Message nicht gefunden":
		for input_message in input_messages:
			input_message = str(input_message[2])
  
			data = json.loads(input_message)
            
			if data["type"] == "device_renamed":
				return True
                    
	else:
		return False
