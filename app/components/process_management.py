import heapq
import re

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.process_scheduler import SCHEDULER_TIME_PROCESS, SCHEDULER_SENSOR_PROCESS, SCHEDULER_PING_PROCESS
from app.components.process_controller import CONTROLLER_PROCESS
from app.components.mqtt import *
from app.components.control_led import *
from app.components.shared_resources import process_management_queue
from app.components.tasks import START_SPEECHCONTROL_TASK
from app.components.control_watering import START_WATERING_THREAD

""" ################ """
""" management queue """
""" ################ """

# https://www.bogotobogo.com/python/python_PriorityQueue_heapq_Data_Structure.php

def PROCESS_MANAGEMENT_THREAD():
	
	while True:
		
		try:
			process = heapq.heappop(process_management_queue)[1]
			
			
			# ############
			#  controller
			# ############
			
			if process[0] == "controller":
				ieeeAddr = process[1]
				msg      = process[2]
				
				CONTROLLER_PROCESS(ieeeAddr, msg)    	    
				
				
			# ###########
			#  dashboard
			# ###########
				
			if process[0] == "dashboard":
					
						
				if process[1] == "led_scene":
					group_id          = process[2]
					scene_id          = process[3] 
					brightness_global = process[4]
					
					LED_SET_SCENE(group_id, scene_id, brightness_global)
				
				
				if process[1] == "led_brightness":
					group_id          = process[2]
					brightness_global = process[3]	
									
					LED_SET_BRIGHTNESS(group_id, brightness_global)
					
					
				if process[1] == "led_off_group":
					group_id          = process[2]
										
					LED_TURN_OFF_GROUP(group_id)
				
				
				if process[1] == "device":
					channel = process[2]
					msg     = process[3]
					
					MQTT_PUBLISH(channel, msg)					
	
	
			# #########
			#  program
			# #########
	
			if process[0] == "program":
				
				
				if process[1] == "device":
					MQTT_PUBLISH(process[2], process[3])	
					
				if process[1] == "led_rgb": 
					led_name      = process[2]
					rgb_values    = re.findall(r'\d+', process[3])
					led_brightnes = process[4]
					
					SETTING_LED_RGB(led_name, rgb_values[0], rgb_values[1], rgb_values[2], led_brightnes)
					
					ZIGBEE2MQTT_CHECK_SETTING_THREAD(led_name, '{"brightnes":' + str(led_brightnes) + '}', 2, 10)
				
				
				if process[1] == "led_white":
					led_name      = process[2]
					color_temp    = process[3]
					led_brightnes = process[4]		
							
					SETTING_LED_WHITE(led_name, color_temp, led_brightness)
					
					ZIGBEE2MQTT_CHECK_SETTING_THREAD(led_name, '{"brightness":' + str(led_brightness) + '}', 2, 10)
					
					
				if process[1] == "led_simple":
					led_name       = process[2]
					led_brightness = process[3]	
									
					SETTING_LED_SIMPLE(led_name, led_brightness)
					
					ZIGBEE2MQTT_CHECK_SETTING_THREAD(led_name, '{"brightness":' + str(led_brightness) + '}', 2, 10)


				if process[1] == "turn_off":
					led_name      = process[2]
					
					SETTING_LED_TURN_OFF(led_name)
					
					ZIGBEE2MQTT_CHECK_SETTING_THREAD(led_name, '{"state":"OFF"}', 2, 10)			
				
					
			# ###########
			#  scheduler
			# ###########
									
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


			# ###############
			#  speechcontrol
			# ###############

			if process[0] == "speechcontrol":
				speech_recognition_answer = process[1]
				
				START_SPEECHCONTROL_TASK(speech_recognition_answer)  					
			
				
			# ##########
			#  watering
			# ##########
				
			if process[0] == "watering" and process[1] == "start":
				ieeeAddr = process[2]
				START_WATERING_THREAD(ieeeAddr)
				
				
			if process[0] == "watering" and process[1] != "start":
				channel = process[1]
				msg     = process[2]
				
				MQTT_PUBLISH(channel, msg)	
				
				
		except Exception as e:
			if "index out of range" not in str(e):
				WRITE_LOGFILE_SYSTEM("ERROR", "Process Management | Process - " + process + " | " + str(e))  
				print(str(e))
				
			  
		time.sleep(0.2)
   
