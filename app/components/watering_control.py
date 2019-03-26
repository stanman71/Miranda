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


""" ############## """
""" sensor control """
""" ############## """

def CHECK_MOISTURE():

    for plant in GET_ALL_PLANTS():   

        time.sleep(5)     
        # send request message
        channel = "/SmartHome/" + plant.mqtt_device.channel_path + "/plant/" + str(plant.id)
        MQTT_PUBLISH(channel, str(plant.sensor_id))

        target_moisture  = plant.moisture_voltage_target 
        current_moisture = plant.moisture_voltage_current
      
        # dry   = 2.80V
        # water = 1.20V  
   
        if current_moisture < 1.2:
            print("sensor_error")
            
        else:
            moisture = float(current_moisture) - float(target_moisture)

            # not enough water
            if moisture > 0.2:
                new_watervolume = int(plant.watervolume) + 20
            elif moisture > 0.1:
                new_watervolume = int(plant.watervolume) + 10

            # too much water
            elif moisture < -0.2:
                new_watervolume = int(plant.watervolume) - 20
            elif moisture < -0.1:
                new_watervolume = int(plant.watervolume) - 10
            else:
                pass

            if new_watervolume < 0:
                new_watervolume = 0

            # update database
            SET_PLANT_WATERVOLUME(plant.id, str(new_watervolume)) 

  
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