from flask import request
from flask_sqlalchemy import SQLAlchemy
import time

from app import app


""" ################# """
""" database settings """
""" ################# """

# connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smarthome.sqlite3'
db = SQLAlchemy(app)

# define table structure
class Plants(db.Model):
    __tablename__ = 'plants'
    id           = db.Column(db.Integer, primary_key=True, autoincrement = True)   
    name         = db.Column(db.String(50), unique=True)
    sensor_id    = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    sensor_name  = db.relationship('Sensor')
    moisture     = db.Column(db.Integer)    
    water_volume = db.Column(db.Integer)
    pump_id      = db.Column(db.Integer)

class Sensor(db.Model):
    __tablename__ = 'sensor'
    id   = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name = db.Column(db.String(50), unique=True)


""" ################# """
""" watering database """
""" ################# """

def GET_ALL_PLANTS():
    return Plants.query.all()


def ADD_PLANT(name, sensor_id, pump_id):

    # name exist ?
    check_entry = Plants.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,25):
            if Plants.query.filter_by(id=i).first():
                pass
            else:
                # add the new plant
                plant = Plants(
                        id           = i,
                        name         = name,
                        sensor_id    = sensor_id,
                        pump_id      = pump_id,
                        moisture     = 0,
                        water_volume = 0,
                    )
                db.session.add(plant)
                db.session.commit()
                return ""
    else:
        return "Name schon vergeben"


def CHANGE_MOISTURE(plant_id, moisture):    
    entry = Plants.query.filter_by(id=plant_id).first()
    entry.moisture = moisture
    db.session.commit()  


def CHANGE_WATER_VOLUME(plant_id, water_volume):        
    entry = Plants.query.filter_by(id=plant_id).first()
    entry.water_volume = water_volume
    db.session.commit()    


def DELETE_PLANT(plant_id):
    Plants.query.filter_by(id=plant_id).delete()
    db.session.commit()


""" ################ """
""" watering control """
""" ################ """

def START_PUMP(pump, seconds):

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

        # start
        GPIO.output(RELAIS_GPIO, GPIO.LOW) 

        time.sleep(seconds) 

        # stop
        GPIO.output(RELAIS_GPIO, GPIO.HIGH) 

    except:
        pass


def WATERING_PLANTS():

    plants_list = Plants.query.all()

    # watering plants
    for plant in plants_list:
        START_PUMP(plant.pump, plant.water_volume)
    
    # wait 5 minutes  
    time.sleep(300) 

    # check moisture
    for plant in plants_list:
        target_moisture  = plant.moisture
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

        # update database
        plant.water_volume = new_water_volume
        db.session.commit()      