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

class Sensor_GPIO_A00(db.Model):
    __tablename__ = 'sensor_gpio_a00'
    id        = db.Column(db.Integer, primary_key=True, autoincrement = True)
    value     = db.Column(db.String(50))    
    date      = db.Column(db.String(50))

class Sensor_GPIO_A01(db.Model):
    __tablename__ = 'sensor_gpio_a01'
    id        = db.Column(db.Integer, primary_key=True, autoincrement = True)
    value     = db.Column(db.String(50))    
    date      = db.Column(db.String(50))

class Sensor_GPIO_A02(db.Model):
    __tablename__ = 'sensor_gpio_a02'
    id        = db.Column(db.Integer, primary_key=True, autoincrement = True)
    value     = db.Column(db.String(50))    
    date      = db.Column(db.String(50))

class Sensor_GPIO_A03(db.Model):
    __tablename__ = 'sensor_gpio_a03'
    id        = db.Column(db.Integer, primary_key=True, autoincrement = True)
    value     = db.Column(db.String(50))    
    date      = db.Column(db.String(50))

class Sensor_GPIO_A04(db.Model):
    __tablename__ = 'sensor_gpio_a04'
    id        = db.Column(db.Integer, primary_key=True, autoincrement = True)
    value     = db.Column(db.String(50))    
    date      = db.Column(db.String(50))

class Sensor_GPIO_A05(db.Model):
    __tablename__ = 'sensor_gpio_a05'
    id        = db.Column(db.Integer, primary_key=True, autoincrement = True)
    value     = db.Column(db.String(50))    
    date      = db.Column(db.String(50))

class Sensor_GPIO_A06(db.Model):
    __tablename__ = 'sensor_gpio_a06'
    id        = db.Column(db.Integer, primary_key=True, autoincrement = True)
    value     = db.Column(db.String(50))    
    date      = db.Column(db.String(50))  

class Sensor_GPIO_A07(db.Model):
    __tablename__ = 'sensor_gpio_a07'
    id        = db.Column(db.Integer, primary_key=True, autoincrement = True)
    value     = db.Column(db.String(50))    
    date      = db.Column(db.String(50))

class Sensor_MQTT_00(db.Model):
    __tablename__ = 'sensor_mqtt_00'
    id        = db.Column(db.Integer, primary_key=True, autoincrement = True)
    value     = db.Column(db.String(50))    
    date      = db.Column(db.String(50))

class Sensor_MQTT_01(db.Model):
    __tablename__ = 'sensor_mqtt_01'
    id        = db.Column(db.Integer, primary_key=True, autoincrement = True)
    value     = db.Column(db.String(50))    
    date      = db.Column(db.String(50))

class Sensor_MQTT_02(db.Model):
    __tablename__ = 'sensor_mqtt_02'
    id        = db.Column(db.Integer, primary_key=True, autoincrement = True)
    value     = db.Column(db.String(50))    
    date      = db.Column(db.String(50))  


# create all database tables
db.create_all()


""" ################ """
""" Sensor Functions """
""" ################ """

def GET_SENSOR_VALUES(id):

    sensor_name = Sensor.query.filter_by(id=id).first()
    sensor_name = sensor_name.name

    if sensor_name == "GPIO_A00":
        sensor_values = Sensor_GPIO_A00.query.all()
    if sensor_name == "GPIO_A01":
        sensor_values = Sensor_GPIO_A01.query.all()
    if sensor_name == "GPIO_A02":
        sensor_values = Sensor_GPIO_A02.query.all()
    if sensor_name == "GPIO_A03":
        sensor_values = Sensor_GPIO_A03.query.all()
    if sensor_name == "GPIO_A04":
        sensor_values = Sensor_GPIO_A04.query.all()
    if sensor_name == "GPIO_A05":
        sensor_values = Sensor_GPIO_A05.query.all()
    if sensor_name == "GPIO_A06":
        sensor_values = Sensor_GPIO_A06.query.all()
    if sensor_name == "GPIO_A07":
        sensor_values = Sensor_GPIO_A07.query.all()        
    if sensor_name == "MQTT_00":
        sensor_values = Sensor_MQTT_00.query.all()
    if sensor_name == "MQTT_01":
        sensor_values = Sensor_MQTT_01.query.all()
    if sensor_name == "MQTT_02":
        sensor_values = Sensor_MQTT_02.query.all()
    
    if sensor_values == []:
        return None
    else:
        return sensor_values


def READ_SENSOR(sensor_name):

    try:

        import gpiozero

        if sensor_name == "GPIO_A00":
            adc = gpiozero.MCP3008(channel = 0)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A00(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A01":
            adc = gpiozero.MCP3008(channel = 1)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A01(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A02":
            adc = gpiozero.MCP3008(channel = 2)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A02(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A03":
            adc = gpiozero.MCP3008(channel = 3)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A03(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A04":
            adc = gpiozero.MCP3008(channel = 4)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A04(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A05":
            adc = gpiozero.MCP3008(channel = 5)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A05(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A06":
            adc = gpiozero.MCP3008(channel = 6)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A06(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A07":
            adc = gpiozero.MCP3008(channel = 7)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A07(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   

        db.session.add(entry)
        db.session.commit()   

    except:
        pass
    

def WRITE_MQTT_DATA(mqtt, result):
    
    if mqtt == 0:
        entry = Sensor_MQTT_00(
            value = result,
            date  = time.strftime("%Y-%m-%d %H:%M"),
        ) 
    if mqtt == 1:
        entry = Sensor_MQTT_01(
            value = result,
            date  = time.strftime("%Y-%m-%d %H:%M"),
        ) 
    if mqtt == 2:
        entry = Sensor_MQTT_02(
            value = result,
            date  = time.strftime("%Y-%m-%d %H:%M"),
        ) 

    db.session.add(entry)
    db.session.commit()   


def DELETE_SENSOR_VALUES(id):

    sensor_name = Sensor.query.filter_by(id=id).first()
    sensor_name = sensor_name.name

    if sensor_name == "GPIO_A00":
        Sensor_GPIO_A00.query.delete()
    if sensor_name == "GPIO_A01":
        Sensor_GPIO_A01.query.delete()
    if sensor_name == "GPIO_A02":
        Sensor_GPIO_A02.query.delete()
    if sensor_name == "GPIO_A03":
        Sensor_GPIO_A03.query.delete()
    if sensor_name == "GPIO_A04":
        Sensor_GPIO_A04.query.delete()
    if sensor_name == "GPIO_A05":
        Sensor_GPIO_A05.query.delete()
    if sensor_name == "GPIO_A06":
        Sensor_GPIO_A06.query.delete()
    if sensor_name == "GPIO_A07":
        Sensor_GPIO_A07.query.delete()
    if sensor_name == "MQTT_00":
        Sensor_MQTT_00.query.delete()
    if sensor_name == "MQTT_01":
        Sensor_MQTT_01.query.delete()
    if sensor_name == "MQTT_02":
        Sensor_MQTT_02.query.delete()

    db.session.commit() 
    return "Werte geloescht"


""" ######## """
""" Watering """
""" ######## """

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
        current_moisture = READ_SENSOR(plant.sensor_name)

        if current_moisture < target_moisture:
            new_water_volume = plant.water_volume * 1.1

        if current_moisture > target_moisture:
            new_water_volume = plant.water_volume * 0.9

        # update database
        plant.water_volume = new_water_volume
        db.session.commit()            





