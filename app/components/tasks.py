from app import app
from app.components.control_led import *
from app.database.database import *
from app.components.control_watering import START_WATERING_THREAD
from app.components.mqtt import *
from app.components.file_management import SAVE_DATABASE, WRITE_LOGFILE_SYSTEM, GET_CONFIG_MQTT_BROKER, GET_LOCATION_COORDINATES
from app.components.process_program import START_PROGRAM_THREAD, STOP_PROGRAM_THREAD, GET_PROGRAM_RUNNING
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL

from difflib import SequenceMatcher


""" ################################ """
""" ################################ """
"""         controller tasks         """
""" ################################ """
""" ################################ """


def START_CONTROLLER_TASK(task, controller_name, controller_command):

    # ###########
    # start scene
    # ###########

	if "scene" in task:

		task = task.split(" /// ")
		group = GET_LED_GROUP_BY_NAME(task[1])
		scene = GET_LED_SCENE_BY_NAME(task[2])

		# group existing ?
		if group != None:

			# scene existing ?
			if scene != None:

				try:
					brightness = int(task[3])
				except:
					brightness = 100

				# new led setting ?
				if group.current_setting != scene.name or int(group.current_brightness) != brightness:
					LED_SET_SCENE(group.id, scene.id, brightness)
					LED_GROUP_CHECK_SETTING_THREAD(group.id, scene.id, scene.name, brightness, 2, 10)

				else:
					WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name +
										 " | " + scene.name + " : " + str(brightness))

			else:
				WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " +
									 controller_command + " | Scene - " + task[2] + " | not founded")

		else:
			WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " +
								 controller_command + " | Group - " + task[1] + " | not founded")

    # #################
    # change brightness
    # #################

	if "brightness" in task:
		task = task.split(" /// ")
		group = GET_LED_GROUP_BY_NAME(task[1])
		command = task[2]

		# group existing ?
		if group != None:

			# command valid ?
			if command == "turn_up" or command == "TURN_UP" or command == "turn_down" or command == "TURN_DOWN":
				scene_name = group.current_setting

				# led_group off ?
				if scene_name != "OFF":
					scene = GET_LED_SCENE_BY_NAME(scene_name)

					# get new brightness_value
					current_brightness = group.current_brightness

					if (command == "turn_up" or command == "TURN_UP") and current_brightness != 100:
						target_brightness = int(current_brightness) + 20

						if target_brightness > 100:
							target_brightness = 100

						LED_SET_BRIGHTNESS_DIMMER(group.id, "turn_up")
						LED_GROUP_CHECK_SETTING_THREAD(group.id, scene.id, scene_name, target_brightness, 2, 10)

					elif (command == "turn_down" or command == "TURN_DOWN") and current_brightness != 0:

						target_brightness = int(current_brightness) - 20

						if target_brightness < 0:
							target_brightness = 0

						LED_SET_BRIGHTNESS_DIMMER(group.id, "turn_down")
						LED_GROUP_CHECK_SETTING_THREAD(group.id, scene.id, scene_name, target_brightness, 2, 10)

					else:
						WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name +
						                     " | " + scene_name + " : " + str(current_brightness) + " %")

				else:
					WRITE_LOGFILE_SYSTEM("WARNING", "LED | Group - " +
					                     group.name + " | OFF : 0 %")

			else:
				WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " +
				                     controller_command + " | Command - " + task[2] + " | not valid")

		else:
			WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " +
			                     controller_command + " | Group - " + task[1] + " | not founded")

    # #######
    # led off
    # #######

	if "led_off" in task:
		task = task.split(" /// ")

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
					scene = GET_LED_SCENE_BY_NAME(scene_name)

					LED_TURN_OFF_GROUP(group.id)
					LED_GROUP_CHECK_SETTING_THREAD(group.id, scene.id, "OFF", 0, 2, 10)

				else:
					WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %")

			# group not founded
			if group_founded == False:
				WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " +
				                     controller_command + " | Group - " + input_group_name + " | not founded")

		if task[1] == "all" or task[1] == "ALL":
			for group in GET_ALL_LED_GROUPS():

				# new led setting ?
				if group.current_setting != "OFF":
					scene_name = group.current_setting
					scene      = GET_LED_SCENE_BY_NAME(scene_name)

					LED_TURN_OFF_GROUP(group.id)
					LED_GROUP_CHECK_SETTING_THREAD(group.id, scene.id, "OFF", 0, 2, 10)

			else:
				WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %")

    # ######
    # device
    # ######

	if "device" in task:
		task = task.split(" /// ")
		device = GET_MQTT_DEVICE_BY_NAME(task[1].lower())

		# device founded ?
		if device != None:
			
			controller_setting = task[2:]
			controller_setting = controller_setting.replace(" ", "")
			
			# new device setting ?
			if controller_setting != device.previous_setting:
					
				if "|" in controller_setting:
					controller_setting = controller_setting.replace("|", ",")
							
				# mqtt
				if device.gateway == "mqtt":
					
					channel  = "SmartHome/mqtt/" + device.ieeeAddr + "/set"                  
					msg      = controller_setting

					MQTT_PUBLISH(channel, msg)  
					
					MQTT_CHECK_SETTING_THREAD(device.ieeeAddr, controller_setting, 5, 20)


				# zigbee2mqtt
				if device.gateway == "zigbee2mqtt":
					
					channel  = "SmartHome/zigbee2mqtt/" + device.name + "/set"                  
					msg      = controller_setting

					MQTT_PUBLISH(channel, msg)  
					
					ZIGBEE2MQTT_CHECK_SETTING_THREAD(device.name, controller_setting, 5, 20)                                    
                                
		
			else:

				if device.gateway == "mqtt":
					WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + device.name + " | " + setting_value)

				if device.gateway == "zigbee2mqtt":
					WRITE_LOGFILE_SYSTEM("STATUS", "Zigbee2MQTT | Device - " + device.name + " | " + setting_value)

		else:
			WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | Gerät - " + task[1] + " | not founded")


    # ########
    # programs
    # ########

	if "program" in task:
		task = task.split(" /// ")
		program = GET_PROGRAM_BY_NAME(task[1].lower())

		if program != None:
			program_running = GET_PROGRAM_RUNNING()

			if task[2] == "start" and program_running == None:
				START_PROGRAM_THREAD(program.id)
				
			elif task[2] == "start" and program_running != None:
				WRITE_LOGFILE_SYSTEM("WARNING", "Controller - " + controller_name + " | Command - " + controller_command + " | Other Program running")
									 
			elif task[2] == "stop":
				STOP_PROGRAM_THREAD()
				
			else:
				WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | Command not valid")

		else:
			WRITE_LOGFILE_SYSTEM("ERROR", "Controller - " + controller_name + " | Command - " + controller_command + " | Program not founded")


