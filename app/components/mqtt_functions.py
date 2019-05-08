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
         messages = READ_LOGFILE_MQTT("mqtt", "SmartHome/mqtt/log",10)

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

               name        = data['ieeeAddr']
               gateway     = "mqtt"
               ieeeAddr    = data['ieeeAddr']
               model       = data['model']
               
               try:
                  device_type = data['device_type']
               except:
                  device_type = ""                 
                  
               try:
                  description = data['description']
               except:
                  description = ""

               try:
                  inputs = inputs_temp
               except:
                  inputs = ""
                  
               try:
                  outputs = outputs_temp
               except:
                  outputs = ""
                  
               # add new device
               if not GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr):
                  ADD_MQTT_DEVICE(name, gateway, ieeeAddr, model, device_type, description, inputs, outputs)
                  
               # update existing device
               else:
                  id   = GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr).id
                  name = GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr).name
                                
                  UPDATE_MQTT_DEVICE(id, name, gateway, device_type, description, inputs, outputs)
                  SET_MQTT_DEVICE_LAST_CONTACT(ieeeAddr)

            return ""

         else: 
	         return messages

      except Exception as e:
         if str(e) == "string index out of range":
            WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | No connection") 
            return ("Error: " + str(e))   


   if gateway == "zigbee2mqtt":

      error = ""

      MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/devices", "")  
      time.sleep(2)
      
      try:
         messages = READ_LOGFILE_MQTT("zigbee2mqtt", "SmartHome/zigbee2mqtt/bridge/log",10)
         
         if messages != "Message nicht gefunden" and messages != "Keine Verbindung zu ZigBee2MQTT":
             for message in messages:
           
                 message = str(message[2])
                 message = message.replace("'","")

                 data = json.loads(message)
                 
                 if (data['type']) == "devices":
                     devices = (data['message'])
                     
                     for i in range(0, len(devices)):
                        
                        device = devices[i]
                        
                        # add new device
                        
                        if not GET_MQTT_DEVICE_BY_IEEEADDR(device['ieeeAddr']):
                           
                           name         = device['friendly_name']
                           gateway      = "zigbee2mqtt"              
                           ieeeAddr     = device['ieeeAddr']
                           device_model = device['model']

                           device_type = GET_MQTT_DEVICE_INFORMATIONS(model)[0]
                           description = GET_MQTT_DEVICE_INFORMATIONS(model)[1]
                           inputs      = GET_MQTT_DEVICE_INFORMATIONS(model)[2]
                           outputs     = GET_MQTT_DEVICE_INFORMATIONS(model)[3]     
                           
                           ADD_MQTT_DEVICE(name, gateway, ieeeAddr, device_model, device_type, description, inputs, outputs)

                        # update device informations
                        
                        else:
                           
                           device_data = GET_MQTT_DEVICE_BY_IEEEADDR(device['ieeeAddr'])
                           
                           print(device_data)
                           
                           id       = device_data.id	      
                           name     = device['friendly_name']
                           gateway  = "zigbee2mqtt"
                           model    = device_data.model
                           
                           try:
                              device_type = GET_MQTT_DEVICE_INFORMATIONS(model)[0]
                              description = GET_MQTT_DEVICE_INFORMATIONS(model)[1]
                              inputs      = GET_MQTT_DEVICE_INFORMATIONS(model)[2]
                              outputs     = GET_MQTT_DEVICE_INFORMATIONS(model)[3]     
                           except:
                              device_type = device_data.device_type
                              description = device_data.description 
                              inputs      = device_data.inputs
                              outputs     = device_data.outputs	
                              
                              error = "Error: File zigbee_device_informations.yaml not founded"
                                                                     
                           UPDATE_MQTT_DEVICE(id, name, gateway, device_type, description, inputs, outputs)
                           SET_MQTT_DEVICE_LAST_CONTACT(device['ieeeAddr'])
                           
                     if error != "":
                        return error
                     else:
                        return ""
      
      except Exception as e:
         WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | " + str(e))  
         return ("Error: " + str(e))
      

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
       
            
            
""" ################### """
"""      set switch     """
""" ################### """
   
   
def MQTT_SET_SWITCH(name, gateway, ieeeAddr, setting):
   
   if setting == "checked":
      msg = '{"state": "ON"}'
      setting = "ON"
      
   else:
      msg = '{"state": "OFF"}'
      setting = "OFF"
      
   channel = "SmartHome/" + gateway + "/" + ieeeAddr + "/set"

   MQTT_PUBLISH(channel, msg)   
   
   time.sleep(2)
   
   # start check function
   if gateway == "mqtt":
      check_setting = MQTT_CHECK_SETTING(gateway, ieeeAddr, "state", setting)
   else:
      check_setting = MQTT_CHECK_SETTING(gateway, name, "state", setting)
   
   
   if check_setting:
      return ""
   else:
      return ("Fehler, Einstellung konnte nicht bestätigt werden >>> " + name)
   

   
""" ################### """
"""  mqtt check setting """
""" ################### """
 
def MQTT_CHECK_SETTING(gateway, Addr, key, setting):
                  
   input_messages = READ_LOGFILE_MQTT(gateway, "SmartHome/" + gateway + "/" + Addr, 5)
   
   if input_messages != "Message nicht gefunden":
      for input_message in input_messages:
         input_message = str(input_message[2])

         data = json.loads(input_message)
         
         if data[key] == setting:
            return True
     
   return False
   

