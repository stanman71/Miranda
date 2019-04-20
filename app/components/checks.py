from app import app
from app.database.database import *
from app.components.mqtt import *


""" ############### """
""" check functions """
""" ############### """


def CHECK_PLANTS():
    string_errors = ""
    entries = Plants.query.all()
    for entry in entries:
        if ((entry.sensor_key == "None" or entry.sensor_key == None) or
            (entry.pump_key == "None" or entry.pump_key == None)):
            
            string_errors = string_errors + str(entry.name) + " "
     
    if string_errors != "":
        return ("Einstellungen unvollständig ( Pflanzen-Name: " + string_errors + ")")
    else:
        return ""


def CHECK_SENSORDATA_JOBS():
    string_errors = ""
    entries = Sensordata_Jobs.query.all()
    for entry in entries:
        if entry.sensor_key == "None" or entry.sensor_key == None:
            string_errors = string_errors + str(entry.id) + " "
            
    if string_errors != "":
        return ("Einstellungen unvollständig ( Job-ID: " + string_errors + ")")
    else:
        return ""


def CHECK_TASKS(tasks, task_type):
   list_errors = []

   for element in tasks:
      task = element.task
      name = element.name

      # check snowboy_active
      if task == "snowboy_active" and task_type == "snowboy":
         continue

      # check start_scene
      if "scene" in task:
         if ":" in task:
            task = task.split(":") 

            # check group setting
            try:
               if GET_LED_GROUP_BY_NAME(task[1]):
                  pass
               else:
                  list_errors.append(name + " >>> LED Gruppe nicht vorhanden >>> " + task[1])                     
            except:
               list_errors.append(name + " >>> fehlende Einstellung >>> LED Gruppe")        

            # check scene setting    
            try:
               if GET_LED_SCENE_BY_NAME(task[2]):
                  pass
               else:
                  list_errors.append(name + " >>> LED Szene nicht vorhanden >>> " + task[2])
            except:
               list_errors.append(name + " >>> fehlende Einstellung >>> LED Szene")

            # check global brightness    
            try:
               if task[3].isdigit():
                  if 1 <= int(task[3]) <= 100:
                     continue
                  else:
                     list_errors.append(name + " >>> ungültiger Wertebereich >>> Globale Helligkeit") 
                     continue             
               else:
                  list_errors.append(name + " >>> ungültige Einstellung >>> Globale Helligkeit")
                  continue 
            except:
               continue 

         else:
            list_errors.append(name + " >>> Ungültige Formatierung")
            continue

      # check start_program
      if "program" in task:
         if ":" in task:
            task = task.split(":") 

            # check group setting
            try:
               if GET_LED_GROUP_BY_NAME(task[1]):
                  pass
               else:
                  list_errors.append(name + " >>> LED Gruppe nicht vorhanden >>> " + task[1])                     
            except:
               list_errors.append(name + " >>> fehlende Einstellung >>> LED Gruppe")        

            # check program setting    
            try:
               if GET_LED_PROGRAM_BY_NAME(task[2]):
                  continue
               else:
                  list_errors.append(name + " >>> LED Programm nicht vorhanden >>> " + task[2])
                  continue
            except:
               list_errors.append(name + " >>> fehlende Einstellung >>> LED Programm")    
               continue  

         else:
            list_errors.append(name + " >>> Ungültige Formatierung")
            continue

      # check led_off
      if "led_off" in task:
         if ":" in task:
            task = task.split(":")

            # check group setting
            if task[1] == "group":
               try: 
                  if GET_LED_GROUP_BY_NAME(task[2]):
                     continue
                  else:
                     list_errors.append(name + " >>> LED Gruppe nicht vorhanden >>> " + task[2])
                     continue
               except:
                  list_errors.append(name + " >>> fehlende Einstellung >>> LED Gruppe")
                  continue                  

            # check turn off all leds
            try:
               if task[1] == "all": 
                  continue
            except:
               pass
            
            list_errors.append(name + " >>> Ungültige Eingabe >>> 'all' oder 'group'")
            continue     

         else:
            list_errors.append(name + " >>> Ungültige Formatierung")
            continue

      # check watering_plants
      if task == "watering_plants" and task_type == "timer":
         continue

      # check save_database         
      if task == "save_database" and task_type == "timer":
         continue

      # check mqtt_update_devices
      if task == "mqtt_update_devices" and task_type == "timer":
         continue

      # check request_sensordata
      if "request_sensordata" in task and (task_type == "timer" or task_type == "sensor"):
         if ":" in task:
            task = task.split(":")

            # check job-id setting
            try:          
               if GET_SENSORDATA_JOB_BY_ID(int(task[1])):
                  continue
               else:
                  list_errors.append(name + " >>> Job-ID nicht vorhanden >>> " + task[1])
                  continue      
            except:
               list_errors.append(name + " >>> fehlende Einstellung >>> Job-ID") 
               continue      

         else:
            list_errors.append(name + " >>> Ungültige Formatierung")
            continue 

      # nothing found
      list_errors.append(name + " >>> Ungültige Aufgabe") 

   if list_errors == []:
      return ""
   else:
      return list_errors


