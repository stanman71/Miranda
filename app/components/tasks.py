from app import app
from app.components.led_control import *
from app.database.database import *
from app.components.pixel_ring import PIXEL_RING_CONTROL
from app.components.mqtt import MQTT_PUBLISH
from app.components.watering_control import START_WATERING_THREAD
from app.components.file_management import SAVE_DATABASE, WRITE_LOGFILE_SYSTEM, READ_LOGFILE_MQTT

import datetime
import json

from threading import Thread


""" #### """
""" mqtt """
""" #### """


def CHECK_MQTT():
   MQTT_PUBLISH("SmartHome/mqtt/devices", "") 


def UPDATE_MQTT_DEVICES():
   MQTT_PUBLISH("SmartHome/mqtt/devices", "")  
   time.sleep(2)

   try:
      messages = READ_LOGFILE_MQTT("mqtt", "SmartHome/mqtt/log")

      if messages != "Message nicht gefunden" and messages != "Keine Verbindung zu MQTT":
         for message in messages:

            message = str(message[2])

            data = json.loads(message)

            name     = data['ieeeAddr']
            ieeeAddr = data['ieeeAddr']
            gateway  = "mqtt"
            model    = data['model']
            inputs   = data['input']
            outputs  = data['output']

            ADD_MQTT_DEVICE(name, ieeeAddr, gateway, model, inputs, outputs)    
   except:
      pass


def GET_MQTT_SENSORDATA(job_id):
   sensordata_job  = GET_SENSORDATA_JOB(job_id)
   device_gateway  = sensordata_job.mqtt_device.gateway
   device_ieeeAddr = sensordata_job.mqtt_device.ieeeAddr  
   sensor_id = sensordata_job.sensor_id
 
   channel = "SmartHome/" + device_gateway + "/" + device_ieeeAddr + "/get"
   MQTT_PUBLISH(channel, "")  

   time.sleep(2)

   input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr)

   for input_message in input_messages:
      input_message = str(input_message[2])
      
      print(input_message)
      
      #data = json.loads(input_message)
      #print(data["inputs"][0])



""" ####### """
""" snowboy """
""" ####### """

snowboy_detect_on = False

def SNOWBOY_TASKS(entry):
   
   global snowboy_detect_on
   
   WRITE_LOGFILE_SYSTEM("EVENT", 'Snowboy >>> Detection >>> ' + str(entry.task))
   
   # activate command mode
   if "snowboy_active" in entry.task:
      snowboy_detect_on = True
      PIXEL_RING_CONTROL("on")

      # set snowboy_detect_on to False after 1 second
      class waiter(Thread):
         def run(self):
            global detect
            time.sleep(1)
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")
      waiter().start()
  
   # start scene
   if "start_scene" in entry.task and snowboy_detect_on == True:
      task = entry.task.split(":")
      try:
            LED_SET_SCENE(int(task[1]), int(task[2]))
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")
      except:
            LED_SET_SCENE(int(task[1]))
            snowboy_detect_on = False
            PIXEL_RING_CONTROL("off")

   # start program
   if "start_program" in entry.task and snowboy_detect_on == True:
      task = entry.task.split(":")
      START_PROGRAM(int(task[1]))
      snowboy_detect_on = False
      PIXEL_RING_CONTROL("off")

   # turn off leds
   if "led_off" in entry.task and snowboy_detect_on == True:
      task = entry.task.split(":")
      LED_OFF(int(task[1]))   
      snowboy_detect_on = False 
      PIXEL_RING_CONTROL("off")


""" ######### """
""" schedular """
""" ######### """

def TASKMANAGEMENT_TIME_TASKS(entries):

   now    = datetime.datetime.now()
   day    = now.strftime('%a')
   hour   = now.strftime('%H')
   minute = now.strftime('%M')

   for entry in entries:
      if entry.day == day or entry.day == "*":
         if entry.hour == hour or entry.hour == "*":
            if entry.minute == minute or entry.minute == "*":
               print(entry.name)

               WRITE_LOGFILE_SYSTEM("EVENT", 'Task >>> ' + entry.name + ' >>> started') 

               # start scene
               if "start_scene" in entry.task:
                  task = entry.task.split(":")
                  try:
                        LED_SET_SCENE(int(task[1]), int(task[2]))
                  except:
                        LED_SET_SCENE(int(task[1]))

               # start program
               if "start_program" in entry.task:
                  task = entry.task.split(":")
                  START_PROGRAM(int(task[1]))

               # turn off leds
               if "led_off" in entry.task:
                  task = entry.task.split(":")
                  LED_OFF(int(task[1])) 

               # watering plants
               if "watering_plants" in entry.task:
                  START_WATERING_THREAD()

               # save database
               if "save_database" in entry.task:
                  SAVE_DATABASE()

               # update mqtt devices
               if "update_mqtt_devices" in entry.task:
                  UPDATE_MQTT_DEVICES()

               # get mqtt sensor data
               if "get_mqtt_sensordata" in entry.task:
                  task = entry.task.split(":")
                  GET_MQTT_SENSORDATA(int(task[1])) 

               # remove schedular task without repeat
               if entry.repeat == "":
                  DELETE_TASKMANAGEMENT_TIME_TASK(entry.id)
