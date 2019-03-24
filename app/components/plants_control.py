import threading
import time

from app import app
from app.database.database import *


""" ################ """
""" watering control """
""" ################ """

def START_PUMP(pump_id):
    # 40 ml / minute

    print("Start: " + str(pump_id))

  


def STOP_PUMP(pump_id):

    print("Stop: " + str(pump_id))
 
 


""" ############## """
""" sensor control """
""" ############## """

def CHECK_MOISTURE():
 
    print("Check moisture")

    for plant in GET_ALL_PLANTS():
        target_moisture  = plant.moisture_voltage
        
        current_moisture = ""

        # dry = 2.84V
        # water = 1.24V
        moisture = float(current_moisture) - float(target_moisture)

        # not enough water
        if moisture > 0.2:
            new_water_volume = int(plant.water_volume) + 20
        elif moisture > 0.1:
            new_water_volume = int(plant.water_volume) + 10

        # too much water
        elif moisture < -0.2:
            new_water_volume = int(plant.water_volume) - 20
        elif moisture < -0.1:
            new_water_volume = int(plant.water_volume) - 10
        else:
            pass

        if new_water_volume < 0:
            new_water_volume = 0

        try:
            # update database
            CHANGE_WATER_VOLUME(plant.id, str(new_water_volume)) 
        except:
            pass
  

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
                START_PUMP(plant.pump_id)
                pump_running = pump_running + 1

            while pump_running != 0:

                for plant in GET_ALL_PLANTS():
                    if i == plant.water_volume:
                        STOP_PUMP(plant.pump_id) 
                        pump_running = pump_running - 1 
                
                # 10 ml / 15 sec
                i = i + 10
                time.sleep(15)
                print(i) 

            print("alle Pumpen ausgeschaltet")

            #check moisture     
            time.sleep(600)
            CHECK_MOISTURE()     
            print("Sensoren überprüft")

    # start thread
    t1 = watering_Thread()
    t1.start()
