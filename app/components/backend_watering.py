import threading
import time
import json
import heapq

from app import app
from app.database.database import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM
from app.components.mqtt import MQTT_CHECK_SETTING, MQTT_UPDATE_DEVICES
from app.components.shared_resources import process_management_queue
from app.components.email import SEND_EMAIL


""" ############ """
""" pump control """
""" ############ """

def START_PUMP(plant_id):
    
    time.sleep(5)
    
    plant    = GET_PLANT_BY_ID(plant_id)
    ieeeAddr = plant.mqtt_device.ieeeAddr 
    
    channel  = "SmartHome/mqtt/" + ieeeAddr + "/set"
    
    if plant.pumptime != "auto":    
        msg = '{"pump":"ON","pump_time":' + str(plant.pumptime) + '}'
        
    else:
        msg = '{"pump":"ON","pump_time":' + str(plant.pumptime_auto) + '}'
    
    heapq.heappush(process_management_queue, (50, ("watering", channel, msg)))
    
    time.sleep(5)
    
    # check pump started first try
    if MQTT_CHECK_SETTING(ieeeAddr, msg, 10):
        WRITE_LOGFILE_SYSTEM("SUCCESS", "Watering | Plant - " + plant.name + " | Pump started")  
        return True

    time.sleep(5)

    # check pump started second try 
    if MQTT_CHECK_SETTING(ieeeAddr, msg, 10):
        WRITE_LOGFILE_SYSTEM("SUCCESS", "Watering | Plant - " + plant.name + " | Pump started")  
        return True
        
    WRITE_LOGFILE_SYSTEM("WARNING", "Watering | Plant - " + plant.name + " | Pump starting not confimed")   
    return False

        
        
""" ########### """
""" main thread """
""" ########### """

def START_WATERING_THREAD(group_number):

	try:
		Thread = threading.Thread(target=WATERING_THREAD)
		Thread.start()  
		
	except Exception as e:
		WRITE_LOGFILE_SYSTEM("ERROR", "Thread | Start Watering | Group - " + group_number + " | " + str(e)) 
		SEND_EMAIL("ERROR", "Thread | Start Watering | Group - " + group_number + " | " + str(e)) 


def WATERING_THREAD(group_number):
    global pump_incoming_list    
  
    pump_running = 0
    warnings     = []       
  
    # get current sensor values
    MQTT_UPDATE_DEVICES("mqtt")
    time.sleep(30)
      
  
    # ##############
    # starting pumps
    # ##############
    
    # search plant
    for plant in GET_ALL_PLANTS():
        
        # valid group ?
        valid_group = False
        
        if group_number.isdigit():
            if plant.group == int(group_number):
                
                valid_group = True
        
        if group_number == "all" or group_number == "ALL":
            valid_group = True
               
        
        # valid group founded
        if valid_group == True:
            
            watering = False
        
            # check watertank sensor
            if plant.control_sensor_watertank == "checked":
                
                sensor_values      = plant.mqtt_device.last_values
                sensor_values_json = json.loads(sensor_values)              
                current_watertank  = sensor_values_json["sensor_watertank"] 
                
                if current_watertank == 0:
                    WRITE_LOGFILE_SYSTEM("WARNING", "Watering | Plant - " + plant.name + " | Watertank Low")                    
                    warnings.append("Watertank Low")    
         
     
            # check moisture sensor
            if plant.control_sensor_moisture == "checked":          
                
                moisture_level     = plant.moisture_level            
                sensor_values      = plant.mqtt_device.last_values
                sensor_values_json = json.loads(sensor_values) 
                current_moisture   = sensor_values_json["sensor_moisture"] 
                
                # 300 moisture low
                # 700 moisture high
                
                if moisture_level == "much" and current_moisture < 550:
                    watering = True
                if moisture_level == "normal" and current_moisture < 450:
                    watering = True                
                if moisture_level == "less" and current_moisture < 300:
                    watering = True     
                        
            else:
                watering = True
                    
                    
            # start watering
            if watering == True:
                
                WRITE_LOGFILE_SYSTEM("EVENT", "Watering | Plant - " + plant.name + " | Starting") 
                
                if START_PUMP(plant.id) != True:  
                    warnings.append("Pump starting not confimed")
                      
                pump_running = pump_running + 1
                
                
            # start control moisture for pumptime_auto
            if plant.pumptime == "auto":

                try:
                    Thread = threading.Thread(target=PUMPTIME_AUTO_UPDATE_TREAD, args=(plant.id, ))
                    Thread.start()      
                    
                except Exception as e:
                    WRITE_LOGFILE_SYSTEM("ERROR", "Thread | Pumptime auto update | Plant - " +  plant.name + " | " + str(e)) 
                    warnings.append("Thread | Pumptime auto update | " + str(e)) 


    # ####################
    # check pumps stopping
    # ####################

    seconds = 0
                    
    # check watering process
    while pump_running != 0 or seconds == 180:
        
        time.sleep(10)
    
        # check pump stopped ?
        if MQTT_CHECK_SETTING(plant.mqtt_device.ieeeAddr , '"pump":"OFF"', 15):  
            WRITE_LOGFILE_SYSTEM("SUCCESS", "Watering | Plant - " + plant.name + " | Pump stopped")                              
            pump_running = False

        seconds = seconds + 10
                      
                             
    # pump stopping not confirmed
    if pump_running > 0:
        
        WRITE_LOGFILE_SYSTEM("WARNING", "Watering | Plant - " + plant.name + " | Pump stopping not confimed")         
        warnings.append("Pump stopping not confimed")


    if warnings != []:
        WRITE_LOGFILE_SYSTEM("WARNING", "Watering | Plant - " + plant.name + " | Finished with Warning | " + str(warnings))
        SEND_EMAIL("WARNING", "Watering | Plant - " + plant.name + " | Finished with Warning | " + str(warnings))                      
    else:
        WRITE_LOGFILE_SYSTEM("SUCCESS", "Watering | Plant - " + plant.name + " | Finished")    

                                          
