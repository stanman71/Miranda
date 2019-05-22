from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
import re
import time
import datetime
import os
import yaml
import csv

from app import app


""" ###################### """
""" ###################### """
"""     file management    """
""" ###################### """
""" ###################### """


""" ######## """
""" get PATH """
""" ######## """

# windows
if os.name == "nt":                 
    PATH = os.path.abspath("") 
# linux
else:                               
    PATH = os.path.abspath("") + "/SmartHome"


""" ######### """
""" Systemlog """
""" ######### """

def WRITE_LOGFILE_SYSTEM(log_type, description):
    try:
        # open csv file
        file = PATH + "/logs/log_system.csv"

        with open(file, 'a', newline='', encoding='utf-8') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)                                        
            filewriter.writerow( [str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), str(log_type), str(description) ])
            csvfile.close()
       
    except:
        pass


""" ############ """
""" get database """
""" ############ """

try:
    # open config file
    with open(PATH + "/app/config/config.yaml", "r") as file_config:
        config = yaml.load(file_config, Loader=yaml.SafeLoader)
except:
    pass

        
def GET_CONFIG_DATABASE():
    try:
        return str(config['config']['database'])
    except:
        return "sqlite:///database/smarthome.sqlite3"


app.config['SQLALCHEMY_DATABASE_URI'] = GET_CONFIG_DATABASE()
db = SQLAlchemy(app)


""" ###################### """
""" ###################### """
""" define table structure """
""" ###################### """
""" ###################### """

class Controller(db.Model):
    __tablename__        = 'controller'
    id                   = db.Column(db.Integer, primary_key=True, autoincrement = True)
    mqtt_device_ieeeAddr = db.Column(db.String(50), db.ForeignKey('mqtt_devices.ieeeAddr')) 
    mqtt_device          = db.relationship('MQTT_Devices') 
    command_1            = db.Column(db.String(50))
    task_1               = db.Column(db.String(50))
    command_2            = db.Column(db.String(50))
    task_2               = db.Column(db.String(50))
    command_3            = db.Column(db.String(50))
    task_3               = db.Column(db.String(50))    
    command_4            = db.Column(db.String(50))
    task_4               = db.Column(db.String(50))
    command_5            = db.Column(db.String(50))
    task_5               = db.Column(db.String(50))
    command_6            = db.Column(db.String(50))
    task_6               = db.Column(db.String(50))   
    command_7            = db.Column(db.String(50))
    task_7               = db.Column(db.String(50))
    command_8            = db.Column(db.String(50))
    task_8               = db.Column(db.String(50))
    command_9            = db.Column(db.String(50))
    task_9               = db.Column(db.String(50))   
    error_task_settings  = db.Column(db.String(500), server_default=(""))      
    
class eMail(db.Model):
    __tablename__ = 'email'
    id                  = db.Column(db.Integer, primary_key=True, autoincrement = True)
    mail_server_address = db.Column(db.String(50))
    mail_server_port    = db.Column(db.Integer)
    mail_encoding       = db.Column(db.String(50))
    mail_username       = db.Column(db.String(50))
    mail_password       = db.Column(db.String(50)) 

class Error_List(db.Model):
    __tablename__ = 'error_list'
    id           = db.Column(db.Integer, primary_key=True, autoincrement = True)
    content      = db.Column(db.String(100))

class Global_Settings(db.Model):
    __tablename__ = 'global_settings'
    id            = db.Column(db.Integer, primary_key=True, autoincrement = True)
    setting_name  = db.Column(db.String(50), unique=True)
    setting_value = db.Column(db.String(50))   

class LED_Groups(db.Model):
    __tablename__         = 'led_groups'
    id                    = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name                  = db.Column(db.String(50), unique = True)
    led_ieeeAddr_1        = db.Column(db.String(50))
    led_name_1            = db.Column(db.String(50))
    led_device_type_1     = db.Column(db.String(50))
    active_led_2          = db.Column(db.String(50))
    led_ieeeAddr_2        = db.Column(db.String(50))           
    led_name_2            = db.Column(db.String(50))
    led_device_type_2     = db.Column(db.String(50))
    active_led_3          = db.Column(db.String(50))
    led_ieeeAddr_3        = db.Column(db.String(50))           
    led_name_3            = db.Column(db.String(50))
    led_device_type_3     = db.Column(db.String(50))
    active_led_4          = db.Column(db.String(50))
    led_ieeeAddr_4        = db.Column(db.String(50))       
    led_name_4            = db.Column(db.String(50))
    led_device_type_4     = db.Column(db.String(50))
    active_led_5          = db.Column(db.String(50))
    led_ieeeAddr_5        = db.Column(db.String(50))         
    led_name_5            = db.Column(db.String(50)) 
    led_device_type_5     = db.Column(db.String(50))
    active_led_6          = db.Column(db.String(50))
    led_ieeeAddr_6        = db.Column(db.String(50))
    led_name_6            = db.Column(db.String(50))
    led_device_type_6     = db.Column(db.String(50))
    active_led_7          = db.Column(db.String(50))
    led_ieeeAddr_7        = db.Column(db.String(50))
    led_name_7            = db.Column(db.String(50))
    led_device_type_7     = db.Column(db.String(50))
    active_led_8          = db.Column(db.String(50))
    led_ieeeAddr_8        = db.Column(db.String(50))
    led_name_8            = db.Column(db.String(50))
    led_device_type_8     = db.Column(db.String(50))
    active_led_9          = db.Column(db.String(50))
    led_ieeeAddr_9        = db.Column(db.String(50))
    led_name_9            = db.Column(db.String(50)) 
    led_device_type_9     = db.Column(db.String(50))
    current_setting       = db.Column(db.String(50))
    current_brightness    = db.Column(db.Integer)
    error_change_settings = db.Column(db.String(500), server_default=(""))

class LED_Programs(db.Model):
    __tablename__ = 'led_programs'
    id      = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name    = db.Column(db.String(50), unique = True)
    content = db.Column(db.Text)

class LED_Scenes(db.Model):
    __tablename__ = 'led_scenes'
    id                    = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name                  = db.Column(db.String(50), unique = True) 
    red_1                 = db.Column(db.Integer, server_default=("0"))
    green_1               = db.Column(db.Integer, server_default=("0"))
    blue_1                = db.Column(db.Integer, server_default=("0"))
    color_temp_1          = db.Column(db.Integer, server_default=("0"))
    brightness_1          = db.Column(db.Integer, server_default=("254"))
    active_setting_2      = db.Column(db.String(50))
    red_2                 = db.Column(db.Integer, server_default=("0"))
    green_2               = db.Column(db.Integer, server_default=("0"))
    blue_2                = db.Column(db.Integer, server_default=("0"))
    color_temp_2          = db.Column(db.Integer, server_default=("0"))
    brightness_2          = db.Column(db.Integer, server_default=("254"))
    active_setting_3      = db.Column(db.String(50))
    red_3                 = db.Column(db.Integer, server_default=("0"))
    green_3               = db.Column(db.Integer, server_default=("0"))
    blue_3                = db.Column(db.Integer, server_default=("0"))
    color_temp_3          = db.Column(db.Integer, server_default=("0"))
    brightness_3          = db.Column(db.Integer, server_default=("254"))
    active_setting_4      = db.Column(db.String(50))
    red_4                 = db.Column(db.Integer, server_default=("0"))
    green_4               = db.Column(db.Integer, server_default=("0"))
    blue_4                = db.Column(db.Integer, server_default=("0"))
    color_temp_4          = db.Column(db.Integer, server_default=("0"))
    brightness_4          = db.Column(db.Integer, server_default=("254"))
    active_setting_5      = db.Column(db.String(50))
    red_5                 = db.Column(db.Integer, server_default=("0"))
    green_5               = db.Column(db.Integer, server_default=("0"))
    blue_5                = db.Column(db.Integer, server_default=("0"))
    color_temp_5          = db.Column(db.Integer, server_default=("0"))
    brightness_5          = db.Column(db.Integer, server_default=("254"))        
    active_setting_6      = db.Column(db.String(50))
    red_6                 = db.Column(db.Integer, server_default=("0"))
    green_6               = db.Column(db.Integer, server_default=("0"))
    blue_6                = db.Column(db.Integer, server_default=("0"))
    color_temp_6          = db.Column(db.Integer, server_default=("0"))
    brightness_6          = db.Column(db.Integer, server_default=("254"))
    active_setting_7      = db.Column(db.String(50))
    red_7                 = db.Column(db.Integer, server_default=("0"))
    green_7               = db.Column(db.Integer, server_default=("0"))
    blue_7                = db.Column(db.Integer, server_default=("0"))
    color_temp_7          = db.Column(db.Integer, server_default=("0"))
    brightness_7          = db.Column(db.Integer, server_default=("254"))
    active_setting_8      = db.Column(db.String(50))
    red_8                 = db.Column(db.Integer, server_default=("0"))
    green_8               = db.Column(db.Integer, server_default=("0"))
    blue_8                = db.Column(db.Integer, server_default=("0"))
    color_temp_8          = db.Column(db.Integer, server_default=("0"))
    brightness_8          = db.Column(db.Integer, server_default=("254"))
    active_setting_9      = db.Column(db.String(50))
    red_9                 = db.Column(db.Integer, server_default=("0"))
    green_9               = db.Column(db.Integer, server_default=("0"))
    blue_9                = db.Column(db.Integer, server_default=("0"))
    color_temp_9          = db.Column(db.Integer, server_default=("0"))
    brightness_9          = db.Column(db.Integer, server_default=("254"))   
    error_change_settings = db.Column(db.String(100), server_default=(""))
    error_led_control     = db.Column(db.String(100), server_default=(""))

class MQTT_Devices(db.Model):
    __tablename__ = 'mqtt_devices'
    id                   = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name                 = db.Column(db.String(50), unique=True)
    gateway              = db.Column(db.String(50)) 
    ieeeAddr             = db.Column(db.String(50), unique=True)  
    model                = db.Column(db.String(50))
    device_type          = db.Column(db.String(50))
    description          = db.Column(db.String(200))
    inputs               = db.Column(db.String(200))
    outputs              = db.Column(db.String(200))
    last_contact         = db.Column(db.String(50))
    last_values          = db.Column(db.String(200))  
    last_values_formated = db.Column(db.String(200)) 
    options              = db.Column(db.String(50))
    options_value_1      = db.Column(db.String(50))
    options_value_2      = db.Column(db.String(50))
    options_value_3      = db.Column(db.String(50))
    power_setting        = db.Column(db.String(50))  

class Plants(db.Model):
    __tablename__  = 'plants'
    id                   = db.Column(db.Integer, primary_key=True, autoincrement = True)   
    name                 = db.Column(db.String(50), unique=True)
    mqtt_device_ieeeAddr = db.Column(db.String(50), db.ForeignKey('mqtt_devices.ieeeAddr'))   
    mqtt_device          = db.relationship('MQTT_Devices')      
    pumptime             = db.Column(db.Integer)
    pump_key             = db.Column(db.String(50))
    sensor_key           = db.Column(db.String(50))
    control_sensor       = db.Column(db.String(50))     

