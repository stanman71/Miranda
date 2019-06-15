import json

from app import app
from app.components.control_led import *
from app.database.database import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM
from app.components.mqtt import *


""" ###################### """
"""   controller process   """
""" ###################### """     

def CONTROLLER_PROCESS(ieeeAddr, msg):
	
	for controller in GET_ALL_CONTROLLER():
		
		if controller.mqtt_device_ieeeAddr == ieeeAddr:
			
			data = json.loads(msg)
			
			#command_1
			try:
				command_1_key   = controller.command_1.split("=")[0]
				command_1_key   = command_1_key.replace(" ", "")
				command_1_value = controller.command_1.split("=")[1]
				command_1_value = command_1_value.replace(" ", "")

				if str(data[command_1_key]) == str(command_1_value):
					START_CONTROLLER_TASK(controller.task_1, controller.mqtt_device.name, controller.command_1)
					break
		   
			except Exception as e:
				if "list index out of range" not in str(e) and command_1_key not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_1 + " | " + str(e))    
				
			#command_2
			try:
				command_2_key   = controller.command_2.split("=")[0]
				command_2_key   = command_2_key.replace(" ", "")
				command_2_value = controller.command_2.split("=")[1]
				command_2_value = command_2_value.replace(" ", "")

				if str(data[command_2_key]) == str(command_2_value):
					START_CONTROLLER_TASK(controller.task_2, controller.mqtt_device.name, controller.command_2)
					break

			except Exception as e:
				if "list index out of range" not in str(e) and command_2_key not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_2 + " | " + str(e))    

			#command_3
			try:
				command_3_key   = controller.command_3.split("=")[0]
				command_3_key   = command_3_key.replace(" ", "")
				command_3_value = controller.command_3.split("=")[1]
				command_3_value = command_3_value.replace(" ", "")

				if str(data[command_3_key]) == str(command_3_value):
					START_CONTROLLER_TASK(controller.task_3, controller.mqtt_device.name, controller.command_3)
					break

			except Exception as e:
				if "list index out of range" not in str(e) and command_3_key not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_3 + " | " + str(e))    
	
			#command_4
			try:
				command_4_key   = controller.command_4.split("=")[0]
				command_4_key   = command_4_key.replace(" ", "")
				command_4_value = controller.command_4.split("=")[1]
				command_4_value = command_4_value.replace(" ", "")

				if str(data[command_4_key]) == str(command_4_value):
					START_CONTROLLER_TASK(controller.task_4, controller.mqtt_device.name, controller.command_4)
					break

			except Exception as e:
				if "list index out of range" not in str(e) and command_4_key not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_4 + " | " + str(e))    
				
			#command_5
			try:
				command_5_key   = controller.command_5.split("=")[0]
				command_5_key   = command_5_key.replace(" ", "")
				command_5_value = controller.command_5.split("=")[1]
				command_5_value = command_5_value.replace(" ", "")

				if str(data[command_5_key]) == str(command_5_value):
					START_CONTROLLER_TASK(controller.task_5, controller.mqtt_device.name, controller.command_5)
					break

			except Exception as e:
				if "list index out of range" not in str(e) and command_5_key not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_5 + " | " + str(e))    
	
			#command_6
			try:
				command_6_key   = controller.command_6.split("=")[0]
				command_6_key   = command_6_key.replace(" ", "")
				command_6_value = controller.command_6.split("=")[1]
				command_6_value = command_6_value.replace(" ", "")
				
				if str(data[command_6_key]) == str(command_6_value):
					START_CONTROLLER_TASK(controller.task_6, controller.mqtt_device.name, controller.command_6)
					break
						
			except Exception as e:
				if "list index out of range" not in str(e) and command_6_key not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_6 + " | " + str(e))    

			#command_7
			try:	
				command_7_key   = controller.command_7.split("=")[0]
				command_7_key   = command_7_key.replace(" ", "")
				command_7_value = controller.command_7.split("=")[1]
				command_7_value = command_7_value.replace(" ", "")

				if str(data[command_7_key]) == str(command_7_value):
					START_CONTROLLER_TASK(controller.task_7, controller.mqtt_device.name, controller.command_7)
					break
						 
			except Exception as e:
				if "list index out of range" not in str(e) and command_7_key not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_7 + " | " + str(e))    
				
			#command_8
			try:
				command_8_key   = controller.command_8.split("=")[0]
				command_8_key   = command_8_key.replace(" ", "")
				command_8_value = controller.command_8.split("=")[1]
				command_8_value = command_8_value.replace(" ", "")

				if str(data[command_8_key]) == str(command_8_value):
					START_CONTROLLER_TASK(controller.task_8, controller.mqtt_device.name, controller.command_8)
					break
						
			except Exception as e:
				if "list index out of range" not in str(e) and command_8_key not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_8 + " | " + str(e))    
	
			#command_9
			try:
				command_9_key   = controller.command_9.split("=")[0]
				command_9_key   = command_9_key.replace(" ", "")
				command_9_value = controller.command_9.split("=")[1]
				command_9_value = command_9_value.replace(" ", "")

				if str(data[command_9_key]) == str(command_9_value):
					START_CONTROLLER_TASK(controller.task_9, controller.mqtt_device.name, controller.command_9)
					break

			except Exception as e:
				if "list index out of range" not in str(e) and command_9_key not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_9 + " | " + str(e))    	


