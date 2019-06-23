import paho.mqtt.client as mqtt
import heapq
import threading
import json
import datetime
import time

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.shared_resources import process_management_queue, mqtt_incomming_messages_list

BROKER_ADDRESS = GET_CONFIG_MQTT_BROKER()


""" ################################ """
""" ################################ """
"""              mqtt main           """
""" ################################ """
""" ################################ """


def MQTT_GET_INCOMMING_MESSAGES(limit):

	# get the time check value
	time_check = datetime.datetime.now() - datetime.timedelta(seconds=limit)
	time_check = time_check.strftime("%Y-%m-%d %H:%M:%S")	
	
	message_list = []
	
	for message in mqtt_incomming_messages_list:
		
		time_message = datetime.datetime.strptime(message[0],"%Y-%m-%d %H:%M:%S")   
		time_limit   = datetime.datetime.strptime(time_check, "%Y-%m-%d %H:%M:%S")

		# select messages in search_time 
		if time_message > time_limit:
			message_list.append(message)
				
	return message_list


""" #################### """
""" mqtt receive message """
""" #################### """
	
def MQTT_THREAD():

	def on_message(client, userdata, new_message): 
      
		channel = new_message.topic					
		msg     = str(new_message.payload.decode("utf-8"))	      
      
		new_message = True
		
		# log messages always passing
		if (channel != "SmartHome/mqtt/log" and 
		    channel != "SmartHome/zigbee2mqtt/bridge/log" and 
		    channel != "SmartHome/zigbee2mqtt/bridge/config" and
		    channel != "SmartHome/zigbee2mqtt/bridge/state"):
						
			# other message already arrived?
			for existing_message in MQTT_GET_INCOMMING_MESSAGES(3):	
							
				if existing_message[1] == channel:
					
					if "zigbee2mqtt" in channel:
						
						try:
							# devices changes state ?
							existing_data = json.loads(existing_message[2])
							new_data      = json.loads(msg)

							if existing_data["state"] != new_data["state"]:
								new_message = True
								break
								
						except:
							pass
							
							
						try:
							# motion sensor changes occupancy state ?
							existing_data = json.loads(existing_message[2])
							new_data      = json.loads(msg)

							if existing_data["occupancy"] != new_data["occupancy"]:
								new_message = True
								break
								
						except:
							pass							
					
					new_message = False
				
					
		# message not arrived
		if new_message:
	
			print("message topic: ", channel)		
			print("message received: ", msg)	
			
			# write data in logs
			if "mqtt" in channel:
				WRITE_LOGFILE_MQTT("mqtt", channel, msg)
				
			if "zigbee2mqtt" in channel:
				WRITE_LOGFILE_MQTT("zigbee2mqtt", channel, msg)
				
			# add message to the incoming message list
			mqtt_incomming_messages_list.append((str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), channel, msg))	
			
			# start message thread for additional processes
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

	except Exception as e:
		print("ERROR MQTT: " + str(e))
		return ("Fehler MQTT >>> " + str(e))


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
		
		# save last values and last contact 
		if ieeeAddr != "":	
			SET_MQTT_DEVICE_LAST_VALUES(ieeeAddr, msg) 


		if device_type == "sensor_passiv" or device_type == "sensor_active" or device_type == "watering_array" :
			
			# start schedular job 
			for task in GET_ALL_SCHEDULER_TASKS():
				if task.option_sensors == "checked":
					heapq.heappush(process_management_queue, (10, ("scheduler", "sensor", task.id, ieeeAddr)))

			# save sensor data of passive devices
			if FIND_SENSORDATA_JOB_INPUT(ieeeAddr) != "":
				list_jobs = FIND_SENSORDATA_JOB_INPUT(ieeeAddr)
				
				for job in list_jobs:
					MQTT_SAVE_SENSORDATA(job) 


		# start controller job
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
		
		message_founded = False

		MQTT_PUBLISH("SmartHome/mqtt/devices", "")  
		time.sleep(3)

		try:
			for message in MQTT_GET_INCOMMING_MESSAGES(5):
				
				if message[1] == "SmartHome/mqtt/log": 
					
					message_founded = True   

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


			if message_founded == True:
				WRITE_LOGFILE_SYSTEM("SUCCESS", "MQTT | Update Devices")
				return ""
				
			else:	 
				WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | Update Devices | Message not founded")
				return "MQTT | Update | Message nicht gefunden"
			
			
		except Exception as e:
			if str(e) == "string index out of range":
				WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | No connection") 
				return ("Error: " + str(e))   
	

	if gateway == "zigbee2mqtt":
		
		message_founded = False
		error = ""
	
		MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/devices", "")  
		time.sleep(2)
      
		try:

			for message in MQTT_GET_INCOMMING_MESSAGES(5):
				
				if message[1] == "SmartHome/zigbee2mqtt/bridge/log":  
					
					message_founded = True

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
								
								try:
									model      = device['model']
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

								try:          
									model = device_data.model  
									        
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
                 
                           
			if message_founded == True:
                           
				if error != "":
					WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | Update Devices | " + str(error))
					return error	
				else:
					WRITE_LOGFILE_SYSTEM("SUCCESS", "ZigBee2MQTT | Update Devices")
					return ""
								
			else:			
				WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | Update Devices | Message not founded")
				return "ZigBee2MQTT | Update Devices | Message nicht gefunden"					
			
    
		except Exception as e:
			WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | Update Devices | " + str(e))  
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
	
	for message in MQTT_GET_INCOMMING_MESSAGES(5):
		
		if message[1] == "SmartHome/" + device_gateway + "/" + device_ieeeAddr:
				
			try:

				data     = json.loads(message[2])
				filename = sensordata_job.filename
	
				WRITE_SENSORDATA_FILE(filename, device_ieeeAddr, sensor_key, data[sensor_key])
				
				if device_gateway == "mqtt":
					WRITE_LOGFILE_SYSTEM("SUCCESS", "MQTT | Sensor Data saved") 
				if device_gateway == "zigbee2mqtt":
					WRITE_LOGFILE_SYSTEM("SUCCESS", "ZigBee2MQTT | Sensor Data saved") 				
				
				return
				
			except:
				pass

	if device_gateway == "mqtt":
		WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | Message not founded") 
	if device_gateway == "zigbee2mqtt":
		WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | Message not founded") 

   