""" ################################ """
""" ################################ """
"""           scheduler tasks        """
""" ################################ """
""" ################################ """


def START_SCHEDULER_TASK(task_object):

	# ###########
	# start scene
	# ###########

	try:
		if "scene" in task_object.task:

			task = task_object.task.split(" /// ")
			group = GET_LED_GROUP_BY_NAME(task[1])
			scene = GET_LED_SCENE_BY_NAME(task[2])

			# group existing ?
			if group != None:

				# scene existing ?
				if scene != None:

					try:
						brightness = int(task[3])
					except:
						brightness = 100

					# new led setting ?
					if group.current_setting != scene.name or int(group.current_brightness) != brightness:
						
						WRITE_LOGFILE_SYSTEM("EVENT", 'Scheduler | Task - ' + task_object.name + ' | started')						
						
						LED_SET_SCENE(group.id, scene.id, brightness)
						LED_GROUP_CHECK_SETTING_THREAD(group.id, scene.id, scene.name, brightness, 2, 10)


				else:
					WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Scene - " + task[2] + " | not founded")

			else:
				WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Group - " + task[1] + " | not founded")

	except Exception as e:
		print(e)
		WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))


    # #######
    # led off
    # #######

	try:
		if "led_off" in task_object.task:
			task = task_object.task.split(" /// ")

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
								
								WRITE_LOGFILE_SYSTEM("EVENT", 'Scheduler | Task - ' + task_object.name + ' | started')								
								
								LED_TURN_OFF_GROUP(group.id)
								LED_GROUP_CHECK_SETTING_THREAD(group.id, 0, "OFF", 0, 5, 20)   


					if group_founded == False:
						WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Group - " + input_group_name + " | not founded")     


			if task[1] == "all" or task[1] == "ALL":

				for group in GET_ALL_LED_GROUPS():

					# new led setting ?
					if group.current_setting != "OFF":
						scene_name = group.current_setting
						scene      = GET_LED_SCENE_BY_NAME(scene_name)

						WRITE_LOGFILE_SYSTEM("EVENT", 'Scheduler | Task - ' + task_object.name + ' | started')

						LED_TURN_OFF_GROUP(group.id)
						LED_GROUP_CHECK_SETTING_THREAD(group.id, scene.id, "OFF", 0, 5, 20)    
						   

	except Exception as e:
		print(e)
		WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


	# ######
	# device
	# ######

	try:
		if "device" in task_object.task and "mqtt_update" not in task_object.task:
			task = task_object.task.split(" /// ")

			device = GET_MQTT_DEVICE_BY_NAME(task[1].lower())

			# device founded ?
			if device != None:
				scheduler_setting = task[2]
				scheduler_setting = scheduler_setting.replace(" ", "")

				# new device setting ?
				if scheduler_setting != device.previous_setting:
					
					WRITE_LOGFILE_SYSTEM("EVENT", 'Scheduler | Task - ' + task_object.name + ' | started')								
												
					if "|" in scheduler_setting:
						scheduler_setting = scheduler_setting.replace("|", ",")
								
					# mqtt
					if device.gateway == "mqtt":
						
						channel  = "SmartHome/mqtt/" + device.ieeeAddr + "/set"                  
						msg      = scheduler_setting

						MQTT_PUBLISH(channel, msg)  
						
						MQTT_CHECK_SETTING_THREAD(device.ieeeAddr, scheduler_setting, 5, 20)


					# zigbee2mqtt
					if device.gateway == "zigbee2mqtt":
						
						channel  = "SmartHome/zigbee2mqtt/" + device.name + "/set"                  
						msg      = scheduler_setting

						MQTT_PUBLISH(channel, msg)  
						
						ZIGBEE2MQTT_CHECK_SETTING_THREAD(device.name, scheduler_setting, 5, 20)            


			else:
				WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Device - " + task[1] + " | not founded")                  


	except Exception as e:
		print(e)
		WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))     


	# ########
	# programs
	# ########

	try:
		if "program" in task_object.task:
			task    = task_object.task.split(" /// ")
			program = GET_PROGRAM_BY_NAME(task[1].lower())

			if program != None:
				program_running = GET_PROGRAM_RUNNING() 

				if task[2] == "start" and program_running == None:
					START_PROGRAM_THREAD(program.id)
					
				elif task[2] == "start" and program_running != None:
					WRITE_LOGFILE_SYSTEM("WARNING", "Scheduler | Task - " + task_object.name + " | Other Program running")	
					
				elif task[2] == "stop":
					STOP_PROGRAM_THREAD() 
					
				else:
					WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Command not valid")

			else:
				WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | Program not founded")		     

	except Exception as e:
		print(e)
		WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


	# ###############
	# watering plants
	# ###############

	try:
		if "watering_plants" in task_object.task:
			task = task_object.task.split(" /// ")
			group = task[1]
			START_WATERING_THREAD(group)

	except Exception as e:
		print(e)
		WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


	# #############
	# save database 
	# #############

	try:  
		if "save_database" in task_object.task:
			SAVE_DATABASE()	

	except Exception as e:
		print(e)
		WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))     


	# ###################
	# update mqtt devices
	# ###################

	try:
		if "mqtt_update_devices" in task_object.task:
			MQTT_UPDATE_DEVICES("mqtt")

	except Exception as e:
		print(e)
		WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))      


	# ##################
	# request sensordata
	# ##################

	try:
		if "request_sensordata" in task_object.task:
			task = task_object.task.split(":")
			MQTT_REQUEST_SENSORDATA(task[1])  

	except Exception as e:
		print(e)
		WRITE_LOGFILE_SYSTEM("ERROR", "Scheduler | Task - " + task_object.name + " | " + str(e))              


	# ####################################
	# remove scheduler task without repeat
	# ####################################

	if task_object.option_repeat != "checked":
		DELETE_SCHEDULER_TASK(task_object.id)