""" ############################ """
""" pumptime auto control thread """
""" ############################ """

def PUMPTIME_AUTO_UPDATE_TREAD(plant_id):
    
    # wait 1 hour
    time.sleep(3600)
    
    
    # get current sensor values
    MQTT_UPDATE_DEVICES("mqtt")
    time.sleep(30)
    
    
    # get moisture target and moisture current
    plant = GET_PLANT_BY_ID(plant_id)
    
    if plant.moisture_level == "much":
        moisture_target = 600
    if plant.moisture_level == "normal":
        moisture_target = 500               
    if plant.moisture_level == "less":
        moisture_target = 350   
        
    sensor_values      = plant.mqtt_device.last_values
    sensor_values_json = json.loads(sensor_values) 
    moisture_current   = sensor_values_json["sensor_moisture"] 
    
    
    # compare moisture values and set new pumptime_auto value
    pumptime_auto_current = plant.pumptime_auto


    # 30 % lower
    if moisture_current < int(moisture_target * 0.7):
        SET_PLANT_PUMPTIME_AUTO(plant_id, int(pumptime_auto_current * 1.3))    
    
    # 20 % - 30 % lower
    if moisture_current < int(moisture_target * 0.8):
        SET_PLANT_PUMPTIME_AUTO(plant_id, int(pumptime_auto_current * 1.2))
        
    # 10 % - 20 % lower    
    if moisture_current < int(moisture_target * 0.9):
        SET_PLANT_PUMPTIME_AUTO(plant_id, int(pumptime_auto_current * 1.1))        
        
        
    # 10 % - 20% higher
    if moisture_current > int(moisture_target * 1.1):
        SET_PLANT_PUMPTIME_AUTO(plant_id, int(pumptime_auto_current * 0.9))    
    
    # 20 % - 30 % higher
    if moisture_current > int(moisture_target * 1.2):
        SET_PLANT_PUMPTIME_AUTO(plant_id, int(pumptime_auto_current * 0.8))
        
    # 30 % higher    
    if moisture_current > int(moisture_target * 1.3):
        SET_PLANT_PUMPTIME_AUTO(plant_id, int(pumptime_auto_current * 0.7))            
        
        
        
    
