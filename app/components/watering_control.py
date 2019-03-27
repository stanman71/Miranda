import threading
import time

from app import app
from app.database.database import *
from app.components.mqtt import MQTT_PUBLISH


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


def CHECK_MOISTURE():
    for plant in GET_ALL_PLANTS():   
        # send request message
        channel = "/SmartHome/" + plant.mqtt_device.channel_path + "/plant/" + str(plant.id)
        MQTT_PUBLISH(channel, str(plant.sensor_id))

        time.sleep(10)

        moisture_target  = plant.moisture_target 
        moisture_current = plant.moisture_current

        # check current moisture inside value range
        # dry   = 870
        # water = 370  
             
        if not 350 < moisture_current < 900:
            # repeat request message
            channel = "/SmartHome/" + plant.mqtt_device.channel_path + "/plant/" + str(plant.id)
            MQTT_PUBLISH(channel, str(plant.sensor_id))

            time.sleep(10)    

            moisture_current = plant.moisture_current

            # abort process, error message
            if not 350 < moisture_current < 900:
                RESET_PLANT_MOISTURE_CURRENT(plant.id)
                return "sensor_error"         
            
        else:
            moisture = moisture_current - moisture_target

            # not enough water
            if moisture > 50:
                new_watervolume = plant.watervolume + 40
                
                if moisture > 100:
                    print ("Fehler")
                
            elif moisture > 25:
                new_watervolume = plant.watervolume + 20

            # too much water
            elif moisture < -50:
                new_watervolume = plant.watervolume - 40
                
                if moisture < -100:
                    print ("Fehler")
                
            elif moisture < -25:
                new_watervolume = plant.watervolume - 20
                
            else:
                return "sensor_error" 

            if new_watervolume < 0:
                new_watervolume = 0

            # update database
            SET_PLANT_WATERVOLUME(plant.id, new_watervolume) 
            RESET_PLANT_MOISTURE_CURRENT(plant.id)

  
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
            print("Start Pumpen")
       
            i = 0
            pump_running = 0

            for plant in GET_ALL_PLANTS():
                START_PUMP(plant.mqtt_device.channel_path, plant.pump_id)
                pump_running = pump_running + 1

            while pump_running != 0:

                for plant in GET_ALL_PLANTS():
                    if i == plant.watervolume:
                        STOP_PUMP(plant.mqtt_device.channel_path, plant.pump_id) 
                        pump_running = pump_running - 1 
                
                # 10 ml / 15 sec
                i = i + 10
                time.sleep(15)
                print(i) 

            print("alle Pumpen ausgeschaltet")

            time.sleep(600)          
            CHECK_MOISTURE()     
            print("Sensoren überprüft")

    # start thread
    t1 = watering_Thread()
    t1.start()