class Scheduler_Tasks(db.Model):
    __tablename__ = 'scheduler_tasks'
    id                      = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name                    = db.Column(db.String(50), unique=True)
    task                    = db.Column(db.String(50), server_default=("None"))
    task_type               = db.Column(db.String(50))    
    option_time             = db.Column(db.String(50), server_default=("None"))
    option_sun              = db.Column(db.String(50), server_default=("None"))
    option_sensors          = db.Column(db.String(50), server_default=("None"))
    option_position         = db.Column(db.String(50), server_default=("None"))    
    option_repeat           = db.Column(db.String(50), server_default=("None"))
    day                     = db.Column(db.String(50), server_default=("None"))
    hour                    = db.Column(db.String(50), server_default=("None"))
    minute                  = db.Column(db.String(50), server_default=("None"))
    option_sunrise          = db.Column(db.String(50), server_default=("None")) 
    option_sunset           = db.Column(db.String(50), server_default=("None")) 
    location                = db.Column(db.String(50), server_default=("None"))
    sunrise                 = db.Column(db.String(50), server_default=("None")) 
    sunset                  = db.Column(db.String(50), server_default=("None"))         
    mqtt_device_ieeeAddr_1  = db.Column(db.String(50), server_default=("None"))  
    mqtt_device_name_1      = db.Column(db.String(50), server_default=("None")) 
    mqtt_device_inputs_1    = db.Column(db.String(100), server_default=("None")) 
    sensor_key_1            = db.Column(db.String(50), server_default=("None"))    
    value_1                 = db.Column(db.String(100), server_default=("None"))
    operator_1              = db.Column(db.String(50), server_default=("None"))
    operator_main_1         = db.Column(db.String(50), server_default=("None"))     
    mqtt_device_ieeeAddr_2  = db.Column(db.String(50), server_default=("None"))  
    mqtt_device_name_2      = db.Column(db.String(50), server_default=("None"))        
    mqtt_device_inputs_2    = db.Column(db.String(100), server_default=("None")) 
    sensor_key_2            = db.Column(db.String(50), server_default=("None"))    
    value_2                 = db.Column(db.String(100), server_default=("None"))
    operator_2              = db.Column(db.String(50), server_default=("None"))   
    operator_main_2         = db.Column(db.String(50), server_default=("None"))     
    mqtt_device_ieeeAddr_3  = db.Column(db.String(50), server_default=("None"))  
    mqtt_device_name_3      = db.Column(db.String(50), server_default=("None"))        
    mqtt_device_inputs_3    = db.Column(db.String(100), server_default=("None")) 
    sensor_key_3            = db.Column(db.String(50), server_default=("None"))    
    value_3                 = db.Column(db.String(100), server_default=("None"))
    operator_3              = db.Column(db.String(50), server_default=("None")) 
    option_home             = db.Column(db.String(50), server_default=("None")) 
    option_away             = db.Column(db.String(50), server_default=("None")) 
    ip_addresses            = db.Column(db.String(100), server_default=("None")) 
    error_change_settings   = db.Column(db.String(500), server_default=("")) 
    error_general_settings  = db.Column(db.String(500), server_default=(""))  
    error_time_settings     = db.Column(db.String(500), server_default=(""))   
    error_sun_settings      = db.Column(db.String(500), server_default=(""))       
    error_sensor_settings   = db.Column(db.String(500), server_default=(""))   
    error_position_settings = db.Column(db.String(500), server_default=(""))        
    error_task_settings     = db.Column(db.String(500), server_default=(""))  

class Sensordata_Jobs(db.Model):
    __tablename__  = 'sensordata_jobs'
    id                   = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name                 = db.Column(db.String(50), unique=True)
    filename             = db.Column(db.String(50))
    mqtt_device_ieeeAddr = db.Column(db.String(50), db.ForeignKey('mqtt_devices.ieeeAddr'))  
    mqtt_device          = db.relationship('MQTT_Devices')  
    sensor_key           = db.Column(db.String(50)) 
    always_active        = db.Column(db.String(50))

class Snowboy_Settings(db.Model):
    __tablename__  = 'snowboy_settings'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    sensitivity = db.Column(db.Integer)
    timeout     = db.Column(db.Integer)
    microphone  = db.Column(db.String(50))

class Speech_Recognition_Provider_Settings(db.Model):
    __tablename__ = 'speech_recognition_provider_settings'
    id                                   = db.Column(db.Integer, primary_key=True, autoincrement = True)
    snowboy_hotword                      = db.Column(db.String(100))
    speech_recognition_provider          = db.Column(db.String(100))
    speech_recognition_provider_username = db.Column(db.String(100))
    speech_recognition_provider_key      = db.Column(db.String(200))
    
class Speech_Recognition_Provider_Tasks(db.Model):
    __tablename__ = 'speech_recognition_provider_tasks'
    id         = db.Column(db.Integer, primary_key=True, autoincrement = True)
    task       = db.Column(db.String(50))
    keywords   = db.Column(db.String(50))
    parameters = db.Column(db.String(100))

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id                        = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username                  = db.Column(db.String(50), unique=True)
    email                     = db.Column(db.String(50), unique=True)
    password                  = db.Column(db.String(100))
    role                      = db.Column(db.String(20), server_default=("guest")) 
    email_notification_info   = db.Column(db.String(20), server_default=(""))
    email_notification_error  = db.Column(db.String(20), server_default=(""))
    email_notification_camera = db.Column(db.String(20), server_default=(""))

class ZigBee2MQTT(db.Model):
    __tablename__ = 'zigbee2mqtt'
    id      = db.Column(db.Integer, primary_key=True, autoincrement = True)
    pairing = db.Column(db.String(50))


""" ################################ """
""" ################################ """
""" create tables and default values """
""" ################################ """
""" ################################ """


# create all database tables
db.create_all()


# create default email
if eMail.query.filter_by().first() is None:
    email = eMail(
        id = 1,
    )
    db.session.add(email)
    db.session.commit()


# create error list
if Error_List.query.filter_by().first() is None:      
    error = Error_List(
        id = 1,
        content = "",
    )        
    db.session.add(error)
    db.session.commit()


# create default global settings
if Global_Settings.query.filter_by().first() is None:
    setting_mqtt = Global_Settings(
        setting_name  = "mqtt",
        setting_value = "False",
    )
    db.session.add(setting_mqtt)    
    db.session.commit()
    
    setting_zigbee2mqtt = Global_Settings(
        setting_name  = "zigbee2mqtt",
        setting_value = "False",
    )
    db.session.add(setting_zigbee2mqtt)    
    db.session.commit()

    setting_speech_control = Global_Settings(
        setting_name  = "speech_control",
        setting_value = "False",
    )
    db.session.add(setting_speech_control)    
    db.session.commit()


# create default snowboy settings
if Snowboy_Settings.query.filter_by().first() is None:
    snowboy = Snowboy_Settings(
        sensitivity  = 50,
        timeout = 5,
    )
    db.session.add(snowboy)
    db.session.commit()


# create default speech control settings
if Speech_Recognition_Provider_Settings.query.filter_by().first() is None:
    speech_recognition_provider = Speech_Recognition_Provider_Settings(
    )
    db.session.add(speech_recognition_provider)
    db.session.commit()


# create default user
if User.query.filter_by(username='default').first() is None:
    user = User(
        username='default',
        email='member@example.com',
        password=generate_password_hash('qwer1234', method='sha256'),
        role='superuser'
    )
    db.session.add(user)
    db.session.commit()


# create default zigbee2mqtt
if ZigBee2MQTT.query.filter_by().first() is None:
    zigbee2mqtt = ZigBee2MQTT(
        pairing = "False",
    )
    db.session.add(zigbee2mqtt)
    db.session.commit()


""" ################################ """
""" ################################ """
"""        database functions        """
""" ################################ """
""" ################################ """


""" ################## """
""" ################## """
"""     Controller     """
""" ################## """
""" ################## """


def GET_ALL_CONTROLLER():   
    return Controller.query.all()


def GET_CONTROLLER_BY_ID(id):
    return Controller.query.filter_by(id=id).first()


def GET_CONTROLLER_BY_NAME(name):
    return Controller.query.filter_by(name=name).first()
    

def ADD_CONTROLLER(mqtt_device_ieeeAddr):
    # controller exist ?
    
    check_entry = Controller.query.filter_by(mqtt_device_ieeeAddr=mqtt_device_ieeeAddr).first()
    if check_entry is None:
        if mqtt_device_ieeeAddr == "":
            return "Keinen Controller angegeben"
        else:
            # find a unused id
            for i in range(1,21):
                if Controller.query.filter_by(id=i).first():
                    pass
                else:
                    # add new controller
                    new_controller = Controller(
                                          id = i,
                        mqtt_device_ieeeAddr = mqtt_device_ieeeAddr,
                        )
                    db.session.add(new_controller)
                    db.session.commit()
                    
                    UPDATE_CONTROLLER_COMMANDS()
                    
                    controller_name = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr).name

                    WRITE_LOGFILE_SYSTEM("EVENT", "Database | Controller - " + controller_name + " | added")  

                    return ""

            return "Controllerlimit erreicht (20)"

    else:
        return "Controller bereits vorhanden"    


def UPDATE_CONTROLLER_COMMANDS(): 
    
    for controller in GET_ALL_CONTROLLER():
    
        mqtt_device_inputs = GET_MQTT_DEVICE_BY_IEEEADDR(controller.mqtt_device_ieeeAddr).inputs
        mqtt_device_inputs = mqtt_device_inputs.split(",")

        try:
            mqtt_device_input    = mqtt_device_inputs[0].replace(" ","")
            mqtt_device_input    = mqtt_device_input.replace("=", " = ")
            controller.command_1 = mqtt_device_input
        except:
            controller.command_1 = "None"
        try:
            mqtt_device_input    = mqtt_device_inputs[1].replace(" ","")
            mqtt_device_input    = mqtt_device_input.replace("=", " = ")
            controller.command_2 = mqtt_device_input
        except:
            controller.command_2 = "None"
        try:
            mqtt_device_input    = mqtt_device_inputs[2].replace(" ","")
            mqtt_device_input    = mqtt_device_input.replace("=", " = ")
            controller.command_3 = mqtt_device_input
        except:
            controller.command_3 = "None"
        try:
            mqtt_device_input    = mqtt_device_inputs[3].replace(" ","")
            mqtt_device_input    = mqtt_device_input.replace("=", " = ")
            controller.command_4 = mqtt_device_input
        except:
            controller.command_4 = "None"
        try:
            mqtt_device_input    = mqtt_device_inputs[4].replace(" ","")
            mqtt_device_input    = mqtt_device_input.replace("=", " = ")
            controller.command_5 = mqtt_device_input
        except:
            controller.command_5 = "None"
        try:
            mqtt_device_input    = mqtt_device_inputs[5].replace(" ","")
            mqtt_device_input    = mqtt_device_input.replace("=", " = ")
            controller.command_6 = mqtt_device_input
        except:
            controller.command_6 = "None"            
        try:
            mqtt_device_input    = mqtt_device_inputs[6].replace(" ","")
            mqtt_device_input    = mqtt_device_input.replace("=", " = ")
            controller.command_7 = mqtt_device_input
        except:
            controller.command_7 = "None"
        try:
            mqtt_device_input    = mqtt_device_inputs[7].replace(" ","")
            mqtt_device_input    = mqtt_device_input.replace("=", " = ")
            controller.command_8 = mqtt_device_input
        except:
            controller.command_8 = "None"
        try:
            mqtt_device_input    = mqtt_device_inputs[8].replace(" ","")
            mqtt_device_input    = mqtt_device_input.replace("=", " = ")
            controller.command_9 = mqtt_device_input
        except:
            controller.command_9 = "None"      

        db.session.commit()