def CHECK_ALL_TIMER_SETTINGS(timer_tasks): 
   list_errors_settings = []  

   for task in timer_tasks:

      ### check day
      if "," in task.day:
            day = task.day.split(",")
            for element in day:
               if element not in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
                  list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Tag") 
                  break                                 
      else:
            if task.day not in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su", "*"] and task.day != "*":
               list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Tag") 

      ### check hour
      if "," in task.hour:
            hour = task.hour.split(",")
            for element in hour:
               try:                                   
                  if not (0 <= int(element) <= 24):
                        list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Stunde") 
                        break   
               except:
                  list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Stunde") 
                  break   
      else:
            try:
               if not (0 <= int(task.hour) <= 24) and task.hour != "*":
                        list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Stunde") 
            except:
               if task.hour != "*":
                  list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Stunde")    

      ### check minute
      if "," in task.minute:
            minute = task.minute.split(",")
            for element in minute:
               try:                                   
                  if not (0 <= int(element) <= 60):
                        list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Minute") 
                        break   
               except:
                  list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Minute") 
                  break   
      else:
            try:
               if not (0 <= int(task.minute) <= 60) and task.minute != "*":
                        list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Minute") 
            except:
               if task.minute != "*":
                  list_errors_settings.append(task.name + " >>> falsche Zeitangabe >>> Minute") 

   if list_errors_settings == []:
      error_message_settings = ""
   else:
      error_message_settings = list_errors_settings

   return error_message_settings


def CHECK_ALL_SENSOR_SETTINGS(sensor_tasks): 
   list_errors_settings = []  

   for task in sensor_tasks:

      # check mqtt devices
      if task.mqtt_device_id_1 == "None" or task.mqtt_device_id_1 == "" or task.mqtt_device_id_1 == None:
         list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> MQTT-Gerät 1") 

      if task.mqtt_device_id_2 == "None" or task.mqtt_device_id_2 == "" or task.mqtt_device_id_2 == None:
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> MQTT-Gerät 2") 

      if task.mqtt_device_id_3 == "None" or task.mqtt_device_id_3 == "" or task.mqtt_device_id_3 == None:
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.operator_main_2 != "None" and task.operator_main_2 != None:
               list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> MQTT-Gerät 3")             

      # check sensors
      if ((task.mqtt_device_id_1 != "None" or task.mqtt_device_id_1 != "") and 
          (task.sensor_key_1 == "None" or task.sensor_key_1 == "")):
         list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Sensor 1") 
         
      if ((task.mqtt_device_id_2 != "None" or task.mqtt_device_id_2 != "") and 
          (task.sensor_key_2 == "None" or task.sensor_key_2 == "" )):
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Sensor 2")  

      if ((task.mqtt_device_id_3 != "None" or task.mqtt_device_id_3 != "") and 
          (task.sensor_key_3 == "None" or task.sensor_key_3 == "" )):
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.operator_main_2 != "None" and task.operator_main_2 != None:
               list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Sensor 3")  

      # check operators
      if task.operator_1 == "None" or task.operator_1 == "" or task.operator_1 == None: 
         list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Operator 1") 
         
      if task.operator_2 == "None" or task.operator_2 == "" or task.operator_2 == None: 
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.operator_main_1 != "<" and task.operator_main_1 != ">" and task.operator_main_1 != "=":
               list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Operator 2")  

      if task.operator_3 == "None" or task.operator_3 == "" or task.operator_3 == None: 
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.operator_main_2 != "None" and task.operator_main_2 != None:
               if task.operator_main_2 != "<" and task.operator_main_2 != ">" and task.operator_main_2 != "=":
                  list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Operator 3")  

      # check values
      if ((task.operator_1 == "<" or task.operator_1 == ">" or task.operator_1 == "=" or task.operator_1 == "None" or task.operator_1 == None) and 
          (task.value_1 == "" or task.value_1 == "None" or task.value_1 == None)):
         list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Vergleichswert 1")         

      if ((task.operator_2 == "<" or task.operator_2 == ">" or task.operator_2 == "=" or task.operator_1 == "None" or task.operator_2 == None) and 
          (task.value_2 == "" or task.value_2 == "None" or task.value_2 == None)):
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.operator_main_1 != "<" and task.operator_main_1 != ">" and task.operator_main_1 != "=":
               list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Vergleichswert 2") 

      if ((task.operator_3 == "<" or task.operator_3 == ">" or task.operator_3 == "=" or task.operator_1 == "None" or task.operator_3 == None) and 
          (task.value_3 == "" or task.value_3 == "None" or task.value_3 == None)):
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.operator_main_2 != "None" and task.operator_main_2 != None:
               if task.operator_main_2 != "<" and task.operator_main_2 != ">" and task.operator_main_2 != "=":
                  list_errors_settings.append(task.name + " >>> fehlende Einstellung >>> Vergleichswert 3") 

   if list_errors_settings == []:
      error_message_settings = ""
   else:
      error_message_settings = list_errors_settings

   return error_message_settings


def CHECK_LED_GROUP_SETTINGS(settings):
   list_errors = []

   for element in settings:
      if element.led_id_1 == None or element.led_id_1 == "None":
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 1")        
      if element.active_led_2 == "on" and (element.led_id_2 == None or element.led_id_2 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 2") 
      if element.active_led_3 == "on" and (element.led_id_3 == None or element.led_id_3 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 3") 
      if element.active_led_4 == "on" and (element.led_id_4 == None or element.led_id_4 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 4") 
      if element.active_led_5 == "on" and (element.led_id_5 == None or element.led_id_5 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 5") 
      if element.active_led_6 == "on" and (element.led_id_6 == None or element.led_id_6 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 6") 
      if element.active_led_7 == "on" and (element.led_id_7 == None or element.led_id_7 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 7") 
      if element.active_led_8 == "on" and (element.led_id_8 == None or element.led_id_8 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 8") 
      if element.active_led_9 == "on" and (element.led_id_9 == None or element.led_id_9 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 9")                     

   if list_errors == []:
      return ""
   else:
      return list_errors