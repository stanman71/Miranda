import threading
import time
import json

from app import app
from app.database.database import *
from app.components.mqtt import MQTT_PUBLISH
from app.components.file_management import WRITE_LOGFILE_SYSTEM, READ_LOGFILE_MQTT


""" ################ """
""" watering control """
""" ################ """

# 40 ml / minute
def START_PUMP(plant_id):
    
    plant = GET_PLANT_BY_ID(plant_id)
    
    gateway  = plant.mqtt_device.gateway 
    ieeeAddr = plant.mqtt_device.ieeeAddr 
    pump_key = plant.pump_key
    pump_key = pump_key.replace(" ","")
    
    channel = "SmartHome/" + gateway + "/" + ieeeAddr + "/set"
    
    if pump_key == "pump_0":
        MQTT_PUBLISH(channel, "pump_0:on")
    if pump_key == "pump_1":
        MQTT_PUBLISH(channel, "pump_1:on")
    if pump_key == "pump_2": 
        MQTT_PUBLISH(channel, "pump_2:on")  
    if pump_key == "pump_3":
        MQTT_PUBLISH(channel, "pump_3:on")  
        
    print("Start: " + pump_key)
    WRITE_LOGFILE_SYSTEM("EVENT", "Watering | Start Pump - " + plant.pump_key)
        
    time.sleep(1)
  

def STOP_PUMP(plant_id):
    
    plant = GET_PLANT_BY_ID(plant_id)
    
    gateway  = plant.mqtt_device.gateway 
    ieeeAddr = plant.mqtt_device.ieeeAddr 
    pump_key = plant.pump_key 
    pump_key = pump_key.replace(" ","")  
    
    channel = "SmartHome/mqtt" + gateway + "/" + ieeeAddr + "/set"
    
    if pump_key == "pump_0":
        MQTT_PUBLISH(channel, "pump_0:off")
    if pump_key == "pump_1": 
        MQTT_PUBLISH(channel, "pump_1:off")
    if pump_key == "pump_2": 
        MQTT_PUBLISH(channel, "pump_2:off")  
    if pump_key == "pump_3":   
        MQTT_PUBLISH(channel, "pump_3:off")    
        
    print("Stop: " + pump_key)
    WRITE_LOGFILE_SYSTEM("EVENT", "Watering | Stop Pump - " + plant.pump_key)
    
    time.sleep(1)


""" ######### """
""" threading """
""" ######### """

def START_WATERING_THREAD():

    Thread = threading.Thread(target=WATERING_THREAD, args=("start",))
    Thread.start()   



def WATERING_THREAD(start):

    i = 0
    pump_running = 0

    for plant in GET_ALL_PLANTS():
        
        if plant.control_sensor == "checked":
        
            ieeeAddr   = plant.mqtt_device.ieeeAddr
            gateway    = plant.mqtt_device.gateway
            sensor_key = plant.sensor_key
            sensor_key = sensor_key.replace(" ","")
            
            # send request message
            channel = "SmartHome/" + gateway + "/" + ieeeAddr + "/get"
            MQTT_PUBLISH(channel, "")
            
            time.sleep(2)
            
            # get sensor value
            input_messages = READ_LOGFILE_MQTT(gateway, "SmartHome/" + gateway + "/" + ieeeAddr, 5)
            
            for input_message in input_messages:
               
                input_message = str(input_message[2])
                
                data  = json.loads(input_message)
                value = data[sensor_key]
                
                print("SENSOR: " + str(value))
               
                if int(value) < 50:                        
                    START_PUMP(plant.id)       
                    pump_running = pump_running + 1  
                    break   
                                         
                else:
                    WRITE_LOGFILE_SYSTEM("WARNING", "Watering | Plant - " + plant.name + " | Water on the Ground") 
                    break
       
        else:
            START_PUMP(plant.id)       
            pump_running = pump_running + 1

    while pump_running != 0:

        for plant in GET_ALL_PLANTS():
            if i == plant.pumptime:
                STOP_PUMP(plant.id)                 
                pump_running = pump_running - 1 
        
        # 10 ml / 15 sec
        i = i + 10
        time.sleep(15)
        print(i) 

    WRITE_LOGFILE_SYSTEM("SUCCESS", "Watering | finished") 
      
      