def SET_CONTROLLER_TASKS(id, task_1 = "", task_2 = "", task_3 = "", task_4 = "", task_5 = "",
                             task_6 = "", task_7 = "", task_8 = "", task_9 = ""):  

    entry = Controller.query.filter_by(id=id).first()
    entry.task_1 = task_1
    entry.task_2 = task_2
    entry.task_3 = task_3   
    entry.task_4 = task_4
    entry.task_5 = task_5
    entry.task_6 = task_6     
    entry.task_7 = task_7
    entry.task_8 = task_8
    entry.task_9 = task_9               
    db.session.commit()


def SET_CONTROLLER_TASK_ERRORS(id, error_task_settings):    
    entry = Controller.query.filter_by(id=id).first()

    entry.error_task_settings = error_task_settings
    db.session.commit()   


def RESET_CONTROLLER_ERRORS(id):    
    entry = Controller.query.filter_by(id=id).first()

    entry.error_task_settings     = ""
    db.session.commit()   


def CHANGE_CONTROLLER_POSITION(id, direction):
    
    if direction == "up":
        controller_list = GET_ALL_CONTROLLER()
        controller_list = controller_list[::-1]
        
        for controller in controller_list:
            
            if controller.id < id:     
                new_id = controller.id
                
                # change ids
                controller_1 = GET_CONTROLLER_BY_ID(id)
                controller_2 = GET_CONTROLLER_BY_ID(new_id)
                
                controller_1.id = 99
                db.session.commit()
                
                controller_2.id = id
                controller_1.id = new_id
                db.session.commit()
                
                return 

    if direction == "down":
        for controller in GET_ALL_CONTROLLER():
            if controller.id > id:       
                new_id = controller.id
                
                # change ids
                controller_1 = GET_CONTROLLER_BY_ID(id)
                controller_2 = GET_CONTROLLER_BY_ID(new_id)
                
                controller_1.id = 99
                db.session.commit()
                
                controller_2.id = id
                controller_1.id = new_id
                db.session.commit()
                
                return 


def DELETE_CONTROLLER(id):
    mqtt_device_ieeeAddr = GET_CONTROLLER_BY_ID(id).mqtt_device_ieeeAddr
    controller_name      = GET_MQTT_DEVICE_BY_IEEEADDR(mqtt_device_ieeeAddr).name
    
    try:
        WRITE_LOGFILE_SYSTEM("EVENT", "Database | Controller - " + controller_name + " | deleted")   
    except:
        pass     
    
    Controller.query.filter_by(id=id).delete()
    db.session.commit() 
    

""" ################## """
""" ################## """
"""        eMail       """
""" ################## """
""" ################## """


def GET_EMAIL_CONFIG():   
    return eMail.query.all()


def GET_EMAIL_ADDRESS(address_type): 
    if address_type == "test":
        mail_list = []
        mail_list.append(eMail.query.filter_by().first().mail_username)
        return mail_list

    if address_type == "info":
        mail_list = []
        users = User.query.all()
        for user in users:
            if user.email_notification_info == "checked":
                mail_list.append(user.email)
        return mail_list

    if address_type == "error":
        mail_list = []
        users = User.query.all()
        for user in users:
            if user.email_notification_error == "checked":
                mail_list.append(user.email)
        return mail_list

    if address_type == "camera":
        mail_list = []
        users = User.query.all()
        for user in users:
            if user.email_notification_camera == "checked":
                mail_list.append(user.email)
        return mail_list


def SET_EMAIL_SETTINGS(mail_server_address, mail_server_port, mail_encoding, mail_username, mail_password): 
    email = eMail.query.filter_by().first()
    email.mail_server_address = mail_server_address
    email.mail_server_port    = mail_server_port
    email.mail_encoding       = mail_encoding
    email.mail_username       = mail_username
    email.mail_password       = mail_password
    db.session.commit()
    
    WRITE_LOGFILE_SYSTEM("EVENT", "Database | eMail Server Settings | changed")
    return ""


""" ################## """
""" ################## """
"""     error list     """
""" ################## """
""" ################## """


def SET_ERROR_LIST(content):
    entry = Error_List.query.filter_by(id=1).first()
    entry.content = content
    db.session.commit()  


def GET_ERROR_LIST():
    entry = Error_List.query.filter_by(id=1).first()
    return entry.content


""" ################### """
""" ################### """
"""   global settings   """
""" ################### """
""" ################### """


def GET_GLOBAL_SETTING_VALUE(name):
    return Global_Settings.query.filter_by(setting_name=name).first().setting_value


def SET_GLOBAL_SETTING_VALUE(name, value):
    entry = Global_Settings.query.filter_by(setting_name=name).first()
    entry.setting_value = value
    db.session.commit()    
    

""" ################### """
""" ################### """
"""    led scenes     """
""" ################### """
""" ################### """


def GET_ALL_LED_SCENES():
    return LED_Scenes.query.all()   


def GET_LED_SCENE_BY_ID(id):
    return LED_Scenes.query.filter_by(id=id).first()


def GET_LED_SCENE_BY_NAME(name):
    return LED_Scenes.query.filter_by(name=name).first()


def ADD_LED_SCENE(name):
    # name exist ?
    check_entry = LED_Scenes.query.filter_by(name=name).first()
    if check_entry is None:
        if name == "":
            return "Kein Name angegeben"
        else:
            # find a unused id
            for i in range(1,21):
                if LED_Scenes.query.filter_by(id=i).first():
                    pass
                else:
                    # add the new program
                    scene = LED_Scenes(
                            id = i,
                            name = name,
                        )
                    db.session.add(scene)
                    db.session.commit()

                    RESET_LED_SCENE_ERRORS(i)

                    WRITE_LOGFILE_SYSTEM("EVENT", "Database | LED Scene - " + name + " | added")  

                    return ""

            return "Szenenlimit erreicht (20)"

    else:
        return "Name bereits vergeben"


def SET_LED_SCENE(id, name, red_1, green_1, blue_1, color_temp_1, brightness_1,
                            red_2, green_2, blue_2, color_temp_2, brightness_2,
                            red_3, green_3, blue_3, color_temp_3, brightness_3,
                            red_4, green_4, blue_4, color_temp_4, brightness_4,
                            red_5, green_5, blue_5, color_temp_5, brightness_5,
                            red_6, green_6, blue_6, color_temp_6, brightness_6,
                            red_7, green_7, blue_7, color_temp_7, brightness_7,
                            red_8, green_8, blue_8, color_temp_8, brightness_8,
                            red_9, green_9, blue_9, color_temp_9, brightness_9):

    entry = LED_Scenes.query.filter_by(id=id).first()
    entry.name  = name
    entry.red_1 = red_1
    entry.green_1 = green_1   
    entry.blue_1 = blue_1
    entry.color_temp_1 = color_temp_1
    entry.brightness_1 = brightness_1
    entry.red_2 = red_2
    entry.green_2 = green_2   
    entry.blue_2 = blue_2
    entry.color_temp_2 = color_temp_2
    entry.brightness_2 = brightness_2
    entry.red_3 = red_3
    entry.green_3 = green_3   
    entry.blue_3 = blue_3
    entry.color_temp_3 = color_temp_3
    entry.brightness_3 = brightness_3    
    entry.red_4 = red_4
    entry.green_4 = green_4   
    entry.blue_4 = blue_4
    entry.color_temp_4 = color_temp_4
    entry.brightness_4 = brightness_4
    entry.red_5 = red_5
    entry.green_5 = green_5   
    entry.blue_5 = blue_5
    entry.color_temp_5 = color_temp_5
    entry.brightness_5 = brightness_5
    entry.red_6 = red_6
    entry.green_6 = green_6   
    entry.blue_6 = blue_6
    entry.color_temp_6 = color_temp_6
    entry.brightness_6 = brightness_6
    entry.red_7 = red_7
    entry.green_7 = green_7   
    entry.blue_7 = blue_7
    entry.color_temp_7 = color_temp_7
    entry.brightness_7 = brightness_7
    entry.red_8 = red_8
    entry.green_8 = green_8   
    entry.blue_8 = blue_8
    entry.color_temp_8 = color_temp_8
    entry.brightness_8 = brightness_8
    entry.red_9 = red_9
    entry.green_9 = green_9   
    entry.blue_9 = blue_9
    entry.color_temp_9 = color_temp_9
    entry.brightness_9 = brightness_9                    
    db.session.commit()  


def ADD_LED_SCENE_SETTING(id):
    entry = LED_Scenes.query.filter_by(id=id).first()

    if entry.active_setting_2 != "on":
        entry.active_setting_2 = "on"
        db.session.commit()
        return
    if entry.active_setting_3 != "on":
        entry.active_setting_3 = "on"
        db.session.commit()
        return
    if entry.active_setting_4 != "on":
        entry.active_setting_4 = "on"
        db.session.commit()
        return
    if entry.active_setting_5 != "on":
        entry.active_setting_5 = "on"
        db.session.commit()
        return
    if entry.active_setting_6 != "on":
        entry.active_setting_6 = "on"
        db.session.commit()
        return
    if entry.active_setting_7 != "on":
        entry.active_setting_7 = "on"
        db.session.commit()
        return
    if entry.active_setting_8 != "on":
        entry.active_setting_8 = "on"
        db.session.commit()
        return       
    if entry.active_setting_9 != "on":
        entry.active_setting_9 = "on"
        db.session.commit()
        return  


def SET_LED_SCENE_CHANGE_ERRORS(id, error_change_settings):
    entry = LED_Scenes.query.filter_by(id=id).first()

    entry.error_change_settings = error_change_settings
    db.session.commit()


