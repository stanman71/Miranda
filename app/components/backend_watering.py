import threading
import time
import json
import heapq

from app import app
from app.database.database import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM
from app.components.mqtt import CHECK_MQTT_SETTING, UPDATE_MQTT_DEVICES
from app.components.shared_resources import process_management_queue
from app.components.email import SEND_EMAIL


""" ############ """
""" pump control """
""" ############ """

def START_PUMP(plant_id):
    
    time.sleep(5)
    
    plant    = GET_PLANT_BY_ID(plant_id)
    ieeeAddr = plant.mqtt_device.ieeeAddr 
    
    channel  = "miranda/mqtt/" + ieeeAddr + "/set"
    
    if plant.pumptime != "auto":    
        msg = '{"pump":"ON","pump_time":' + str(plant.pumptime) + '}'
        
    else:
        msg = '{"pump":"ON","pump_time":' + str(plant.pumptime_auto) + '}'
    
    heapq.heappush(process_management_queue, (50, ("watering", channel, msg)))
    
    time.sleep(5)
    
    # check pump started first try
    if CHECK_MQTT_SETTING(ieeeAddr, msg, 10):
        WRITE_LOGFILE_SYSTEM("SUCCESS", "Watering | Plant - " + plant.name + " | Pump started")  
        return True

    time.sleep(5)

    # check pump started second try 
    if CHECK_MQTT_SETTING(ieeeAddr, msg, 10):
        WRITE_LOGFILE_SYSTEM("SUCCESS", "Watering | Plant - " + plant.name + " | Pump started")  
        return True
        
    WRITE_LOGFILE_SYSTEM("WARNING", "Watering | Plant - " + plant.name + " | Pump starting not confimed")   
    return False

        
        
""" ########### """
""" main thread """
""" ########### """

def START_WATERING_THREAD(group_number):

    try:
        Thread = threading.Thread(target=WATERING_THREAD, args=(group_number, ))
        Thread.start()  
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Thread | Start Watering | Group - " + group_number + " | " + str(e)) 
        SEND_EMAIL("ERROR", "Thread | Start Watering | Group - " + group_number + " | " + str(e)) 


def WATERING_THREAD(group_number):
    global pump_incoming_list    
  
    pump_running = 0
    warnings     = []       
  
    # get current sensor values
    UPDATE_MQTT_DEVICES("mqtt")
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
                
                if moisture_level == "much" and current_moisture < 350:
                    watering = True
                if moisture_level == "normal" and current_moisture < 250:
                    watering = True                
                if moisture_level == "less" and current_moisture < 150:
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
        if CHECK_MQTT_SETTING(plant.mqtt_device.ieeeAddr , '"pump":"OFF"', 15):  
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
    
    # wait 30 minutes
    time.sleep(1800)
     
    # get current sensor values
    UPDATE_MQTT_DEVICES("mqtt")
    time.sleep(30)
     
    # get moisture target and moisture current
    plant = GET_PLANT_BY_ID(plant_id)
    
    if plant.moisture_level == "much":
        moisture_target = 350
    if plant.moisture_level == "normal":
        moisture_target = 250               
    if plant.moisture_level == "less":
        moisture_target = 150   
        
    sensor_values      = plant.mqtt_device.last_values
    sensor_values_json = json.loads(sensor_values) 
    moisture_current   = sensor_values_json["sensor_moisture"]
    
    WRITE_LOGFILE_SYSTEM("SUCCESS", "Plant - " + plant.name + " | Moisture checked") 

    # more than 30 % lower
    if moisture_current < int(moisture_target * 0.7):
        SET_PLANT_PUMPTIME_AUTO(plant_id, int(plant.pumptime_auto * 1.3))
        return
    
    # 20 % - 30 % lower
    if moisture_current < int(moisture_target * 0.8):
        SET_PLANT_PUMPTIME_AUTO(plant_id, int(plant.pumptime_auto * 1.2))
        return
        
    # 10 % - 20 % lower    
    if moisture_current < int(moisture_target * 0.9):
        SET_PLANT_PUMPTIME_AUTO(plant_id, int(plant.pumptime_auto * 1.1))
        return
              
    # 10 % - 20% higher
    if moisture_current > int(moisture_target * 1.1):
        SET_PLANT_PUMPTIME_AUTO(plant_id, int(plant.pumptime_auto * 0.9))
        return
    
    # 20 % - 30 % higher
    if moisture_current > int(moisture_target * 1.2):
        SET_PLANT_PUMPTIME_AUTO(plant_id, int(plant.pumptime_auto * 0.8))
        return
        
    # more than 30 % higher    
    if moisture_current > int(moisture_target * 1.3):
        SET_PLANT_PUMPTIME_AUTO(plant_id, int(plant.pumptime_auto * 0.7))
        return
