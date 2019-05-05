import paho.mqtt.client as mqtt
import datetime
import time
import json

from app import app
from app.database.database import *
from app.components.file_management import *


""" #################### """
""" mqtt publish message """
""" #################### """

BROKER_ADDRESS = GET_CONFIG_MQTT_BROKER()

def MQTT_PUBLISH(MQTT_TOPIC, MQTT_MSG):


    def on_publish(client, userdata, mid):
        print ('Message Published...')

    client = mqtt.Client()
    client.on_publish = on_publish
    client.connect(BROKER_ADDRESS) 
    client.publish(MQTT_TOPIC,MQTT_MSG)
    client.disconnect()

    return ""


""" ################### """
"""    update devices   """
""" ################### """

def MQTT_UPDATE_DEVICES(gateway):
   
   if gateway == "mqtt":
      
      MQTT_PUBLISH("SmartHome/mqtt/devices", "")  
      time.sleep(2)

      try:
         messages = READ_LOGFILE_MQTT("mqtt", "SmartHome/mqtt/log",30)

         if messages != "Message nicht gefunden" and messages != "Keine Verbindung zu MQTT":

            for message in messages:
               
               message = str(message[2])

               data = json.loads(message)
               
               inputs_temp = str(data['inputs'])
               inputs_temp = inputs_temp[1:]
               inputs_temp = inputs_temp[:-1]
               inputs_temp = inputs_temp.replace("'", "")
               inputs_temp = inputs_temp.replace('"', "")

               outputs_temp = str(data['outputs'])
               outputs_temp = outputs_temp[1:]
               outputs_temp = outputs_temp[:-1]
               outputs_temp = outputs_temp.replace("'", "")
               outputs_temp = outputs_temp.replace('"', "")  

               name     = data['ieeeAddr']
               gateway  = "mqtt"
               ieeeAddr = data['ieeeAddr']
               model    = data['model']
               inputs   = inputs_temp
               outputs  = outputs_temp

               ADD_MQTT_DEVICE(name, gateway, ieeeAddr, model, inputs, outputs)
               
            return ""

         else: 
	         return messages

      except Exception as e:
         if str(e) == "string index out of range":
            WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | No connection")    


   if gateway == "zigbee2mqtt":

      MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/devices", "")  
       
      for i in range (0,5):

         try:
            messages = READ_LOGFILE_MQTT("zigbee2mqtt", "SmartHome/zigbee2mqtt/bridge/log",30)
            
            if messages != "Message nicht gefunden" and messages != "Keine Verbindung zu ZigBee2MQTT":
                for message in messages:
		  		  
                    message = str(message[2])
                    message = message.replace("'","")

                    data = json.loads(message)
                  
                    if (data['type']) == "devices":
                        for device in (data['message']):

                           # add new device
                           if not GET_MQTT_DEVICE_BY_IEEEADDR(device['ieeeAddr']):
                              name     = device['friendly_name']
                              gateway  = "zigbee2mqtt"              
                              ieeeAddr = device['ieeeAddr']
                              model    = device['model']
			      
                              ADD_MQTT_DEVICE(name, gateway, ieeeAddr, model)

                           # get device informations
                           else:
                              gateway  = "zigbee2mqtt"
                              id       = GET_MQTT_DEVICE_BY_IEEEADDR(device['ieeeAddr']).id	      
                              name     = device['friendly_name']
                              inputs   = GET_MQTT_DEVICE_BY_IEEEADDR(device['ieeeAddr']).inputs	
			      	      	      
                              SET_MQTT_DEVICE(gateway, id, name, inputs)

         except Exception as e:
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | " + str(e))            


""" ################### """
"""    get sensordata   """
""" ################### """


def MQTT_REQUEST_SENSORDATA(job_id):
   sensordata_job  = GET_SENSORDATA_JOB_BY_ID(job_id)
   device_gateway  = sensordata_job.mqtt_device.gateway
   device_ieeeAddr = sensordata_job.mqtt_device.ieeeAddr  
   sensor_key = sensordata_job.sensor_key
   sensor_key = sensor_key.replace(" ", "")
 
   channel = "SmartHome/" + device_gateway + "/" + device_ieeeAddr + "/get"
   MQTT_PUBLISH(channel, "")  

   time.sleep(2)

   input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr, 30)

   if input_messages != "Message nicht gefunden":
      
      for input_message in input_messages:
         input_message = str(input_message[2])
         
         data = json.loads(input_message)

      filename = sensordata_job.filename

      WRITE_SENSORDATA_FILE(filename, device_ieeeAddr, sensor_key, data[sensor_key])

      return ""

   return "Message nicht gefunden"
   
   
def MQTT_SAVE_SENSORDATA(job_id):
   sensordata_job  = GET_SENSORDATA_JOB_BY_ID(job_id)
   device_gateway  = sensordata_job.mqtt_device.gateway
   device_ieeeAddr = sensordata_job.mqtt_device.ieeeAddr  
   sensor_key = sensordata_job.sensor_key
   sensor_key = sensor_key.replace(" ", "")

   input_messages = READ_LOGFILE_MQTT(device_gateway, "SmartHome/" + device_gateway + "/" + device_ieeeAddr, 30)

   for input_message in input_messages:
      input_message = str(input_message[2])
      
      data = json.loads(input_message)

   filename = sensordata_job.filename

   WRITE_SENSORDATA_FILE(filename, device_ieeeAddr, sensor_key, data[sensor_key])
   
   
   
""" ################### """
"""     stop outputs    """
""" ################### """
   
   
def MQTT_STOP_ALL_OUTPUTS():
   devices = GET_ALL_MQTT_DEVICES("mqtt")
   
   for device in devices:

      if device.outputs != "" or device.outputs != None or device.outputs != "None":
         outputs = device.outputs
         outputs = outputs.replace(" ","")
         outputs = outputs.split(",")
	 
         for output in outputs:
            
            channel = "SmartHome/" + device.gateway + "/" + device.ieeeAddr + "/set"
            msg = output + ":off"

            MQTT_PUBLISH(channel, msg)
            
            time.sleep(1)