def SET_LED_SCENE_CONTROL_ERRORS(id, error_led_control):
    entry = LED_Scenes.query.filter_by(id=id).first()

    entry.error_led_control = error_led_control
    db.session.commit()


def RESET_LED_SCENE_ERRORS(id):
    entry = LED_Scenes.query.filter_by(id=id).first()

    entry.error_change_settings = ""
    entry.error_led_control = ""
    db.session.commit()


def CHANGE_LED_SCENE_POSITION(id, direction):
    
    if direction == "up":
        scenes_list = GET_ALL_LED_SCENES()
        scenes_list = scenes_list[::-1]
        
        for scene in scenes_list:
            
            if scene.id < id:    
                new_id = scene.id
                
                # change ids
                scene_1 = GET_LED_SCENE_BY_ID(id)
                scene_2 = GET_LED_SCENE_BY_ID(new_id)
                
                scene_1.id = 99
                db.session.commit()
                
                scene_2.id = id
                scene_1.id = new_id
                db.session.commit()
                
                return 

    if direction == "down":
        for scene in GET_ALL_LED_SCENES():
            if scene.id > id:   
                new_id = scene.id
                
                # change ids
                scene_1 = GET_LED_SCENE_BY_ID(id)
                scene_2 = GET_LED_SCENE_BY_ID(new_id)
                
                scene_1.id = 99
                db.session.commit()
                
                scene_2.id = id
                scene_1.id = new_id
                db.session.commit()
                
                return 


def REMOVE_LED_SCENE_SETTING(id, setting):
    entry = LED_Scenes.query.filter_by(id=id).first()

    if setting == 2:
        entry.active_setting_2 = "None"
        entry.red_2            = 0
        entry.green_2          = 0
        entry.blue_2           = 0
        entry.color_temp_2     = 0
        entry.brightness_2     = 254
    if setting == 3:
        entry.active_setting_3 = "None"
        entry.red_3            = 0
        entry.green_3          = 0
        entry.blue_3           = 0
        entry.color_temp_3     = 0
        entry.brightness_3     = 254        
    if setting == 4:
        entry.active_setting_4 = "None"
        entry.red_4            = 0
        entry.green_4          = 0
        entry.blue_4           = 0
        entry.color_temp_4     = 0
        entry.brightness_4     = 254
    if setting == 5:
        entry.active_setting_5 = "None"
        entry.red_5            = 0
        entry.green_5          = 0
        entry.blue_5           = 0
        entry.color_temp_5     = 0
        entry.brightness_5     = 254
    if setting == 6:
        entry.active_setting_6 = "None"
        entry.red_6            = 0
        entry.green_6          = 0
        entry.blue_6           = 0
        entry.color_temp_6     = 0
        entry.brightness_6     = 254
    if setting == 7:
        entry.active_setting_7 = "None"
        entry.red_7            = 0
        entry.green_7          = 0
        entry.blue_7           = 0
        entry.color_temp_7     = 0
        entry.brightness_7     = 254
    if setting == 8:
        entry.active_setting_8 = "None"
        entry.red_8            = 0
        entry.green_8          = 0
        entry.blue_8           = 0
        entry.color_temp_8     = 0
        entry.brightness_8     = 254
    if setting == 9:
        entry.active_setting_9 = "None"
        entry.red_9            = 0
        entry.green_9          = 0
        entry.blue_9           = 0
        entry.color_temp_9     = 0
        entry.brightness_9     = 254

    db.session.commit()
    return


def DELETE_LED_SCENE(id):
    name = GET_LED_SCENE_BY_ID(id).name
    
    try:
        WRITE_LOGFILE_SYSTEM("EVENT", "Database | LED Scene - " + name + " | deleted") 
    except:
        pass 

    LED_Scenes.query.filter_by(id=id).delete()
    db.session.commit() 


""" ################### """
""" ################### """
"""    led programs     """
""" ################### """
""" ################### """


def GET_ALL_LED_PROGRAMS():
    return LED_Programs.query.all()   


def GET_LED_PROGRAM_BY_NAME(name):
    return LED_Programs.query.filter_by(name=name).first()


def GET_LED_PROGRAM_BY_ID(id):
    return LED_Programs.query.filter_by(id=id).first()


def ADD_LED_PROGRAM(name):
    # name exist ?
    check_entry = LED_Programs.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,21):
            if LED_Programs.query.filter_by(id=i).first():
                pass
            else:
                # add the new program
                program = LED_Programs(
                        id = i,
                        name = name,
                        content = "",
                    )
                db.session.add(program)
                db.session.commit()

                WRITE_LOGFILE_SYSTEM("EVENT", "Database | LED Program - " + name + " | added")  

                return ""

        return "Programmlimit erreicht (20)"

    else:
        return "Name bereits vergeben"


def SET_LED_PROGRAM_NAME(id, name):
    check_entry = LED_Programs.query.filter_by(name=name).first()
    if check_entry is None:
        entry = LED_Programs.query.filter_by(id=id).first()
        entry.name = name
        db.session.commit()    


def SAVE_LED_PROGRAM(id, content):
    entry = LED_Programs.query.filter_by(id=id).first()
    entry.content = content
    
    db.session.commit()


def DELETE_LED_PROGRAM(id):
    name = LED_Programs.query.filter_by(id=id).first().name
    
    try:
        WRITE_LOGFILE_SYSTEM("EVENT", "Database | LED Program - " + name + " | deleted")  
    except:
        pass 

    LED_Programs.query.filter_by(id=id).delete()
    db.session.commit() 


""" ################### """
""" ################### """
"""     led groups      """
""" ################### """
""" ################### """


def GET_ALL_LED_GROUPS():
    return LED_Groups.query.all()   
  
    
def GET_ALL_ACTIVE_LED_GROUPS():
    list_active_groups = []

    for group in LED_Groups.query.all():
        if group.led_ieeeAddr_1 != None and group.led_ieeeAddr_1 != "None":
            list_active_groups.append(group)
            
    return list_active_groups
          

def GET_LED_GROUP_BY_ID(id):
    return LED_Groups.query.filter_by(id=id).first()


def GET_LED_GROUP_BY_NAME(name):
    return LED_Groups.query.filter_by(name=name).first()


def ADD_LED_GROUP(name):
    # name exist ?
    check_entry = LED_Groups.query.filter_by(name=name).first()
    if check_entry is None:
        if name == "":
            return "Kein Name angegeben"
        else:
            # find a unused id
            for i in range(1,21):
                if LED_Groups.query.filter_by(id=i).first():
                    pass
                else:
                    # add the new program
                    group = LED_Groups(
                            id = i,
                            name = name,
                        )
                    db.session.add(group)
                    db.session.commit()

                    RESET_LED_GROUP_ERRORS(i)

                    WRITE_LOGFILE_SYSTEM("EVENT", "Database | LED Group - " + name + " | added")  

                    return ""

            return "Gruppenlimit erreicht (20)"

    else:
        return "Name bereits vergeben"


def SET_LED_GROUP(id, name, led_ieeeAddr_1, led_name_1, led_device_type_1, 
                            led_ieeeAddr_2, led_name_2, led_device_type_2,
                            led_ieeeAddr_3, led_name_3, led_device_type_3,
                            led_ieeeAddr_4, led_name_4, led_device_type_4,
                            led_ieeeAddr_5, led_name_5, led_device_type_5,
                            led_ieeeAddr_6, led_name_6, led_device_type_6,
                            led_ieeeAddr_7, led_name_7, led_device_type_7,
                            led_ieeeAddr_8, led_name_8, led_device_type_8,
                            led_ieeeAddr_9, led_name_9, led_device_type_9):

    entry = LED_Groups.query.filter_by(id=id).first()
    entry.name = name
    
    entry.led_ieeeAddr_1    = led_ieeeAddr_1
    entry.led_name_1        = led_name_1
    entry.led_device_type_1 = led_device_type_1
    entry.led_ieeeAddr_2    = led_ieeeAddr_2
    entry.led_name_2        = led_name_2
    entry.led_device_type_2 = led_device_type_2 
    entry.led_ieeeAddr_3    = led_ieeeAddr_3
    entry.led_name_3        = led_name_3
    entry.led_device_type_3 = led_device_type_3
    entry.led_ieeeAddr_4    = led_ieeeAddr_4
    entry.led_name_4        = led_name_4
    entry.led_device_type_4 = led_device_type_4
    entry.led_ieeeAddr_5    = led_ieeeAddr_5
    entry.led_name_5        = led_name_5
    entry.led_device_type_5 = led_device_type_5
    entry.led_ieeeAddr_6    = led_ieeeAddr_6
    entry.led_name_6        = led_name_6
    entry.led_device_type_6 = led_device_type_6 
    entry.led_ieeeAddr_7    = led_ieeeAddr_7
    entry.led_name_7        = led_name_7
    entry.led_device_type_7 = led_device_type_7
    entry.led_ieeeAddr_8    = led_ieeeAddr_8
    entry.led_name_8        = led_name_8
    entry.led_device_type_8 = led_device_type_8
    entry.led_ieeeAddr_9    = led_ieeeAddr_9
    entry.led_name_9        = led_name_9
    entry.led_device_type_9 = led_device_type_9
       
    db.session.commit()  


def SET_LED_GROUP_NAME(id, name):
    entry = LED_Groups.query.filter_by(id=id).first()
    entry.name = name
       
    db.session.commit()  


def SET_LED_GROUP_CURRENT_SETTING(id, current_setting):
    entry = LED_Groups.query.filter_by(id=id).first()
    entry.current_setting = current_setting     
    db.session.commit()  


def SET_LED_GROUP_CURRENT_BRIGHTNESS(id, current_brightness):
    entry = LED_Groups.query.filter_by(id=id).first()
    entry.current_brightness = current_brightness     
    db.session.commit()  


def UPDATE_LED_GROUP_LED_NAMES():
    groups = GET_ALL_LED_GROUPS()
    
    for group in groups:
        
        entry = LED_Groups.query.filter_by(id=group.id).first()
        
        try:
            entry.led_name_1        = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_1).name
            entry.led_device_type_1 = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_1).device_type
        except:
            pass
        try:
            entry.led_name_2        = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_2).name
            entry.led_device_type_2 = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_2).device_type
        except:
            pass
        try:
            entry.led_name_3        = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_3).name
            entry.led_device_type_3 = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_3).device_type
        except:
            pass
        try:
            entry.led_name_4        = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_4).name
            entry.led_device_type_4 = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_4).device_type
        except:
            pass
        try:
            entry.led_name_5        = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_5).name
            entry.led_device_type_5 = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_5).device_type
        except:
            pass
        try:
            entry.led_name_6        = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_6).name
            entry.led_device_type_6 = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_6).device_type
        except:
            pass
        try:
            entry.led_name_7        = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_7).name
            entry.led_device_type_7 = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_7).device_type
        except:
            pass
        try:
            entry.led_name_8        = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_8).name
            entry.led_device_type_8 = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_8).device_type
        except:
            pass
        try:
            entry.led_name_9        = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_9).name
            entry.led_device_type_9 = GET_MQTT_DEVICE_BY_IEEEADDR(entry.led_ieeeAddr_9).device_type
        except:
            pass            
        
    db.session.commit()


