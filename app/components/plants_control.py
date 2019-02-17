import time

from app import app
from app.database.database_operations import *
from app.components.sensors_control import *


""" ################ """
""" watering control """
""" ################ """

def START_PUMP(pump_id, seconds):

    try:

        import RPi.GPIO as GPIO

        GPIO.setmode(GPIO.BCM)

        if pump == 0:
           RELAIS_GPIO = 26
        if pump == 1:
           RELAIS_GPIO = 26
        if pump == 2:
           RELAIS_GPIO = 26
        if pump == 3:
           RELAIS_GPIO = 26

        GPIO.setup(RELAIS_GPIO, GPIO.OUT) 

        # 40 ml / minute
        # start
        GPIO.output(RELAIS_GPIO, GPIO.LOW) 

        time.sleep(seconds) 

        # stop
        GPIO.output(RELAIS_GPIO, GPIO.HIGH) 

    except:
        pass


def WATERING_PLANTS():

    plants_list = GET_ALL_PLANTS()

    # watering plants
    for plant in plants_list:
        START_PUMP(plant.pump_id, plant.water_volume)
    
    # wait 5 minutes  
    time.sleep(300) 

    # check moisture
    for plant in plants_list:
        target_moisture  = plant.moisture_voltage
        current_moisture = READ_SENSOR_GPIO(plant.sensor_name)

        # dry = 2.84V
        # water = 1.24V

        moisture = current_moisture - target_moisture

        # not enough water
        if moisture > 0.4:
            new_water_volume = plant.water_volume * 1.2
        elif moisture > 0.2:
            new_water_volume = plant.water_volume * 1.1

        # too much water
        elif moisture < -0.4:
            new_water_volume = plant.water_volume * 1.2   
        elif moisture < -0.2:
            new_water_volume = plant.water_volume * 1.1  
        else:
            pass

        try:
            # update database
            CHANGE_WATER_VOLUME(plant.id, new_water_volume) 
        except:
            pass