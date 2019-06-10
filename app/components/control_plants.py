import threading
import time
import json
import heapq

from app import app
from app.database.database import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM, READ_LOGFILE_MQTT
from app.components.mqtt import MQTT_PUBLISH, MQTT_SET_DEVICE_SETTING, MQTT_CHECK_SETTING
from app.components.shared_resources import process_management_queue


""" ################ """
""" watering control """
""" ################ """

def START_PUMP(plant_id):
    
    plant    = GET_PLANT_BY_ID(plant_id)
    ieeeAddr = plant.mqtt_device.ieeeAddr 
    
    heapq.heappush(process_management_queue, (5, ("device", ieeeAddr, 
                                                  "PUMP_ON", '{"state": "PUMP_ON", "pumptime":' + str(plant.pumptime) + '}', 
                                                  "state", "PUMP_ON")))	
    
    time.sleep(2)
    
    # check pump started ?
    if MQTT_CHECK_SETTING(ieeeAddr, "state", "PUMP_ON"):
        WRITE_LOGFILE_SYSTEM("EVENT", "Watering | Plant - " + plant.name + " | Pump started") 
    

""" ######### """
""" threading """
""" ######### """

def START_WATERING_THREAD():

    Thread = threading.Thread(target=WATERING_THREAD, args=("start",))
    Thread.start()   


def WATERING_THREAD(start):

    i = 0
    pump_running = 0
    warnings = False
    
    WRITE_LOGFILE_SYSTEM("EVENT", "Watering | started") 

    for plant in GET_ALL_PLANTS():
        
        watering = False
        
        # check moisture sensor
        if plant.control_sensor_moisture == "checked":          
            
            moisture_level     = plant.moisture            
            
            sensor_values      = plant.mqtt_device.last_values
            sensor_values_json = json.loads(sensor_values) 
            current_moisture   = sensor_values_json["sensor_moisture"] 
            
            # 300 moisture low
            # 700 moisture high
            
            if moisture_level == "much" and current_moisture < 600:
                watering = True
            if moisture_level == "normal" and current_moisture < 450:
                watering = True                
            if moisture_level == "less" and current_moisture < 300:
                watering = True     
                
        else:
            watering = True
            
        # check watertank sensor
        if plant.control_sensor_watertank == "checked":
            
            sensor_values      = plant.mqtt_device.last_values
            sensor_values_json = json.loads(sensor_values)              
            current_watertank  = sensor_values_json["sensor_watertank"] 
            
            if current_watertank == 0:
                WRITE_LOGFILE_SYSTEM("WARNING", "Watering | Plant - " + plant.name + " | Watertank Low") 
                warnings = True

        # start watering
        if watering:
            START_PUMP(plant.id)       
            pump_running = pump_running + 1
            
    
    # overview watering process
    while pump_running != 0:
        
        for plant in GET_ALL_PLANTS():
            if i == plant.pumptime:
                
                # check pump stopped ?
                if MQTT_CHECK_SETTING(plant.mqtt_device.ieeeAddr , "state", "PUMP_OFF"):  
                    WRITE_LOGFILE_SYSTEM("EVENT", "Watering | Plant - " + plant.name + " | Pump stopped")                              
                    pump_running = pump_running - 1 
                
                else:
                    time.sleep(1)
                    
                    if MQTT_CHECK_SETTING(plant.mqtt_device.ieeeAddr , "state", "PUMP_OFF"): 
                        WRITE_LOGFILE_SYSTEM("EVENT", "Watering | Plant - " + plant.name + " | Pump stopped")  
                        pump_running = pump_running - 1    
                        
                    else:
                        WRITE_LOGFILE_SYSTEM("WARNING", "Watering | Plant - " + plant.name + " | Pump stopping not confimed") 
                        warnings = True
                        pump_running = pump_running - 1 
        
        i = i + 15
        time.sleep(15)
        

    if warnings == True:
        WRITE_LOGFILE_SYSTEM("WARNING", "Watering | finished with Warning")  
    else:
        WRITE_LOGFILE_SYSTEM("SUCCESS", "Watering | finished")    
      
      
