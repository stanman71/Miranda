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
			
			data = json.loads(msg)
			
			#command_1
			try:
				# special case aqara cube
				if "side" in controller.command_1:
					command_1_value = controller.command_1.split("=")[1]
					command_1_value = command_1_value.replace(" ", "")
					
					if str(data["to_side"]) == str(command_1_value) or str(data["from_side"]) == str(command_1_value): 
						START_CONTROLLER_TASK(controller.task_1, controller.mqtt_device.name, controller.command_1)
						break		
						
				else:				
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
				# special case aqara cube
				if "side" in controller.command_2:
					command_2_value = controller.command_2.split("=")[1]
					command_2_value = command_2_value.replace(" ", "")
					
					if str(data["to_side"]) == str(command_2_value) or str(data["from_side"]) == str(command_2_value): 
						START_CONTROLLER_TASK(controller.task_2, controller.mqtt_device.name, controller.command_2)
						break		
						
				else:				
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
				# special case aqara cube
				if "side" in controller.command_3:
					command_3_value = controller.command_3.split("=")[1]
					command_3_value = command_3_value.replace(" ", "")
					
					if str(data["to_side"]) == str(command_3_value) or str(data["from_side"]) == str(command_3_value): 
						START_CONTROLLER_TASK(controller.task_3, controller.mqtt_device.name, controller.command_3)
						break		
						
				else:				
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
				# special case aqara cube
				if "side" in controller.command_4:
					command_4_value = controller.command_4.split("=")[1]
					command_4_value = command_4_value.replace(" ", "")
							
					if str(data["to_side"]) == str(command_4_value) or str(data["from_side"]) == str(command_4_value): 
						START_CONTROLLER_TASK(controller.task_4, controller.mqtt_device.name, controller.command_4)
						break		
						
				else:				
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
				# special case aqara cube
				if "side" in controller.command_5:
					command_5_value = controller.command_5.split("=")[1]
					command_5_value = command_5_value.replace(" ", "")					
					
					if str(data["to_side"]) == str(command_5_value) or str(data["from_side"]) == str(command_5_value): 
						START_CONTROLLER_TASK(controller.task_5, controller.mqtt_device.name, controller.command_5)
						break		
						
				else:				
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
				# special case aqara cube
				if "side" in controller.command_6:
					command_6_value = controller.command_6.split("=")[1]
					command_6_value = command_6_value.replace(" ", "")
					
					if str(data["to_side"]) == str(command_6_value) or str(data["from_side"]) == str(command_6_value): 
						START_CONTROLLER_TASK(controller.task_6, controller.mqtt_device.name, controller.command_6)
						break		
						
				else:				
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
				# special case aqara cube
				if "side" in controller.command_7:
					command_7_value = controller.command_7.split("=")[1]
					command_7_value = command_7_value.replace(" ", "")
					
					if str(data["to_side"]) == str(command_7_value) or str(data["from_side"]) == str(command_7_value): 
						START_CONTROLLER_TASK(controller.task_7, controller.mqtt_device.name, controller.command_7)
						break		
						
				else:				
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
				# special case aqara cube
				if "side" in controller.command_8:
					command_8_value = controller.command_8.split("=")[1]
					command_8_value = command_8_value.replace(" ", "")
					
					if str(data["to_side"]) == str(command_8_value) or str(data["from_side"]) == str(command_8_value): 
						START_CONTROLLER_TASK(controller.task_8, controller.mqtt_device.name, controller.command_8)
						break		
						
				else:				
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
				# special case aqara cube
				if "side" in controller.command_9:
					command_9_value = controller.command_9.split("=")[1]
					command_9_value = command_9_value.replace(" ", "")
					
					if str(data["to_side"]) == str(command_9_value) or str(data["from_side"]) == str(command_9_value): 
						START_CONTROLLER_TASK(controller.task_9, controller.mqtt_device.name, controller.command_9)
						break				
				
				else:
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