def ADD_LED_GROUP_LED(id):
    entry = LED_Groups.query.filter_by(id=id).first()

    if entry.active_led_2 != "on":
        entry.active_led_2 = "on"
        db.session.commit()
        return
    if entry.active_led_3 != "on":
        entry.active_led_3 = "on"
        db.session.commit()
        return
    if entry.active_led_4 != "on":
        entry.active_led_4 = "on"
        db.session.commit()
        return
    if entry.active_led_5 != "on":
        entry.active_led_5 = "on"
        db.session.commit()
        return
    if entry.active_led_6 != "on":
        entry.active_led_6 = "on"
        db.session.commit()
        return
    if entry.active_led_7 != "on":
        entry.active_led_7 = "on"
        db.session.commit()
        return
    if entry.active_led_8 != "on":
        entry.active_led_8 = "on"
        db.session.commit()
        return       
    if entry.active_led_9 != "on":
        entry.active_led_9 = "on"
        db.session.commit()
        return  


def SET_LED_GROUP_CHANGE_ERRORS(id, error_change_settings):
    entry = LED_Groups.query.filter_by(id=id).first()

    entry.error_change_settings = error_change_settings
    db.session.commit()


def RESET_LED_GROUP_ERRORS(id):
    entry = LED_Groups.query.filter_by(id=id).first()

    entry.error_change_settings = ""
    db.session.commit()


def CHANGE_LED_GROUP_POSITION(id, direction):
    
    if direction == "up":
        groups_list = GET_ALL_LED_GROUPS()
        groups_list = groups_list[::-1]
        
        for group in groups_list:
            
            if group.id < id: 
                new_id = group.id
                
                # change ids
                group_1 = GET_LED_GROUP_BY_ID(id)
                group_2 = GET_LED_GROUP_BY_ID(new_id)
                
                group_1.id = 99
                db.session.commit()
                
                group_2.id = id
                group_1.id = new_id
                db.session.commit()
                
                return 

    if direction == "down":
        for group in GET_ALL_LED_GROUPS():
            if group.id > id:
                new_id = group.id
                
                # change ids
                group_1 = GET_LED_GROUP_BY_ID(id)
                group_2 = GET_LED_GROUP_BY_ID(new_id)
                
                group_1.id = 99
                db.session.commit()
                
                group_2.id = id
                group_1.id = new_id
                db.session.commit()
                
                return 


def REMOVE_LED_GROUP_LED(id, led):
    entry = LED_Groups.query.filter_by(id=id).first()

    if led == 2:
        entry.active_led_2      = "None"
        entry.led_ieeeAddr_2    = "None"
        entry.led_name_2        = "None"
        entry.led_device_type_2 = "None"
    if led == 3:
        entry.active_led_3      = "None"     
        entry.led_ieeeAddr_3    = "None"
        entry.led_name_3        = "None" 
        entry.led_device_type_3 = "None"
    if led == 4:
        entry.active_led_4      = "None"     
        entry.led_ieeeAddr_4    = "None"
        entry.led_name_4        = "None" 
        entry.led_device_type_4 = "None"
    if led == 5:
        entry.active_led_5      = "None"     
        entry.led_ieeeAddr_5    = "None"
        entry.led_name_5        = "None" 
        entry.led_device_type_5 = "None"
    if led == 6:
        entry.active_led_6      = "None"     
        entry.led_ieeeAddr_6    = "None"
        entry.led_name_6        = "None" 
        entry.led_device_type_6 = "None"
    if led == 7:
        entry.active_led_7      = "None"     
        entry.led_ieeeAddr_7    = "None"
        entry.led_name_7        = "None" 
        entry.led_device_type_7 = "None"
    if led == 8:
        entry.active_led_8      = "None"     
        entry.led_ieeeAddr_8    = "None"
        entry.led_name_8        = "None" 
        entry.led_device_type_8 = "None"
    if led == 9:
        entry.active_led_9      = "None"     
        entry.led_ieeeAddr_9    = "None"
        entry.led_name_9        = "None" 
        entry.led_device_type_9 = "None"

    db.session.commit()


def DELETE_LED_GROUP(id):
    name = GET_LED_GROUP_BY_ID(id).name
    
    try:
        WRITE_LOGFILE_SYSTEM("EVENT", "Database | LED Group - " + name + " | deleted")   
    except:
        pass     
    
    LED_Groups.query.filter_by(id=id).delete()
    db.session.commit() 


""" ################### """
""" ################### """
"""        mqtt         """
""" ################### """
""" ################### """


def GET_MQTT_DEVICE_BY_ID(id):
    return MQTT_Devices.query.filter_by(id=id).first()


def GET_MQTT_DEVICE_BY_NAME(name):
    return MQTT_Devices.query.filter_by(name=name).first()
    
    
def GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr):
    return MQTT_Devices.query.filter_by(ieeeAddr=ieeeAddr).first()   


def GET_ALL_MQTT_DEVICES(selector):
    device_list = []
    devices = MQTT_Devices.query.all()
  
    if selector == "":
        for device in devices:
            device_list.append(device)     
  
    if selector == "controller":
        for device in devices:
            if device.device_type == "controller":
                device_list.append(device)      
 
    if selector == "device":
        for device in devices:
            if device.device_type == "device_switch":
                device_list.append(device)      
  
    if selector == "led":
        for device in devices:
            if (device.device_type == "led_rgb" or 
                device.device_type == "led_white" or 
                device.device_type == "led_simple"):
                    
                device_list.append(device)    
    
    if selector == "mqtt" or selector == "zigbee2mqtt":
        for device in devices:
            if device.gateway == selector:
                device_list.append(device)
                
    if selector == "sensor":
        for device in devices:
            if (device.device_type == "sensor_passiv" or 
                device.device_type == "sensor_active" or 
                device.device_type == "watering_array"):
                
                device_list.append(device)   
     
    if selector == "switch":
        for device in devices:
            if device.device_type == "switch" or device.device_type == "power_switch":
                device_list.append(device)       
                
    if selector == "watering_array":
        for device in devices:
            if device.device_type == "watering_array":
                device_list.append(device)                                                
                
    return device_list
        

def ADD_MQTT_DEVICE(name, gateway, ieeeAddr, model = "", device_type = "", description = "", 
                    inputs = "", outputs = "", last_contact = ""):
                        
    # path exist ?
    check_entry = MQTT_Devices.query.filter_by(ieeeAddr=ieeeAddr).first()
    if check_entry is None:   
            
        # find a unused id
        for i in range(1,51):
            
            if MQTT_Devices.query.filter_by(id=i).first():
                pass
                
            else:
                # add the new device            
                device = MQTT_Devices(
                        id           = i,
                        name         = name,
                        gateway      = gateway,                       
                        ieeeAddr     = ieeeAddr,
                        model        = model,
                        device_type  = device_type,
                        description  = description,
                        inputs       = inputs,
                        outputs      = outputs,
                        last_contact = last_contact,
                        )
                        
                db.session.add(device)
                db.session.commit()
                
                WRITE_LOGFILE_SYSTEM("EVENT", "Database | MQTT Device - " + name + " | added || Gateway - " + gateway + 
                                     " | ieeeAddr - " + ieeeAddr + 
                                     " | Model - " + model + 
                                     " | device_type - " + device_type + 
                                     " | description - " + description + 
                                     " | Inputs - " + inputs + 
                                     " | Outputs - " + outputs)

                SET_MQTT_DEVICE_LAST_CONTACT(ieeeAddr)   
                
                return ""

        return "Gerätelimit erreicht (50)"                           
                
    else:
        SET_MQTT_DEVICE_LAST_CONTACT(ieeeAddr)  


def SET_MQTT_DEVICE_NAME(ieeeAddr, new_name):
    entry = MQTT_Devices.query.filter_by(ieeeAddr=ieeeAddr).first()
    
    WRITE_LOGFILE_SYSTEM("EVENT", "Database | MQTT Device - " + entry.name + 
                         " | Gateway - " + entry.gateway +
                         " | Name changed" + 
                         " || Name - " + new_name)
    
    entry.name = new_name
    db.session.commit()       


def SET_MQTT_DEVICE_LAST_CONTACT(ieeeAddr):
    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
    entry = MQTT_Devices.query.filter_by(ieeeAddr=ieeeAddr).first()
    entry.last_contact = timestamp
    db.session.commit()       


def SET_MQTT_DEVICE_LAST_VALUES(ieeeAddr, last_values):
    entry = MQTT_Devices.query.filter_by(ieeeAddr=ieeeAddr).first()
    
    last_values_formated = last_values.replace("{","")
    last_values_formated = last_values_formated.replace("}","")
    last_values_formated = last_values_formated.replace('"',"")
    last_values_formated = last_values_formated.replace(":",": ")
    last_values_formated = last_values_formated.replace(",",", ")
    
    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    entry.last_values          = last_values
    entry.last_values_formated = last_values_formated
    entry.last_contact         = timestamp
    db.session.commit()   


def SET_MQTT_DEVICE_OPTIONS(ieeeAddr, options, options_value_1, options_value_2, options_value_3):
    entry = MQTT_Devices.query.filter_by(ieeeAddr=ieeeAddr).first()
    
    WRITE_LOGFILE_SYSTEM("EVENT", "Database | MQTT Device - " + entry.name + 
                         " | Gateway - " + entry.gateway +
                         " | Setting changed" + 
                         " || Options - " + options +
                         " | Options_Value_1 - " + options_value_1 +
                         " | Options_Value_2 - " + options_value_2 +                        
                         " | Options_Value_3 - " + options_value_3)
    
    entry.options         = options
    entry.options_value_1 = options_value_1
    entry.options_value_2 = options_value_2
    entry.options_value_3 = options_value_3
    db.session.commit()  


def SET_MQTT_DEVICE_POWERSTATE(ieeeAddr, power_setting):
    entry = MQTT_Devices.query.filter_by(ieeeAddr=ieeeAddr).first()
    
    if power_setting == "checked":
        power = "ON"
    else:
        power = "OFF"
    
    WRITE_LOGFILE_SYSTEM("EVENT", "Database | MQTT Device - " + entry.name + 
                         " | Gateway - " + entry.gateway +
                         " | Setting changed" + 
                         " || Power_Setting - " + power)
    
    entry.power_setting = power_setting
    db.session.commit()  
    
    
