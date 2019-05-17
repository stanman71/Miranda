import paho.mqtt.client as mqtt

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.control_scheduler import SCHEDULER_MAIN
from app.components.mqtt_functions import MQTT_SAVE_SENSORDATA


BROKER_ADDRESS = GET_CONFIG_MQTT_BROKER()

forbitten_topics = []


""" #################### """
""" mqtt receive message """
""" #################### """


def MQTT_START():

	def on_message(client, userdata, message): 
      
		global forbitten_topics 
      
		msg = str(message.payload.decode("utf-8"))
            
		##############################################
		# waiter tread to prevent messages from router

		import threading

		def WAITER_TREAD(topic):
			global forbitten_topics

			time.sleep(5)

			if topic in forbitten_topics:
				forbitten_topics.remove(topic)

		############################################## 
      
		if message.topic not in forbitten_topics:
         
			# get ieeeAddr
			incoming_topic   = message.topic
			incoming_topic   = incoming_topic.split("/")
			mqtt_device_name = incoming_topic[2]
         
			try:
				ieeeAddr = GET_MQTT_DEVICE_BY_NAME(mqtt_device_name).ieeeAddr
			except:
				ieeeAddr = mqtt_device_name


			try:
				# ignore incomming messages for 5 seconds, exept controller 
				if GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr).device_type != "controller":
				
					forbitten_topics.append(message.topic)

					# start waiter tread
					t = threading.Thread(target=WAITER_TREAD, args=(message.topic,))
					t.start()      

			except:
				pass


			print("message topic: ", message.topic)		
			print("message received: ", msg)


			# write data in logs
			if "zigbee" not in message.topic:
				WRITE_LOGFILE_MQTT("mqtt", message.topic, msg)
			else:
				WRITE_LOGFILE_MQTT("zigbee2mqtt", message.topic, msg)


			# start functions
			try:
				if incoming_topic[3] == "get":
					pass
				if incoming_topic[3] == "log":
					pass              
				if incoming_topic[3] == "networkmap" and incoming_topic[4] == "graphviz":

					# generate graphviz diagram
					from graphviz import Source, render

					src = Source(msg)
					src.render(filename = GET_PATH() + '/app/static/images/zigbee_topology', format='png', cleanup=True) 

				if incoming_topic[3] == "networkmap":
					pass  

			except:

				# save last values
				SET_MQTT_DEVICE_LAST_VALUES(ieeeAddr, msg) 
				
				# schedular
				SCHEDULER_MAIN("sensor", ieeeAddr)

				# save sensor data of passive devices
				if FIND_SENSORDATA_JOB_INPUT(ieeeAddr) != "":
					list_jobs = FIND_SENSORDATA_JOB_INPUT(ieeeAddr)
					
					for job in list_jobs:
						MQTT_SAVE_SENSORDATA(job) 




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
	