""" ################ """
"""  scheduler tasks """
""" ################ """


def START_CONTROLLER_TASK(task, controller_name, controller_command):
   
    # ###########
	# start scene
	# ###########
	
	if "scene" in task:
		
		task  = task.split(":")
		group = GET_LED_GROUP_BY_NAME(task[1])

		try:
			brightness = int(task[3])
		except:
			brightness = 100

		# new led setting ?
		if group.current_setting != task[2] and int(group.current_brightness) != brightness:

			group = GET_LED_GROUP_BY_NAME(task[1])
			scene = GET_LED_SCENE_BY_NAME(task[2])     

			LED_SET_SCENE(group.id, scene.id, brightness) 
			LED_ERROR_CHECKING_THREAD(group.id, scene.id, task[2], brightness, 2, 10)      

		else:
			WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | " + task[2] + " : " + str(brightness))     			
           
	# #################
	# change brightness
	# #################
	
	if "brightness" in task:
		task = task.split(":")
		group   = GET_LED_GROUP_BY_NAME(task[1])
		command = task[2]
		
		scene_name = GET_LED_GROUP_BY_NAME(task[1]).current_setting
		
		# led_group off ?
		if scene_name != "OFF":
		
			scene = GET_LED_SCENE_BY_NAME(scene_name)
			
			# get new brightness_value
			current_brightness = GET_LED_GROUP_BY_NAME(task[1]).current_brightness

			if command == "turn_up" and current_brightness != 100:
				
				target_brightness = int(current_brightness) + 20

				if target_brightness > 100:
					target_brightness = 100
					
				LED_SET_BRIGHTNESS_DIMMER(group.id, "turn_up") 
				LED_ERROR_CHECKING_THREAD(group.id, scene.id, scene_name, target_brightness, 2, 10) 		
				
	
			elif command == "turn_down" and current_brightness != 0:
				
				target_brightness = int(current_brightness) - 20

				if target_brightness < 0:
					target_brightness = 0   
			
				LED_SET_BRIGHTNESS_DIMMER(group.id, "turn_down") 
				LED_ERROR_CHECKING_THREAD(group.id, scene.id, scene_name, target_brightness, 2, 10) 
				
			else:
				WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | " + scene_name + " : " + str(current_brightness) + " %")	
				

		else:
			WRITE_LOGFILE_SYSTEM("WARNING", "LED | Group - " + group.name + " | OFF : 0 %") 	

    # #######
	# led off
	# #######
	
	if "led_off" in task:
		task = task.split(":")
 
		if task[1] == "group":
			
			# get input group names and lower the letters
			
			try:
				list_groups = task[2].split(",")
			except:
				list_groups = [task[2]]
			  
			for input_group_name in list_groups: 
				input_group_name = input_group_name.replace(" ", "")
		   
				group_founded = False
		   
			# get exist group names 
			for group in GET_ALL_LED_GROUPS():
		   
				if input_group_name.lower() == group.name.lower():

					group_founded = True
		 
					# new led setting ?
					if group.current_setting != "OFF":

						scene_name = group.current_setting
						scene      = GET_LED_SCENE_BY_NAME(scene_name)
						
						LED_TURN_OFF_GROUP(group.id)
						LED_ERROR_CHECKING_THREAD(group.id, scene.id, "OFF", 0, 2, 10)       

					else:
						WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %") 		     
		 

			if group_founded == False:
				WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | Group - " + input_group_name + " | not founded")
					
		   
		if task[1] == "all":
			
			for group in GET_ALL_LED_GROUPS():

				# new led setting ?
				if group.current_setting != "OFF":

					scene_name = group.current_setting
					scene      = GET_LED_SCENE_BY_NAME(scene_name)

					LED_TURN_OFF_GROUP(group.id)
					LED_ERROR_CHECKING_THREAD(group.id, scene.id, "OFF", 0, 2, 10)       
				  
				else:
					WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %") 

	# ######
	# device
	# ######
	
	if "device" in task:
		task = task.split(":")
	
		try:
			device  = GET_MQTT_DEVICE_BY_NAME(task[1].lower())
			command = task[2].upper()
			
			# new device setting ?
			if command != device.previous_command:
				
				if device.gateway == "mqtt":

					channel = "SmartHome/mqtt/" + device.ieeeAddr + "/set"
					msg     = '{"state": "' + command + '"}'

					MQTT_PUBLISH(channel, msg) 
					MQTT_CHECK_SETTING_THREAD(device.ieeeAddr, "state", command, 5, 20)


				if device.gateway == "zigbee2mqtt":

					channel = "SmartHome/zigbee2mqtt/" + device.name + "/set"
					msg     = '{"state": "' + command + '"}'

					MQTT_PUBLISH(channel, msg) 
					ZIGBEE2MQTT_CHECK_SETTING_THREAD(device.name, "state", command, 5, 20)

			else:

				if device.gateway == "mqtt":
					WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + device.name + " | " + str(command)) 

				if device.gateway == "zigbee2mqtt":
					WRITE_LOGFILE_SYSTEM("STATUS", "Zigbee2MQTT | Device - " + device.name + " | " + str(command))  
										
		except:
			WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | Gerät - " + task[1] + " | not founded")
						