""" ################################ """
""" ################################ """
"""        speechcontrol tasks       """
""" ################################ """
""" ################################ """


def START_SPEECHCONTROL_TASK(answer):

	print(answer)

	# exception
	if ("could not understand audio" in answer) or ("Could not request results" in answer):
		WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | " + answer)

	else:
		WRITE_LOGFILE_SYSTEM("EVENT", 'Speechcontrol | Detection Task | ' + answer)

		SPEECHCONTROL_LED_TASK(answer)
		SPEECHCONTROL_DEVICE_TASK(answer)



# #########
# LED Tasks
# #########

def SPEECHCONTROL_LED_TASK(answer):

	table_numbers = {'zehn'   : 10, 
					 'zwanzig': 20,
					 'dreizig': 30,
				 	 'vierzig': 40,
					 'fünfzig': 50,
					 'sechzig': 60,
				 	 'siebzig': 70,
				 	 'achtzig': 80,
					 'neunzig': 90,
				  	 'hundert': 100                            
					 }

	answer_words = answer.split()
	ratio_value  = float(float(GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_sensitivity)/100)
	
	# ###########
	# start scene 
	# ###########

	keywords = GET_SPEECHCONTROL_LED_TASK_BY_ID(1).keywords

	try:
		list_keywords = keywords.split(",")
	except:
		list_keywords = [keywords]

	for keyword in list_keywords:
		keyword = keyword.replace(" ", "")

		for word in answer_words:
			
			# keyword founded ?
			if SequenceMatcher(None, keyword.lower(), word.lower()).ratio() > ratio_value:

				try:
					groups = GET_ALL_LED_GROUPS()
					scenes = GET_ALL_LED_SCENES() 

					group_id   = None
					scene_id   = None
					brightness = 100

					# search group
					for group in groups:
						for word in answer_words:

							if SequenceMatcher(None, group.name.lower(), word.lower()).ratio() > ratio_value:
								group_id = group.id
								continue

					# search scene
					for scene in scenes:
						for word in answer_words:
							
							if SequenceMatcher(None, scene.name.lower(), word.lower()).ratio() > ratio_value:
								scene_id = scene.id
								continue

					# search brightness value
					for element in answer.split():
						element = element.replace("%","")

						# check brightness as 'number' value
						if element.isdigit() and (1 <= int(element) <= 100):
							brightness = int(element)
							continue

						# check brightness as 'word' value
						try:
							brightness = int(table_numbers[element])
							continue
						except:
							pass  
		

					# group founded ?
					if group_id != None: 

						# scene founded ?
						if scene_id != None:   
							group = GET_LED_GROUP_BY_ID(group_id)
							scene = GET_LED_SCENE_BY_ID(scene_id) 

							# new led setting ?
							if group.current_setting != scene.name or int(group.current_brightness) != brightness:
								LED_SET_SCENE(group.id, scene.id, brightness)
								LED_GROUP_CHECK_SETTING_THREAD(group.id, scene.id, scene.name, brightness, 3, 15)     
								time.sleep(1)
								break								 

							else:
								WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | " + scene.name + " : " + str(brightness) + " %")     
								break

						else:
							WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | Scene not founded")
							break

					else:
						WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | Group not founded")
						break


				except Exception as e:
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | " + str(e))  
					break


	# ##############
	# set brightness
	# ##############

	keywords = GET_SPEECHCONTROL_LED_TASK_BY_ID(2).keywords

	try:
		list_keywords = keywords.split(",")
	except:
		list_keywords = [keywords]

	for keyword in list_keywords:
		keyword = keyword.replace(" ", "")

		for word in answer_words:
			
			# keyword founded ?
			if SequenceMatcher(None, keyword.lower(), word.lower()).ratio() > ratio_value:

				try:		
					groups = GET_ALL_LED_GROUPS()

					group_id   = None
					brightness = None

					# search group
					for group in groups:
						for word in answer_words:

							if SequenceMatcher(None, group.name.lower(), word.lower()).ratio() > ratio_value:
								group_id = group.id
								continue

					# search brightness value
					for element in answer.split():
						element = element.replace("%","")

						# check brightness as 'number' value
						if element.isdigit() and (1 <= int(element) <= 100):
							brightness = int(element)
							continue

						# check brightness as 'word' value
						try:
							brightness = int(table_numbers[element])
							continue
						except:
							pass  					
					
					# group founded ?
					if group_id != None: 

						# brightness value founded ?
						if brightness != None:

							# led_group off ?
							if group.current_setting != "OFF":
								scene_name = group.current_setting
								scene      = GET_LED_SCENE_BY_NAME(scene_name)                            

								# new led brightness setting ?
								if group.current_brightness != brightness:
									LED_SET_BRIGHTNESS(group.id, brightness)
									LED_GROUP_CHECK_SETTING_THREAD(group.id, scene.id, scene_name, brightness, 3, 15)  
									time.sleep(1)
									break									     

								else:
									WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | " + scene_name + " : " + str(brightness) + " %") 
									break	

							else:
								WRITE_LOGFILE_SYSTEM("WARNING", "LED | Group - " + group.name + " | OFF : 0 %") 
								break	                                   

						else:
							WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | Brightness value not founded")
							break
							
					else:
						WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | Group not founded")
						break

				except Exception as e:
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | " + str(e))    
					break


	# ##################
	# turn off led group
	# ##################

	keywords = GET_SPEECHCONTROL_LED_TASK_BY_ID(3).keywords

	try:
		list_keywords = keywords.split(",")
	except:
		list_keywords = [keywords]

	for keyword in list_keywords:
		keyword = keyword.replace(" ", "")

		for word in answer_words:
			
			# keyword founded ?
			if SequenceMatcher(None, keyword.lower(), word.lower()).ratio() > ratio_value:

				try:
					groups = GET_ALL_LED_GROUPS()
					
					founded_groups = []

					# search group
					for group in groups:
						for word in answer_words:

							if SequenceMatcher(None, group.name.lower(), word.lower()).ratio() > ratio_value:
								founded_groups.append(group)        


					# group founded
					if founded_groups != []:

						for group in founded_groups:
							scene_name = group.current_setting
							scene      = GET_LED_SCENE_BY_NAME(scene_name)

							# new led setting ?
							if group.current_setting != "OFF":
								LED_TURN_OFF_GROUP(group.id)
								LED_GROUP_CHECK_SETTING_THREAD(group.id, scene.id, "OFF", 0, 3, 15)  
								time.sleep(1)
								break    								     

							else:
								WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %") 	
								break                       

					else:
						WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | No Group founded")
						break                        


				except Exception as e:
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | " + str(e))    
					break


	# #################
	# turn off all leds
	# #################

	keywords = GET_SPEECHCONTROL_LED_TASK_BY_ID(4).keywords

	try:
		list_keywords = keywords.split(",")
	except:
		list_keywords = [keywords]

	for keyword in list_keywords:
		keyword = keyword.replace(" ", "")

		for word in answer_words:
			
			# keyword founded ?
			if SequenceMatcher(None, keyword.lower(), word.lower()).ratio() > ratio_value:

				try:
					# check all led groups
					for group in GET_ALL_LED_GROUPS():
						scene_name = group.current_setting
						scene      = GET_LED_SCENE_BY_NAME(scene_name)

						# new led setting ?
						if group.current_setting != "OFF":
							LED_TURN_OFF_GROUP(group.id)
							LED_GROUP_CHECK_SETTING_THREAD(group.id, scene.id, "OFF", 0, 3, 15)   
							time.sleep(1)
							break							    

						else:
							WRITE_LOGFILE_SYSTEM("STATUS", "LED | Group - " + group.name + " | OFF : 0 %") 
							break

				except Exception as e:
					print(e)
					WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | LED Task | " + answer + " | " + str(e))    
					break


