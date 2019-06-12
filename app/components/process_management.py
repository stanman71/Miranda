import heapq

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.control_scheduler import SCHEDULER_TIME_PROCESS, SCHEDULER_SENSOR_PROCESS, SCHEDULER_PING_PROCESS
from app.components.control_controller import CONTROLLER_PROCESS
from app.components.mqtt import *
from app.components.shared_resources import process_management_queue
from app.speechcontrol.speech_control_tasks import SPEECH_RECOGNITION_PROVIDER_TASKS


""" ################ """
""" management queue """
""" ################ """

# https://www.bogotobogo.com/python/python_PriorityQueue_heapq_Data_Structure.php

def PROCESS_MANAGEMENT_THREAD():
	
	while True:
		
		#print(process_management_queue)

		try:
			process = heapq.heappop(process_management_queue)[1]
			
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
				ieeeAddr = process[1]
				msg      = process[2]
				CONTROLLER_PROCESS(ieeeAddr, msg)    	    

			if process[0] == "speech_control":
				speech_recognition_answer = process[1]
				SPEECH_RECOGNITION_PROVIDER_TASKS(speech_recognition_answer)  					
				
			if process[0] == "mqtt":
				MQTT_PUBLISH(process[1], process[2]) 
				
			if process[0] == "zigbee2mqtt":
				MQTT_PUBLISH(process[1], process[2]) 
				
				
		except Exception as e:
			if "index out of range" not in str(e):
				print(str(e))
      
		time.sleep(0.2)
   
