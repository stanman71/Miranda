import threading
import time

from app import app
from app.database.database import *
from app.components.mqtt import MQTT_PUBLISH
from app.components.file_management import WRITE_LOGFILE_SYSTEM
from app.components.mqtt import SET_MOISTURE_CURRENT, GET_MOISTURE_CURRENT


""" ################ """
""" watering control """
""" ################ """

# 40 ml / minute
def START_PUMP(mqtt_device_channel, pump_id):
    print("Start: " + str(pump_id))
    channel = "/SmartHome/" + mqtt_device_channel + "/pump/" + str(pump_id)
    MQTT_PUBLISH(channel, "on")
    time.sleep(1)
  

def STOP_PUMP(mqtt_device_channel, pump_id):
    print("Stop: " + str(pump_id))
    channel = "/SmartHome/" + mqtt_device_channel + "/pump/" + str(pump_id)
    MQTT_PUBLISH(channel, "off") 
    time.sleep(1)


def UPDATE_CURRENT_MOISTURE(plant):
    # send request message
    channel = "/SmartHome/" + plant.mqtt_device.channel_path + "/plant/" + str(plant.id)
    MQTT_PUBLISH(channel, str(plant.sensor_id))
    time.sleep(3) 


def CHECK_MOISTURE(plant):
    UPDATE_CURRENT_MOISTURE(plant)
    
    moisture_target  = plant.moisture_target
    moisture_current = GET_MOISTURE_CURRENT()
        
    # check current moisture inside value range
    # dry   = 870
    # water = 370  
 
    print("moisture_current: " + str(moisture_current))
       
    # repeat request message   
    if not 350 < moisture_current < 900:
        UPDATE_CURRENT_MOISTURE(plant)   
        moisture_current = GET_MOISTURE_CURRENT()
        
        print("moisture_current: " + str(moisture_current))   

    # abort process
    if not 350 < moisture_current < 900:
        SET_MOISTURE_CURRENT(0)
        WRITE_LOGFILE_SYSTEM("ERROR", "Watering >>> Plant >>> " + plant.name + " >>> Sensor " + str(plant.sensor_id))     
        
    # update watervolume
    if 350 < moisture_current < 900:
        
        moisture = moisture_current - moisture_target
        
        print(moisture)
    
        # not enough water
        if moisture > 30:
            new_watervolume = plant.watervolume + 40
            
            if moisture > 100:
                WRITE_LOGFILE_SYSTEM("WARNING", "Watering >>> Plant >>> " + plant.name + " >>> has not enough water") 
            
        elif moisture > 0:
            new_watervolume = plant.watervolume + 20

        # too much water
        elif moisture < -30:
            new_watervolume = plant.watervolume - 40
            if new_watervolume < 0:
                new_watervolume = 0              
           
            if moisture < -100:
                WRITE_LOGFILE_SYSTEM("WARNING", "Watering >>> Plant >>> " + plant.name + " >>> has too much water") 
            
        elif moisture < 0:
            new_watervolume = plant.watervolume - 20
            if new_watervolume < 0:
                new_watervolume = 0     
            
        else:
            WRITE_LOGFILE_SYSTEM("ERROR", "Watering >>> Plant >>> " + plant.name + " >>> Sensor " + str(plant.sensor_id))  

        # update database
        SET_PLANT_WATERVOLUME(plant.id, new_watervolume) 
    
        SET_MOISTURE_CURRENT(0)
        WRITE_LOGFILE_SYSTEM("EVENT", "Watering >>> Plant >>> " + plant.name + " >>> new Watervolume " + str(new_watervolume))


""" ######### """
""" threading """
""" ######### """

def START_WATERING_THREAD():
    class watering_Thread(threading.Thread):
        def __init__(self, ID = 1, name = "watering_Thread"):
            threading.Thread.__init__(self)
            self.ID = ID
            self.name = name

        def run(self):
            WRITE_LOGFILE_SYSTEM("EVENT", "Watering >>> Start Pumps") 
       
            i = 0
            pump_running = 0

            """

            for plant in GET_ALL_PLANTS():
                START_PUMP(plant.mqtt_device.channel_path, plant.pump_id)
                WRITE_LOGFILE_SYSTEM("EVENT", "Watering >>> Start Pump " + str(plant.pump_id))            
                pump_running = pump_running + 1

            while pump_running != 0:

                for plant in GET_ALL_PLANTS():
                    if i == plant.watervolume:
                        STOP_PUMP(plant.mqtt_device.channel_path, plant.pump_id) 
                        WRITE_LOGFILE_SYSTEM("EVENT", "Watering >>> Stop Pump " + str(plant.pump_id))                      
                        pump_running = pump_running - 1 
                
                # 10 ml / 15 sec
                i = i + 10
                time.sleep(15)
                print(i) 

            WRITE_LOGFILE_SYSTEM("EVENT", "Watering >>> Stopped all Pumps") 

            time.sleep(600) 

            """

            for plant in GET_ALL_PLANTS():          
                CHECK_MOISTURE(plant)    
             
            WRITE_LOGFILE_SYSTEM("EVENT", "Watering >>> finished") 

    # start thread
    t1 = watering_Thread()
    t1.start()