def MQTT_SAVE_SENSORDATA(job_id):
   
	sensordata_job  = GET_SENSORDATA_JOB_BY_ID(job_id)
	device_gateway  = sensordata_job.mqtt_device.gateway
	device_ieeeAddr = sensordata_job.mqtt_device.ieeeAddr 
	 
	sensor_key = sensordata_job.sensor_key
	sensor_key = sensor_key.replace(" ", "")
	
		
	for message in MQTT_GET_INCOMMING_MESSAGES(10):
		
		if message[1] == "SmartHome/" + device_gateway + "/" + device_ieeeAddr:
				
			try:

				data     = json.loads(message[2])
				filename = sensordata_job.filename
	
				WRITE_SENSORDATA_FILE(filename, device_ieeeAddr, sensor_key, data[sensor_key])
				return
				
			except:
				pass


""" ################### """
"""  mqtt check setting """
""" ################### """
 
 
def MQTT_CHECK_SETTING_THREAD(ieeeAddr, setting_key, command, delay = 1, limit = 15): 
 
	Thread = threading.Thread(target=MQTT_CHECK_SETTING_PROCESS, args=(ieeeAddr, setting_key, command, delay, limit, ))
	Thread.start()   

 
def MQTT_CHECK_SETTING_PROCESS(ieeeAddr, setting_key, command, delay, limit): 
                      
	device = GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr)
                    
	# check setting 1 try
	time.sleep(delay)                             
	result = MQTT_CHECK_SETTING(ieeeAddr, setting_key, command, limit)
	
	# set previous command 
	if result == True:
		SET_MQTT_DEVICE_PREVIOUS_COMMAND(device.ieeeAddr, command)
		WRITE_LOGFILE_SYSTEM("SUCCESS", "MQTT | Device - " + device.name + " | State changed - " + str(command)) 	
	
	else:
		# check setting 2 try
		time.sleep(delay)                             
		result = MQTT_CHECK_SETTING(ieeeAddr, setting_key, command, limit)
		
		# set previous command 
		if result == True:
			SET_MQTT_DEVICE_PREVIOUS_COMMAND(device.ieeeAddr, command)
			WRITE_LOGFILE_SYSTEM("SUCCESS", "MQTT | Device - " + device.name + " | State changed - " + str(command)) 		
			
		else:
			# check setting 3 try
			time.sleep(delay)                             
			result = MQTT_CHECK_SETTING(ieeeAddr, setting_key, command, limit)
			 
			# set previous command 
			if result == True:
				SET_MQTT_DEVICE_PREVIOUS_COMMAND(device.ieeeAddr, command)
				WRITE_LOGFILE_SYSTEM("SUCCESS", "MQTT | Device - " + device.name + " | State changed - " + str(command)) 			
				
			# error message
			else:
				SET_MQTT_DEVICE_PREVIOUS_COMMAND(device.ieeeAddr, command)
				WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | Device - " + device.name + " | Setting not confirmed")  
				return ("MQTT | Device - " + device.name + " | Setting not confirmed") 
				
	return ""
					

