import json

from app import app
from app.database.database import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM
from app.components.tasks import START_CONTROLLER_TASK


""" ###################### """
"""   controller process   """
""" ###################### """     

def CONTROLLER_PROCESS(ieeeAddr, msg):
	
	for controller in GET_ALL_CONTROLLER():
		
		if controller.mqtt_device_ieeeAddr == ieeeAddr:
			
			json_data_event = json.loads(msg)
			
			#command_1
			try:
				# special case aqara cube
				json_data_command_1 = json.loads(controller.command_1)
				
				if "side" in controller.command_1:
					command_1_value = json_data_command_1["side"]
					
					if str(json_data_event["to_side"]) == str(command_1_value) or str(json_data_event["from_side"]) == str(command_1_value): 
						START_CONTROLLER_TASK(controller.task_1, controller.mqtt_device.name, controller.command_1)
						break		
						
				else:		
					if str(controller.command_1)[1:-1] in str(msg):
						START_CONTROLLER_TASK(controller.task_1, controller.mqtt_device.name, controller.command_1)
						break
		   
			except Exception as e:
				if "list index out of range" not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_1 + " | " + str(e))    
				
				
			#command_2
			try:
				# special case aqara cube
				json_data_command_2 = json.loads(controller.command_2)
				
				if "side" in controller.command_2:
					command_2_value = json_data_command_2["side"]
					
					if str(json_data_event["to_side"]) == str(command_2_value) or str(json_data_event["from_side"]) == str(command_2_value): 
						START_CONTROLLER_TASK(controller.task_2, controller.mqtt_device.name, controller.command_2)
						break		
						
				else:		
					if str(controller.command_2)[1:-1] in str(msg):
						START_CONTROLLER_TASK(controller.task_2, controller.mqtt_device.name, controller.command_2)
						break
		   
			except Exception as e:
				if "list index out of range" not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_2 + " | " + str(e))    
				
				
			#command_3
			try:
				# special case aqara cube
				json_data_command_3 = json.loads(controller.command_3)
				
				if "side" in controller.command_3:
					command_3_value = json_data_command_3["side"]
					
					if str(json_data_event["to_side"]) == str(command_3_value) or str(json_data_event["from_side"]) == str(command_3_value): 
						START_CONTROLLER_TASK(controller.task_3, controller.mqtt_device.name, controller.command_3)
						break		
						
				else:		
					if str(controller.command_3)[1:-1] in str(msg):
						START_CONTROLLER_TASK(controller.task_3, controller.mqtt_device.name, controller.command_3)
						break
		   
			except Exception as e:
				if "list index out of range" not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_2 + " | " + str(e))    
				
				
			#command_4
			try:
				# special case aqara cube
				json_data_command_4 = json.loads(controller.command_4)
				
				if "side" in controller.command_4:
					command_4_value = json_data_command_4["side"]
					
					if str(json_data_event["to_side"]) == str(command_4_value) or str(json_data_event["from_side"]) == str(command_4_value): 
						START_CONTROLLER_TASK(controller.task_4, controller.mqtt_device.name, controller.command_4)
						break		
						
				else:		
					if str(controller.command_4)[1:-1] in str(msg):
						START_CONTROLLER_TASK(controller.task_4, controller.mqtt_device.name, controller.command_4)
						break
		   
			except Exception as e:
				if "list index out of range" not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_4 + " | " + str(e))    
				
				
			#command_5
			try:
				# special case aqara cube
				json_data_command_5 = json.loads(controller.command_5)
				
				if "side" in controller.command_5:
					command_5_value = json_data_command_5["side"]
					
					if str(json_data_event["to_side"]) == str(command_5_value) or str(json_data_event["from_side"]) == str(command_5_value): 
						START_CONTROLLER_TASK(controller.task_5, controller.mqtt_device.name, controller.command_5)
						break		
						
				else:		
					if str(controller.command_5)[1:-1] in str(msg):
						START_CONTROLLER_TASK(controller.task_5, controller.mqtt_device.name, controller.command_5)
						break
		   
			except Exception as e:
				if "list index out of range" not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_5 + " | " + str(e))    
				
				
			#command_6
			try:
				# special case aqara cube
				json_data_command_6 = json.loads(controller.command_6)
				
				if "side" in controller.command_6:
					command_6_value = json_data_command_6["side"]
					
					if str(json_data_event["to_side"]) == str(command_6_value) or str(json_data_event["from_side"]) == str(command_6_value): 
						START_CONTROLLER_TASK(controller.task_6, controller.mqtt_device.name, controller.command_6)
						break		
						
				else:		
					if str(controller.command_6)[1:-1] in str(msg):
						START_CONTROLLER_TASK(controller.task_6, controller.mqtt_device.name, controller.command_6)
						break
		   
			except Exception as e:
				if "list index out of range" not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_6 + " | " + str(e))    
				
				
			#command_7
			try:
				# special case aqara cube
				json_data_command_7 = json.loads(controller.command_7)
				
				if "side" in controller.command_7:
					command_7_value = json_data_command_7["side"]
					
					if str(json_data_event["to_side"]) == str(command_7_value) or str(json_data_event["from_side"]) == str(command_7_value): 
						START_CONTROLLER_TASK(controller.task_7, controller.mqtt_device.name, controller.command_7)
						break		
						
				else:		
					if str(controller.command_7)[1:-1] in str(msg):
						START_CONTROLLER_TASK(controller.task_7, controller.mqtt_device.name, controller.command_7)
						break
		   
			except Exception as e:
				if "list index out of range" not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_7 + " | " + str(e))    
				
				
			#command_8
			try:
				# special case aqara cube
				json_data_command_8 = json.loads(controller.command_8)
				
				if "side" in controller.command_8:
					command_8_value = json_data_command_8["side"]
					
					if str(json_data_event["to_side"]) == str(command_8_value) or str(json_data_event["from_side"]) == str(command_8_value): 
						START_CONTROLLER_TASK(controller.task_8, controller.mqtt_device.name, controller.command_8)
						break		
						
				else:		
					if str(controller.command_8)[1:-1] in str(msg):
						START_CONTROLLER_TASK(controller.task_8, controller.mqtt_device.name, controller.command_8)
						break
		   
			except Exception as e:
				if "list index out of range" not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_8 + " | " + str(e))    
				
				
			#command_9
			try:
				# special case aqara cube
				json_data_command_9 = json.loads(controller.command_9)
				
				if "side" in controller.command_9:
					command_9_value = json_data_command_9["side"]
					
					if str(json_data_event["to_side"]) == str(command_9_value) or str(json_data_event["from_side"]) == str(command_9_value): 
						START_CONTROLLER_TASK(controller.task_9, controller.mqtt_device.name, controller.command_9)
						break		
						
				else:		
					if str(controller.command_9)[1:-1] in str(msg):
						START_CONTROLLER_TASK(controller.task_9, controller.mqtt_device.name, controller.command_9)
						break
		   
			except Exception as e:
				if "list index out of range" not in str(e):
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller.mqtt_device.name + " | Command - " + controller.command_9 + " | " + str(e))    
				
								
				