def UPDATE_MQTT_DEVICE(id, name, gateway, device_type = "", description = "", inputs = "", outputs = ""):
    entry = MQTT_Devices.query.filter_by(id=id).first()
    
    # values changed ?
    if (entry.name != name or entry.device_type != device_type or entry.description != description 
        or entry.inputs != inputs or entry.outputs != outputs):
        
        entry.device_type = device_type
        entry.description = description
        entry.inputs      = inputs
        entry.outputs     = outputs
        
        WRITE_LOGFILE_SYSTEM("EVENT", "Database | MQTT Device - " + entry.name + 
                             " | Gateway - " + entry.gateway +
                             " | changed" + 
                             " || Name - " + name + 
                             " | ieeeAddr - " + entry.ieeeAddr + 
                             " | Model - " + entry.model +
                             " | device_type - " + entry.device_type +
                             " | description - " + entry.description +
                             " | inputs - " + entry.inputs + 
                             " | outputs - " + outputs)

        entry.name = name
        db.session.commit()    
   
    
def CHANGE_MQTT_DEVICE_POSITION(id, device_type, direction):
    
    if direction == "up":
        device_list = GET_ALL_MQTT_DEVICES(device_type)
        device_list = device_list[::-1]
        
        for device in device_list:
            
            if device.id < id:
                
                new_id = device.id
                
                # change ids
                device_1 = GET_MQTT_DEVICE_BY_ID(id)
                device_2 = GET_MQTT_DEVICE_BY_ID(new_id)
                
                device_1.id = 99
                db.session.commit()
                
                device_2.id = id
                device_1.id = new_id
                db.session.commit()
                
                return 

    if direction == "down":
        for device in GET_ALL_MQTT_DEVICES(device_type):
            if device.id > id:
                
                new_id = device.id
                
                # change ids
                device_1 = GET_MQTT_DEVICE_BY_ID(id)
                device_2 = GET_MQTT_DEVICE_BY_ID(new_id)
                
                device_1.id = 99
                db.session.commit()
                
                device_2.id = id
                device_1.id = new_id
                db.session.commit()
                
                return 


def DELETE_MQTT_DEVICE(id):
    error_list = ""

    # check controller
    entries = GET_ALL_CONTROLLER()
    for entry in entries:
        if entry.mqtt_device_id == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in Systemeinstellungen / Controller"     

    # check plants
    entries = GET_ALL_PLANTS()
    for entry in entries:
        if entry.mqtt_device_id == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in Bewässung >>> Pflanze - " + entry.name     
    
    # check scheduler sensor
    entries = GET_ALL_SCHEDULER_TASKS()
    for entry in entries:
        if (entry.mqtt_device_id_1 == id) or (entry.mqtt_device_id_2 == id) or (entry.mqtt_device_id_3 == id):
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in Aufgabenplanung >>> Sensor - " + entry.name      
    
    # check sensordata
    entries = GET_ALL_SENSORDATA_JOBS()
    for entry in entries:
        if entry.mqtt_device_id == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in Sensordaten >>> Job - " + entry.name  
        
    # check led groups
    entries = GET_ALL_LED_GROUPS()
    for entry in entries:
        if entry.led_id_1 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED / LED-Gruppen >>> Gruppe - " + entry.name  
        if entry.led_id_2 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED / LED-Gruppen >>> Gruppe - " + entry.name     
        if entry.led_id_3 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED / LED-Gruppen >>> Gruppe - " + entry.name  
        if entry.led_id_4 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED / LED-Gruppen >>> Gruppe - " + entry.name  
        if entry.led_id_5 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED / LED-Gruppen >>> Gruppe - " + entry.name  
        if entry.led_id_6 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED / LED-Gruppen >>> Gruppe - " + entry.name   
        if entry.led_id_7 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED / LED-Gruppen >>> Gruppe - " + entry.name  
        if entry.led_id_8 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED / LED-Gruppen >>> Gruppe - " + entry.name          
        if entry.led_id_9 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED / LED-Gruppen >>> Gruppe - " + entry.name                       
       
    if error_list != "":
        error_list = error_list[1:]
        SET_ERROR_LIST(error_list)           
    else:
        entry = GET_MQTT_DEVICE_BY_ID(id)
        
        try:
            WRITE_LOGFILE_SYSTEM("EVENT", "Database | MQTT Device - " + entry.name + " | deleted")
        except:
            pass 
 
        MQTT_Devices.query.filter_by(id=id).delete()
        db.session.commit() 
        return "MQTT-Device gelöscht"


""" ################### """
""" ################### """
"""       plants        """
""" ################### """
""" ################### """


def GET_PLANT_BY_ID(plant_id):
    return Plants.query.filter_by(id=plant_id).first()


def GET_PLANT_BY_NAME(name):
    plants = Plants.query.all()

    for plant in plants:
        if plant.name == name:
            return plant


def GET_ALL_PLANTS():
    return Plants.query.all()


def ADD_PLANT(name, mqtt_device_ieeeAddr):
    # name exist ?
    check_entry = Plants.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,26):
            if Plants.query.filter_by(id=i).first():
                pass
            else:
                # add the new plant
                plant = Plants(
                        id                   = i,
                        name                 = name, 
                        pumptime             = 30,
                        mqtt_device_ieeeAddr = mqtt_device_ieeeAddr                
                    )
                db.session.add(plant)
                db.session.commit()

                WRITE_LOGFILE_SYSTEM("EVENT", "Database | Plant - " + name + " | added")    
                           
                return ""
                
        return "Pflanzenlimit erreicht (25)"

    else:
        return "Name bereits vergeben"


def SET_PLANT_SETTINGS(id, name, mqtt_device_ieeeAddr, pump_key, sensor_key, pumptime, control_sensor):        
    entry = Plants.query.filter_by(id=id).first()
    old_name = entry.name

    # values changed ?
    if (entry.name != name or entry.mqtt_device_ieeeAddr != mqtt_device_ieeeAddr or entry.pump_key != pump_key or  
        entry.sensor_key != sensor_key or entry.pumptime != int(pumptime) or entry.control_sensor != control_sensor):

        entry.name = name
        entry.mqtt_device_ieeeAddr = mqtt_device_ieeeAddr
        entry.pump_key = pump_key
        entry.sensor_key = sensor_key
        entry.pumptime = pumptime
        entry.control_sensor = control_sensor
        
        db.session.commit()  
        
        WRITE_LOGFILE_SYSTEM("EVENT", "Database | Plant - " + old_name + " | changed || Name - " + entry.name + 
                             " | MQTT-Device - " + entry.mqtt_device.name + 
                             " | Pump - " + entry.pump_key + 
                             " | Sensor - " + entry.sensor_key + 
                             " | Pumptime - " + str(entry.pumptime))       


def CHANGE_PLANTS_POSITION(id, direction):
    
    if direction == "up":
        plants_list = GET_ALL_PLANTS()
        plants_list = plants_list[::-1]
        
        for plant in plants_list:
            
            if plant.id < id:     
                new_id = plant.id
                
                # change ids
                plant_1 = GET_PLANT_BY_ID(id)
                plant_2 = GET_PLANT_BY_ID(new_id)
                
                plant_1.id = 99
                db.session.commit()
                
                plant_2.id = id
                plant_1.id = new_id
                db.session.commit()
                
                return 

    if direction == "down":
        for plant in GET_ALL_PLANTS():
            if plant.id > id:       
                new_id = plant.id
                
                # change ids
                plant_1 = GET_PLANT_BY_ID(id)
                plant_2 = GET_PLANT_BY_ID(new_id)
                
                plant_1.id = 99
                db.session.commit()
                
                plant_2.id = id
                plant_1.id = new_id
                db.session.commit()
                
                return 


def DELETE_PLANT(plant_id):
    entry = GET_PLANT_BY_ID(plant_id)
    
    try:
        WRITE_LOGFILE_SYSTEM("EVENT", "Database | Plant - " + entry.name + " | deleted")   
    except:
        pass 
    
    Plants.query.filter_by(id=plant_id).delete()
    db.session.commit()


""" ################## """
""" ################## """
"""      scheduler     """
""" ################## """
""" ################## """


def GET_SCHEDULER_TASK_BY_NAME(name):
    return Scheduler_Tasks.query.filter_by(name=name).first()


def GET_SCHEDULER_TASK_BY_ID(id):
    return Scheduler_Tasks.query.filter_by(id=id).first()


def GET_ALL_SCHEDULER_TASKS():
    return Scheduler_Tasks.query.all()


def GET_ALL_SCHEDULER_TASKS_BY_TYPE(task_type):
    list_tasks = []

    for task in Scheduler_Tasks.query.all():

        if task_type == "reduced":
            if task.task_type == "reduced":
                list_tasks.append(task)

        if task_type == "complete":
            if task.task_type == "complete":
                list_tasks.append(task)

    return list_tasks       


def ADD_SCHEDULER_TASK(name, task_type, option_time = "None"):
    # name exist ?
    check_entry = Scheduler_Tasks.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,26):
            if Scheduler_Tasks.query.filter_by(id=i).first():
                pass
            else:
                # add the new task
                new_task = Scheduler_Tasks(
                        id            = i,
                        name          = name,
                        task_type     = task_type,
                        option_time   = option_time,
                        option_repeat = "checked",
                    )
                db.session.add(new_task)
                db.session.commit()

                SET_SCHEDULER_TASK_CHANGE_ERRORS(i, "")
            
                WRITE_LOGFILE_SYSTEM("EVENT", "Database | Scheduler | Task - " + name + " | Task_Type - " + task_type + " | added")            
                
                return ""

        return "Aufgabenlimit erreicht (25)"

    else:
        return "Name bereits vergeben"