# ############
# Device Tasks
# ############                   

def SPEECHCONTROL_DEVICE_TASK(answer):

	answer_words = answer.split()
	ratio_value  = float(GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_sensitivity/100)


	for task in GET_ALL_SPEECHCONTROL_DEVICE_TASKS():

		try:
			list_keywords = task.keywords.split(",")
		except:
			list_keywords = [keywords]

		for keyword in list_keywords:
			keyword = keyword.replace(" ", "")

			for word in answer_words:
				
				# keyword founded ?
				if SequenceMatcher(None, keyword.lower(), word.lower()).ratio() > ratio_value:
					
					try:
						device = GET_MQTT_DEVICE_BY_IEEEADDR(task.mqtt_device_ieeeAddr)

						# device founded ?
						if device != None:
							speechcontrol_setting = task.command
							speechcontrol_setting = speechcontrol_setting.replace(" ", "")		

							# new device setting ?
							if speechcontrol_setting != device.previous_setting:
								
								
								if "|" in speechcontrol_setting:
									speechcontrol_setting = speechcontrol_setting.replace("|", ",")
									
		
								# mqtt
								if device.gateway == "mqtt":
									
									channel  = "SmartHome/mqtt/" + device.ieeeAddr + "/set"                  
									msg      = speechcontrol_setting

									MQTT_PUBLISH(channel, msg)  
									
									MQTT_CHECK_SETTING_THREAD(device.ieeeAddr, speechcontrol_setting, 5, 20)
									
									
								# zigbee2mqtt
								if device.gateway == "zigbee2mqtt":
									
									channel  = "SmartHome/zigbee2mqtt/" + device.name + "/set"                  
									msg      = speechcontrol_setting

									MQTT_PUBLISH(channel, msg)  
									
									ZIGBEE2MQTT_CHECK_SETTING_THREAD(device.name, speechcontrol_setting, 5, 20)            


								time.sleep(1)
								break
						
						
							else:

								if device.gateway == "mqtt":
									WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + device.name + " | " + setting) 

								if device.gateway == "zigbee2mqtt":
									WRITE_LOGFILE_SYSTEM("STATUS", "Zigbee2MQTT | Device - " + device.name + " | " + setting)  


						else:
							WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Device Task | " + answer + " | Device not founded")
							break                             


					except Exception as e:
						print(e)
						WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Device Task | " + answer + " | " + str(e))      
						break                    