def MQTT_CHECK_SETTING(ieeeAddr, setting_key, command, limit):
			
	for message in MQTT_GET_INCOMMING_MESSAGES(limit):
		
		# search for fitting message in incomming_messages_list
		if message[1] == "SmartHome/mqtt/" + ieeeAddr:
				
			try:
				data = json.loads(message[2])
				
				if data[setting_key] == command:
					return True
			
			except:
				return False
		 
	return False
   

""" ########################## """
"""  zigbee2mqtt check setting """
""" ########################## """
 
 
def ZIGBEE2MQTT_CHECK_SETTING_THREAD(name, setting_key, command, delay = 1, limit = 15): 
 
	Thread = threading.Thread(target=ZIGBEE2MQTT_CHECK_SETTING_PROCESS, args=(name, setting_key, command, delay, limit, ))
	Thread.start()   

 
def ZIGBEE2MQTT_CHECK_SETTING_PROCESS(name, setting_key, command, delay, limit): 
                      
	device = GET_MQTT_DEVICE_BY_NAME(name)
	                        
	# check setting 1 try
	time.sleep(delay)                             
	result = ZIGBEE2MQTT_CHECK_SETTING(name, setting_key, command, limit)
	
	# set previous command 
	if result == True:
		SET_MQTT_DEVICE_PREVIOUS_COMMAND(device.ieeeAddr, command)
		WRITE_LOGFILE_SYSTEM("SUCCESS", "ZigBee2MQTT | Device - " + device.name + " | State changed - " + str(command))   
		
	else:
		# check setting 2 try
		time.sleep(delay)                             
		result = ZIGBEE2MQTT_CHECK_SETTING(name, setting_key, command, limit)
		
		# set previous command 
		if result == True:
			SET_MQTT_DEVICE_PREVIOUS_COMMAND(device.ieeeAddr, command)
			WRITE_LOGFILE_SYSTEM("SUCCESS", "ZigBee2MQTT | Device - " + device.name + " | State changed - " + str(command)) 			
			
		else:
			# check setting 3 try
			time.sleep(delay)                             
			result = ZIGBEE2MQTT_CHECK_SETTING(name, setting_key, command, limit)
			 
			# set previous command 
			if result == True:
				SET_MQTT_DEVICE_PREVIOUS_COMMAND(device.ieeeAddr, command)
				WRITE_LOGFILE_SYSTEM("SUCCESS", "ZigBee2MQTT | Device - " + device.name + " | State changed - " + str(command))  				
				
			# error message
			else:
				SET_MQTT_DEVICE_PREVIOUS_COMMAND(device.ieeeAddr, command)
				WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | Device - " + device.name + " | Setting not confirmed")  
				return ("ZigBee2MQTT | Device - " + device.name + " | Setting not confirmed") 
	
	return ""
		
 
def ZIGBEE2MQTT_CHECK_SETTING(name, setting_key, command, limit):
	
	for message in MQTT_GET_INCOMMING_MESSAGES(limit):	
		
		# search for fitting message in incomming_messages_list
		if message[1] == "SmartHome/zigbee2mqtt/" + name:
				
			try:
				data = json.loads(message[2])
				
				if data[setting_key] == command:
					return True
			
			except:
				return False
		 
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