def SET_SCHEDULER_TASK(id, name, task,
                       option_time, option_sun, option_sensors, option_position, option_repeat, 
                       day, hour, minute,
                       option_sunrise, option_sunset, location,
                       mqtt_device_ieeeAddr_1, mqtt_device_name_1, mqtt_device_inputs_1,  
                       sensor_key_1, operator_1, value_1, operator_main_1,
                       mqtt_device_ieeeAddr_2, mqtt_device_name_2, mqtt_device_inputs_2, 
                       sensor_key_2, operator_2, value_2, operator_main_2,
                       mqtt_device_ieeeAddr_3, mqtt_device_name_3, mqtt_device_inputs_3, 
                       sensor_key_3, operator_3, value_3,
                       option_home, option_away, ip_addresses):
                          
     
    entry = Scheduler_Tasks.query.filter_by(id=id).first()
    old_name = entry.name

    # values changed ?
    if (entry.name != name or entry.task != task or 
        entry.option_time != option_time or entry.option_sun != option_sun or entry.option_sensors != option_sensors or 
        entry.option_position != option_position or entry.option_repeat != option_repeat or
        entry.day != day or entry.hour != hour or entry.minute != minute or
        entry.option_sunrise != option_sunrise or entry.option_sunset != option_sunset or entry.location != location or
        entry.mqtt_device_ieeeAddr_1 != mqtt_device_ieeeAddr_1 or entry.sensor_key_1 != sensor_key_1 or 
        entry.operator_1 != operator_1 or entry.value_1 != value_1 or 
        entry.mqtt_device_ieeeAddr_2 != mqtt_device_ieeeAddr_2 or entry.sensor_key_2 != sensor_key_2 or 
        entry.operator_2 != operator_2 or entry.value_2 != value_2 or entry.operator_main_1 != operator_main_1 or
        entry.mqtt_device_ieeeAddr_3 != mqtt_device_ieeeAddr_3 or entry.sensor_key_3 != sensor_key_3 or 
        entry.operator_3 != operator_3 or entry.value_3 != value_3 or entry.operator_main_2 != operator_main_2 or
        entry.option_home != option_home or entry.option_away != option_away or entry.ip_addresses != ip_addresses):

        entry.name                    = name
        entry.task                    = task      
        entry.option_time             = option_time    
        entry.option_sun              = option_sun            
        entry.option_sensors          = option_sensors
        entry.option_position         = option_position        
        entry.option_repeat           = option_repeat
        entry.day                     = day
        entry.hour                    = hour
        entry.minute                  = minute
        entry.option_sunrise          = option_sunrise
        entry.option_sunset           = option_sunset
        entry.location                = location        
        entry.mqtt_device_ieeeAddr_1  = mqtt_device_ieeeAddr_1
        entry.mqtt_device_name_1      = mqtt_device_name_1
        entry.mqtt_device_inputs_1    = mqtt_device_inputs_1
        entry.sensor_key_1            = sensor_key_1
        entry.operator_1              = operator_1
        entry.value_1                 = value_1
        entry.operator_main_1         = operator_main_1
        entry.mqtt_device_ieeeAddr_2  = mqtt_device_ieeeAddr_2
        entry.mqtt_device_name_2      = mqtt_device_name_2
        entry.mqtt_device_inputs_2    = mqtt_device_inputs_2
        entry.sensor_key_2            = sensor_key_2
        entry.operator_2              = operator_2
        entry.value_2                 = value_2        
        entry.operator_main_2         = operator_main_2
        entry.mqtt_device_ieeeAddr_3  = mqtt_device_ieeeAddr_3
        entry.mqtt_device_name_3      = mqtt_device_name_3
        entry.mqtt_device_inputs_3    = mqtt_device_inputs_3
        entry.sensor_key_3            = sensor_key_3
        entry.operator_3              = operator_3
        entry.value_3                 = value_3      
        entry.option_home             = option_home
        entry.option_away             = option_away
        entry.ip_addresses            = ip_addresses

        db.session.commit()   

        log_message = "Database | Scheduler | Task - " + old_name + " | changed || Name - " + entry.name + " | Task - " + entry.task

        # option time
        if entry.option_time == "checked":

            if entry.day == None:
                entry.day = "None"
            if entry.hour == None:
                entry.hour = "None"
            if entry.minute == None:
                entry.minute = "None"

            log_message = log_message + (" | Day - " + entry.day + 
                                         " | Hour - " + entry.hour + 
                                         " | Minute - " + entry.minute)

        # option sun
        if entry.option_sun == "checked":

            if entry.location == None:
                entry.location = "None"

            log_message = log_message + (" | Sunrise - " + entry.option_sunrise +
                                         " | Sunset - " + entry.option_sunset +
                                         " | Location - " + entry.location) 

        # option sensors
        if entry.option_sensors == "checked":

            if entry.operator_main_1 == "None":

                log_message = log_message + (" | MQTT-Device_1 - " + entry.mqtt_device_name_1 + 
                                             " | Sensor_1 - " + entry.sensor_key_1 + 
                                             " | Operator_1 - " + entry.operator_1 + 
                                             " | Value_1 - " +  entry.value_1)
                                                                
            elif entry.operator_main_1 != "None" and entry.operator_main_2 == "None":

                log_message = log_message + (" | MQTT-Device_1 - " + entry.mqtt_device_name_1 + 
                                             " | Sensor_1 - " + entry.sensor_key_1 + 
                                             " | Operator_1 - " + entry.operator_1 + 
                                             " | Value_1 - " +  entry.value_1 + 
                                             " | MQTT-Device_2 - " + entry.mqtt_device_name_2 + 
                                             " | Sensor_2 - " + entry.sensor_key_2 + 
                                             " | Operator_2 - " + entry.operator_2 + 
                                             " | Value_2 - " + entry.value_2)
                                
            else:

                log_message = log_message + (" | MQTT-Device_1 - " + entry.mqtt_device_name_1 + 
                                             " | Sensor_1 - " + entry.sensor_key_1 + 
                                             " | Operator_1 - " + entry.operator_1 + 
                                             " | Value_1 - " + entry.value_1 + 
                                             " | MQTT-Device_2 - " + entry.mqtt_device_name_2 + 
                                             " | Sensor_2 - " + entry.sensor_key_2 + 
                                             " | Operator_2 - " + entry.operator_2 + 
                                             " | Value_2 - " + entry.value_2 +
                                             " | MQTT-Device_3 - " + entry.mqtt_device_name_3 + 
                                             " | Sensor_3 - " + entry.sensor_key_3 + 
                                             " | Operator_3 - " + entry.operator_3 + 
                                             " | Value_3 - " + entry.value_3)

        # option position
        if entry.option_position == "checked":

            if entry.ip_addresses == None:
                entry.ip_addresses = "None"

            log_message = log_message + (" | Home - " + entry.option_home + 
                                         " | Away - " + entry.option_away + 
                                         " | IP-Addresses - " + entry.ip_addresses) 

        # option repeat
        if entry.option_repeat == "checked":

            log_message = log_message + (" | Repeat - " + entry.option_repeat)

        WRITE_LOGFILE_SYSTEM("EVENT", log_message) 


def SET_SCHEDULER_TASK_SUNRISE(id, sunrise):    
    entry = Scheduler_Tasks.query.filter_by(id=id).first()

    entry.sunrise = sunrise
    db.session.commit()   


def GET_SCHEDULER_TASK_SUNRISE(id):    
    return (Scheduler_Tasks.query.filter_by(id=id).first().sunrise)


def SET_SCHEDULER_TASK_SUNSET(id, sunset):    
    entry = Scheduler_Tasks.query.filter_by(id=id).first()

    entry.sunset = sunset
    db.session.commit()   


def GET_SCHEDULER_TASK_SUNSET(id):    
    return (Scheduler_Tasks.query.filter_by(id=id).first().sunset)


def SET_SCHEDULER_TASK_CHANGE_ERRORS(id, error_change_settings):    
    entry = Scheduler_Tasks.query.filter_by(id=id).first()

    entry.error_change_settings = error_change_settings
    db.session.commit()   


def SET_SCHEDULER_TASK_SETTING_GENERAL_ERRORS(id, error_general_settings):    
    entry = Scheduler_Tasks.query.filter_by(id=id).first()

    entry.error_general_settings = error_general_settings
    db.session.commit()   
    

def SET_SCHEDULER_TASK_SETTING_TIME_ERRORS(id, error_time_settings):    
    entry = Scheduler_Tasks.query.filter_by(id=id).first()

    entry.error_time_settings = error_time_settings
    db.session.commit()   


def SET_SCHEDULER_TASK_SETTING_SUN_ERRORS(id, error_sun_settings):    
    entry = Scheduler_Tasks.query.filter_by(id=id).first()

    entry.error_sun_settings = error_sun_settings
    db.session.commit()   


def SET_SCHEDULER_TASK_SETTING_SENSOR_ERRORS(id, error_sensor_settings):    
    entry = Scheduler_Tasks.query.filter_by(id=id).first()

    entry.error_sensor_settings = error_sensor_settings
    db.session.commit()   


def SET_SCHEDULER_TASK_SETTING_POSITION_ERRORS(id, error_position_settings):    
    entry = Scheduler_Tasks.query.filter_by(id=id).first()

    entry.error_position_settings = error_position_settings
    db.session.commit()   


def SET_SCHEDULER_TASK_SETTING_TASK_ERRORS(id, error_task_settings):    
    entry = Scheduler_Tasks.query.filter_by(id=id).first()

    entry.error_task_settings = error_task_settings
    db.session.commit()   


def RESET_SCHEDULER_TASK_ERRORS(id):    
    entry = Scheduler_Tasks.query.filter_by(id=id).first()

    entry.error_change_settings   = ""
    entry.error_general_settings  = ""
    entry.error_time_settings     = ""
    entry.error_sun_settings      = ""    
    entry.error_sensor_settings   = ""
    entry.error_position_settings = ""
    entry.error_task_settings     = ""
    db.session.commit()   


def ADD_SCHEDULER_TASK_SENSOR_ROW(id):
    entry = Scheduler_Tasks.query.filter_by(id=id).first()
    operator_main_1 = entry.operator_main_1 
    operator_main_2 = entry.operator_main_2 

    if operator_main_1 == "None" or operator_main_1 == None:
        entry.operator_main_1 = "and"
        entry.operator_main_2 = "None"

    if operator_main_1 != "None" and operator_main_1 != None:
        entry.operator_main_2 = "and"

    db.session.commit()


def REMOVE_SCHEDULER_TASK_SENSOR_ROW(id):
    entry = Scheduler_Tasks.query.filter_by(id=id).first()
    operator_main_1 = entry.operator_main_1 
    operator_main_2 = entry.operator_main_2 

    if operator_main_2 != "None":
        entry.operator_main_2 = "None"

    if operator_main_2 == "None" or operator_main_2 == None:
        entry.operator_main_1 = "None"

    db.session.commit()


def CHANGE_SCHEDULER_TASK_POSITION(id, task_type, direction):
    
    if direction == "up":
        task_list = GET_ALL_SCHEDULER_TASKS_BY_TYPE(task_type)
        task_list = task_list[::-1]
        
        for task in task_list:  
            if task.id < id:
                
                new_id = task.id
                
                # change ids
                task_1 = GET_SCHEDULER_TASK_BY_ID(id)
                task_2 = GET_SCHEDULER_TASK_BY_ID(new_id)
                
                task_1.id = 99
                db.session.commit()
                
                task_2.id = id
                task_1.id = new_id
                db.session.commit()
                
                return 

    if direction == "down":
        for task in GET_ALL_SCHEDULER_TASKS_BY_TYPE(task_type):
            if task.id > id:       
                new_id = task.id
                
                # change ids
                task_1 = GET_SCHEDULER_TASK_BY_ID(id)
                task_2 = GET_SCHEDULER_TASK_BY_ID(new_id)
                
                task_1.id = 99
                db.session.commit()
                
                task_2.id = id
                task_1.id = new_id
                db.session.commit()
                
                return 
            