# #############
# Program Tasks
# #############                   

def SPEECHCONTROL_PROGRAM_TASK(answer):

	answer_words = answer.split()
	ratio_value  = float(GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_sensitivity/100)
	

	for task in GET_ALL_SPEECHCONTROL_PROGRAM_TASKS():

		try:
			list_keywords = task.keywords.split(",")
		except:
			list_keywords = [keywords]

		for keyword in list_keywords:
			keyword = keyword.replace(" ", "")

			for word in answer_words:
				
				# keyword founded ?
				if SequenceMatcher(None, keyword.lower(), word.lower()).ratio() > ratio_value:

					try:
						program = GET_PROGRAM_BY_ID(task.program_id)

						# program founded ?
						if program != None:
							command = task.command.lower()
							command = command.replace(" ", "")

							program_running = GET_PROGRAM_RUNNING() 

							if command == "start" and program_running == None:
								START_PROGRAM_THREAD(program.id)
								break
							elif command == "start" and program_running != None:
								WRITE_LOGFILE_SYSTEM("WARNING", "Speechcontrol | Program Task | " + answer + " | Other Program running")	
								break				
							elif command == "stop":
								STOP_PROGRAM_THREAD() 
								break
							else:
								WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Program Task | " + answer + " | Command not valid")
								break

						else:
							WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Program Task | " + answer + " | Program not founded")	
							break	     

					except Exception as e:
						print(e)
						WRITE_LOGFILE_SYSTEM("ERROR", "Speechcontrol | Program Task | " + answer + " | " + str(e))   
						break 

