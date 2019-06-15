import heapq

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.control_scheduler import SCHEDULER_TIME_PROCESS, SCHEDULER_SENSOR_PROCESS, SCHEDULER_PING_PROCESS
from app.components.control_controller import CONTROLLER_PROCESS
from app.components.mqtt import *
from app.components.control_led import *
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
			
			if process[0] == "controller":
				ieeeAddr = process[1]
				msg      = process[2]
				CONTROLLER_PROCESS(ieeeAddr, msg)    	    
				
				
			if process[0] == "dashboard":
					
				if process[1] == "led_scene":
					LED_SET_SCENE(process[2], process[3], process[4])
				
				if process[1] == "led_brightness":
					LED_SET_BRIGHTNESS(process[2], process[3])
					
				if process[1] == "led_off_group":
					LED_TURN_OFF_GROUP(process[2])
				
				if process[1] == "device":
					MQTT_PUBLISH(process[2], process[3])					
				
							
			if process[0] == "scheduler":
				
				if process[1] == "time":
					task = GET_SCHEDULER_TASK_BY_ID(process[2])
					SCHEDULER_TIME_PROCESS(task)
			
				if process[1] == "ping":
					task = GET_SCHEDULER_TASK_BY_ID(process[2])
					SCHEDULER_PING_PROCESS(task)    
						
				if process[1] == "sensor":
					task     = GET_SCHEDULER_TASK_BY_ID(process[2])
					ieeeAddr = process[3]
					SCHEDULER_SENSOR_PROCESS(task, ieeeAddr)    	         


			if process[0] == "speech_control":
				speech_recognition_answer = process[1]
				SPEECH_RECOGNITION_PROVIDER_TASKS(speech_recognition_answer)  					
				
				
			if process[0] == "watering":
				MQTT_PUBLISH(process[1], process[2])
				
				
		except Exception as e:
			if "index out of range" not in str(e):
				print(str(e))
      
		time.sleep(0.2)
   