def DELETE_SCHEDULER_TASK(task_id):
    entry = GET_SCHEDULER_TASK_BY_ID(task_id)
    
    try:
        WRITE_LOGFILE_SYSTEM("EVENT", "Database | Scheduler | Task - " + entry.name + " | deleted")   
    except:
        pass         
    
    Scheduler_Tasks.query.filter_by(id=task_id).delete()
    db.session.commit()


""" ################### """
""" ################### """
"""     sensordata      """
""" ################### """
""" ################### """


def GET_SENSORDATA_JOB_BY_ID(id):
    return Sensordata_Jobs.query.filter_by(id=id).first()


def GET_SENSORDATA_JOB_BY_NAME(name):
    return Sensordata_Jobs.query.filter_by(name=name).first()


def GET_ALL_SENSORDATA_JOBS():
    return Sensordata_Jobs.query.all()
    

def FIND_SENSORDATA_JOB_INPUT(incoming_ieeeAddr):
    entries = Sensordata_Jobs.query.all()
    
    list_jobs = []

    for entry in entries:
        if entry.mqtt_device.ieeeAddr == incoming_ieeeAddr and entry.always_active == "checked":
            list_jobs.append(entry.id)

    return list_jobs


def ADD_SENSORDATA_JOB(name, filename):
    # name exist ?
    check_entry = Sensordata_Jobs.query.filter_by(name=name).first()
    if check_entry is None:        
        # find a unused id
        for i in range(1,26):
            if Sensordata_Jobs.query.filter_by(id=i).first():
                pass
            else:
                # add the new job
                sensordata_job = Sensordata_Jobs(
                        id             = i,
                        name           = name,
                        filename       = filename,              
                    )
                db.session.add(sensordata_job)
                db.session.commit()

                WRITE_LOGFILE_SYSTEM("EVENT", "Database | Sensordata Job - " + name + " | added")                    
                return ""

        return "Job-Limit erreicht (25)"

    else:
        return "Name bereits vergeben"


def SET_SENSORDATA_JOB(id, name, filename, mqtt_device_ieeeAddr, sensor_key, always_active):        
    entry = Sensordata_Jobs.query.filter_by(id=id).first()
    old_name = entry.name

    # values changed?
    if (entry.name != name or entry.filename != filename or entry.mqtt_device_ieeeAddr != mqtt_device_ieeeAddr or 
        entry.sensor_key != sensor_key or entry.always_active != always_active):

        entry.name = name
        entry.filename = filename
        entry.mqtt_device_ieeeAddr = mqtt_device_ieeeAddr
        entry.sensor_key = sensor_key
        entry.always_active = always_active
        db.session.commit()    

        WRITE_LOGFILE_SYSTEM("EVENT", "Database | Sensordata Job - " + entry.name + " | changed || Name - " + entry.name + 
                             " | Filename - " +  entry.filename + 
                             " | MQTT-Device - " + entry.mqtt_device.name + 
                             " | Sensor - " + entry.sensor_key + 
                             " | Always_Active - " + entry.always_active)    


def CHANGE_SENSORDATA_JOBS_POSITION(id, direction):
    
    if direction == "up":
        sensordata_jobs_list = GET_ALL_SENSORDATA_JOBS()
        sensordata_jobs_list = sensordata_jobs_list[::-1]
        
        for sensordata_job in sensordata_jobs_list:
            
            if sensordata_job.id < id:  
                new_id = sensordata_job.id
                
                # change ids
                sensordata_job_1 = GET_SENSORDATA_JOB_BY_ID(id)
                sensordata_job_2 = GET_SENSORDATA_JOB_BY_ID(new_id)
                
                sensordata_job_1.id = 99
                db.session.commit()
                
                sensordata_job_2.id = id
                sensordata_job_1.id = new_id
                db.session.commit()
                
                return 

    if direction == "down":
        for sensordata_job in GET_ALL_SENSORDATA_JOBS():
            if sensordata_job.id > id:    
                new_id = sensordata_job.id
                
                # change ids
                sensordata_job_1 = GET_SENSORDATA_JOB_BY_ID(id)
                sensordata_job_2 = GET_SENSORDATA_JOB_BY_ID(new_id)
                
                sensordata_job_1.id = 99
                db.session.commit()
                
                sensordata_job_2.id = id
                sensordata_job_1.id = new_id
                db.session.commit()
                
                return 


def DELETE_SENSORDATA_JOB(id):
    entry = GET_SENSORDATA_JOB_BY_ID(id)
    
    try:
        WRITE_LOGFILE_SYSTEM("EVENT", "Database | Sensordata Job - " + entry.name + " | deleted")
    except:
        pass     
 
    Sensordata_Jobs.query.filter_by(id=id).delete()
    db.session.commit()


""" ################### """
""" ################### """
"""      snowboy        """
""" ################### """
""" ################### """


def GET_SNOWBOY_SETTINGS():
    return Snowboy_Settings.query.filter_by().first()
    

def SET_SNOWBOY_SETTINGS(sensitivity, timeout, microphone):
    entry = Snowboy_Settings.query.filter_by().first()
    entry.sensitivity = sensitivity
    entry.timeout     = timeout
    entry.microphone  = microphone
    db.session.commit() 


""" ############################# """
""" ############################# """
"""  speech recognition provider  """
""" ############################# """
""" ############################# """


def GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS():
    return Speech_Recognition_Provider_Settings.query.filter_by().first()
    
    

def SET_SPEECH_RECOGNITION_PROVIDER_SETTINGS(snowboy_hotword, speech_recognition_provider, speech_recognition_provider_username, speech_recognition_provider_key):
    entry = Speech_Recognition_Provider_Settings.query.filter_by().first()
    entry.snowboy_hotword                      = snowboy_hotword
    entry.speech_recognition_provider          = speech_recognition_provider
    entry.speech_recognition_provider_username = speech_recognition_provider_username
    entry.speech_recognition_provider_key      = speech_recognition_provider_key
    db.session.commit() 


def GET_SPEECH_RECOGNITION_PROVIDER_TASK_BY_TASK(task):
    return Speech_Recognition_Provider_Tasks.query.filter_by(task=task).first()


def GET_SPEECH_RECOGNITION_PROVIDER_TASK_BY_ID(id):
    return Speech_Recognition_Provider_Tasks.query.filter_by(id=id).first()


def GET_ALL_SPEECH_RECOGNITION_PROVIDER_TASKS():
    return Speech_Recognition_Provider_Tasks.query.all()


def ADD_SPEECH_RECOGNITION_PROVIDER_TASK(task, keywords, parameters):
    # name exist ?
    check_entry = Speech_Recognition_Provider_Tasks.query.filter_by(task=task).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,26):
            if Speech_Recognition_Provider_Tasks.query.filter_by(id=i).first():
                pass
            else:
                # add the new task
                new_task = Speech_Recognition_Provider_Tasks(
                        id         = i,
                        task       = task,
                        keywords   = keywords,
                        parameters = parameters,
                    )
                db.session.add(new_task)
                db.session.commit()
  
                WRITE_LOGFILE_SYSTEM("EVENT", "Database | Speech Control Task - " + task + " | added") 
  
                return ""

        return "Aufgabenlimit erreicht (25)"

    else:
        return "Aufgabe bereits vorhanden"


def SET_SPEECH_RECOGNITION_PROVIDER_TASK_KEYWORDS(id, keywords):
    entry = Speech_Recognition_Provider_Tasks.query.filter_by(id=id).first()

    # values changed ?
    if (entry.keywords != keywords):
        
        entry.keywords = keywords
        db.session.commit()
        
        WRITE_LOGFILE_SYSTEM("EVENT", "Database | Speech Control Task - " + entry.task + " | Keywords changed || Keywords - " + 
                             entry.keywords)


""" ################### """
""" ################### """
"""   user management   """
""" ################### """
""" ################### """


def GET_USER_BY_ID(user_id):
    return User.query.get(int(user_id))


def GET_USER_BY_NAME(user_name):
    return User.query.filter_by(username=user_name).first()


def GET_EMAIL(email):
    return User.query.filter_by(email=email).first()


def GET_ALL_USERS():
    return User.query.all()


def ADD_USER(user_name, email, password):
    new_user = User(username=user_name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    WRITE_LOGFILE_SYSTEM("EVENT", "Database | User - " + user_name + " | added") 


def SET_USER_SETTINGS(id, username, email, role, email_notification_info, email_notification_error, email_notification_camera):
    entry = User.query.filter_by(id=id).first()
    old_username = entry.username

    # values changed ?
    if (entry.username != username or entry.email != email or entry.role != role or
        entry.email_notification_info   != email_notification_info or
        entry.email_notification_error  != email_notification_error or
        entry.email_notification_camera != email_notification_camera):

        entry.username = username
        entry.email = email
        entry.role = role
        entry.email_notification_info   = email_notification_info
        entry.email_notification_error  = email_notification_error
        entry.email_notification_camera = email_notification_camera
        db.session.commit()
        
        WRITE_LOGFILE_SYSTEM("EVENT", "Database | User - " + old_username + " | changed || Username - " + entry.username +
                             " | eMail - " + entry.email + 
                             " | Role - " + role + 
                             " | eMail-Info - " + email_notification_info +
                             " | eMail-Error - " + email_notification_error +
                             " | eMail-Camera - " + email_notification_camera)


def CHANGE_USER_POSITION(id, direction):
    
    if direction == "up":
        users_list = GET_ALL_USERS()
        users_list = users_list[::-1]
        
        for user in users_list:
            
            if user.id < id:     
                new_id = user.id
                
                # change ids
                user_1 = GET_USER_BY_ID(id)
                user_2 = GET_USER_BY_ID(new_id)
                
                user_1.id = 99
                db.session.commit()
                
                user_2.id = id
                user_1.id = new_id
                db.session.commit()
                
                return 

    if direction == "down":
        for user in GET_ALL_USERS():
            if user.id > id:       
                new_id = user.id
                
                # change ids
                user_1 = GET_USER_BY_ID(id)
                user_2 = GET_USER_BY_ID(new_id)
                
                user_1.id = 99
                db.session.commit()
                
                user_2.id = id
                user_1.id = new_id
                db.session.commit()
                
                return 


def DELETE_USER(user_id):
    entry = GET_USER_BY_ID(user_id)

    try:
        WRITE_LOGFILE_SYSTEM("EVENT", "Database | User - " + entry.username + " | deleted")    
    except:
        pass
    
    User.query.filter_by(id=user_id).delete()
    db.session.commit()


""" ################### """
""" ################### """
"""     zigbee2mqtt     """
""" ################### """
""" ################### """

    
def GET_ZIGBEE2MQTT_PAIRING():
    return ZigBee2MQTT.query.filter_by().first().pairing


def SET_ZIGBEE2MQTT_PAIRING(setting):
    entry = ZigBee2MQTT.query.filter_by().first()
    entry.pairing = setting
    db.session.commit()
