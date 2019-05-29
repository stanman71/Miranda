import paho.mqtt.client as mqtt
import json
import threading

from app import app
from app.components.control_led import *
from app.database.database import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM, GET_CONFIG_MQTT_BROKER


""" #################### """
""" mqtt publish message """
""" #################### """

BROKER_ADDRESS = GET_CONFIG_MQTT_BROKER()

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
      pass
    
      
      
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

				try:
					if str(data[command_1_key]) == str(command_1_value):
						START_CONTROLLER_TASK(controller.task_1, controller.mqtt_device.name, controller.command_1)
						break
				except:
					pass
			except:
				pass
				
			#command_2
			try:
				command_2_key   = controller.command_2.split("=")[0]
				command_2_key   = command_2_key.replace(" ", "")
				command_2_value = controller.command_2.split("=")[1]
				command_2_value = command_2_value.replace(" ", "")

				try:
					if str(data[command_2_key]) == str(command_2_value):
						START_CONTROLLER_TASK(controller.task_2, controller.mqtt_device.name, controller.command_2)
						break
				except:
					pass
			except:
				pass
	
			#command_3
			try:
				command_3_key   = controller.command_3.split("=")[0]
				command_3_key   = command_3_key.replace(" ", "")
				command_3_value = controller.command_3.split("=")[1]
				command_3_value = command_3_value.replace(" ", "")

				try:
					if str(data[command_3_key]) == str(command_3_value):
						START_CONTROLLER_TASK(controller.task_3, controller.mqtt_device.name, controller.command_3)
						break
				except:
					pass
			except:
				pass
	
			#command_4
			try:
				command_4_key   = controller.command_4.split("=")[0]
				command_4_key   = command_4_key.replace(" ", "")
				command_4_value = controller.command_4.split("=")[1]
				command_4_value = command_4_value.replace(" ", "")

				try:
					if str(data[command_4_key]) == str(command_4_value):
						START_CONTROLLER_TASK(controller.task_4, controller.mqtt_device.name, controller.command_4)
						break
				except:
					pass
			except:
				pass
				
			#command_5
			try:
				command_5_key   = controller.command_5.split("=")[0]
				command_5_key   = command_5_key.replace(" ", "")
				command_5_value = controller.command_5.split("=")[1]
				command_5_value = command_5_value.replace(" ", "")

				try:
					if str(data[command_5_key]) == str(command_5_value):
						START_CONTROLLER_TASK(controller.task_5, controller.mqtt_device.name, controller.command_5)
						break
				except:
					pass
			except:
				pass
	
			#command_6
			try:
				command_6_key   = controller.command_6.split("=")[0]
				command_6_key   = command_6_key.replace(" ", "")
				command_6_value = controller.command_6.split("=")[1]
				command_6_value = command_6_value.replace(" ", "")
				
				try:
					if str(data[command_6_key]) == str(command_6_value):
						START_CONTROLLER_TASK(controller.task_6, controller.mqtt_device.name, controller.command_6)
						break
				except:
					pass
			except:
				pass

			#command_7
			try:	
				command_7_key   = controller.command_7.split("=")[0]
				command_7_key   = command_7_key.replace(" ", "")
				command_7_value = controller.command_7.split("=")[1]
				command_7_value = command_7_value.replace(" ", "")

				try:
					if str(data[command_7_key]) == str(command_7_value):
						START_CONTROLLER_TASK(controller.task_7, controller.mqtt_device.name, controller.command_7)
						break
				except:
					pass
			except:
				pass
				
			#command_8
			try:
				command_8_key   = controller.command_8.split("=")[0]
				command_8_key   = command_8_key.replace(" ", "")
				command_8_value = controller.command_8.split("=")[1]
				command_8_value = command_8_value.replace(" ", "")

				try:
					if str(data[command_8_key]) == str(command_8_value):
						START_CONTROLLER_TASK(controller.task_8, controller.mqtt_device.name, controller.command_8)
						break
				except:
					pass
			except:
				pass
	
			#command_9
			try:
				command_9_key   = controller.command_9.split("=")[0]
				command_9_key   = command_9_key.replace(" ", "")
				command_9_value = controller.command_9.split("=")[1]
				command_9_value = command_9_value.replace(" ", "")

				try:
					if str(data[command_9_key]) == str(command_9_value):
						START_CONTROLLER_TASK(controller.task_9, controller.mqtt_device.name, controller.command_9)
						break
				except:
					pass
			except:
				pass
	

""" ################ """
"""  scheduler tasks """
""" ################ """


def START_CONTROLLER_TASK(task, controller_name, controller_command):
   
   # start scene
   try:
      if "scene" in task:
         try:
            task = task.split(":")
            group_id = GET_LED_GROUP_BY_NAME(task[1]).id
            scene_id = GET_LED_SCENE_BY_NAME(task[2]).id      
            error_message = LED_START_SCENE(int(group_id), int(scene_id), int(task[3]))  
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]
               WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | " + str(error_message))
               
         except:
            task = task.split(":")
            group_id = GET_LED_GROUP_BY_NAME(task[1]).id
            scene_id = GET_LED_SCENE_BY_NAME(task[2]).id          
            error_message = LED_START_SCENE(int(group_id), int(scene_id))   
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]                    
               WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | " + str(error_message))
                  
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | " + str(e))      


   # start program
   try:
      if "program" in task:
         task = task.split(":")
         group_id = GET_LED_GROUP_BY_NAME(task[1]).id
         program_id = GET_LED_PROGRAM_BY_NAME(task[2]).id
         error_message = LED_START_PROGRAM_THREAD(int(group_id), int(program_id))  
         
         if error_message != "":
            error_message = str(error_message)
            error_message = error_message[1:]
            error_message = error_message[:-1]                    
            WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | " + str(error_message))
            
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | " + str(e))      


   # change brightness
   try:
      if "brightness" in task:
         task = task.split(":")
         group_id = GET_LED_GROUP_BY_NAME(task[1]).id
         command  = task[2]
         error_message = LED_SET_BRIGHTNESS_DIMMER(int(group_id), command)  
         
         if error_message != "":
            error_message = str(error_message)
            error_message = error_message[1:]
            error_message = error_message[:-1]                    
            WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | " + str(error_message))
            
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | " + str(e))      


   # led off
   try:
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
                  
                     print("#######")
                     print(input_group_name.lower())
                                         
                     group_id = group.id
                     error_message = LED_TURN_OFF_GROUP(int(group_id))
               
                     if error_message != "":
                        error_message = str(error_message)
                        error_message = error_message[1:]
                        error_message = error_message[:-1]                    
                        WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | " + str(error_message))
                        
                     group_founded = True
               
               if group_founded == False:
                  WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | Group - " + input_group_name + " | not founded")
                        
               
         if task[1] == "all":
            error_message = LED_TURN_OFF_ALL()   
            
            if error_message != "":
               error_message = str(error_message)
               error_message = error_message[1:]
               error_message = error_message[:-1]                    
               WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | " + str(error_message))
          
	       
   except Exception as e:
      print(e)
      WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | " + str(e))      

