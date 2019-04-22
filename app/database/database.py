from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
import re
import time
import datetime

from app import app
from app.components.file_management import WRITE_LOGFILE_SYSTEM, GET_CONFIG_DATABASE

app.config['SQLALCHEMY_DATABASE_URI'] = GET_CONFIG_DATABASE()
db = SQLAlchemy(app)


""" ###################### """
""" ###################### """
""" define table structure """
""" ###################### """
""" ###################### """

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
    __tablename__ = 'led_groups'
    id            = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name          = db.Column(db.String(50), unique = True)
    led_id_1      = db.Column(db.Integer)
    led_name_1    = db.Column(db.String(50))
    active_led_2  = db.Column(db.String(50))
    led_id_2      = db.Column(db.Integer)
    led_name_2    = db.Column(db.String(50))
    active_led_3  = db.Column(db.String(50))
    led_id_3      = db.Column(db.Integer)
    led_name_3    = db.Column(db.String(50))
    active_led_4  = db.Column(db.String(50))
    led_id_4      = db.Column(db.Integer)
    led_name_4    = db.Column(db.String(50))
    active_led_5  = db.Column(db.String(50))
    led_id_5      = db.Column(db.Integer)
    led_name_5    = db.Column(db.String(50))      
    active_led_6  = db.Column(db.String(50))
    led_id_6      = db.Column(db.Integer)
    led_name_6    = db.Column(db.String(50))
    active_led_7  = db.Column(db.String(50))
    led_id_7      = db.Column(db.Integer)
    led_name_7    = db.Column(db.String(50))
    active_led_8  = db.Column(db.String(50))
    led_id_8      = db.Column(db.Integer)
    led_name_8    = db.Column(db.String(50))
    active_led_9  = db.Column(db.String(50))
    led_id_9      = db.Column(db.Integer)
    led_name_9    = db.Column(db.String(50))  

class LED_Programs(db.Model):
    __tablename__ = 'led_programs'
    id      = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name    = db.Column(db.String(50), unique = True)
    content = db.Column(db.Text)

class LED_Scenes(db.Model):
    __tablename__ = 'led_scenes'
    id                = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name              = db.Column(db.String(50), unique = True) 
    red_1             = db.Column(db.Integer, server_default=("0"))
    green_1           = db.Column(db.Integer, server_default=("0"))
    blue_1            = db.Column(db.Integer, server_default=("0"))
    brightness_1      = db.Column(db.Integer, server_default=("254"))
    active_setting_2  = db.Column(db.String(50))
    red_2             = db.Column(db.Integer, server_default=("0"))
    green_2           = db.Column(db.Integer, server_default=("0"))
    blue_2            = db.Column(db.Integer, server_default=("0"))
    brightness_2      = db.Column(db.Integer, server_default=("254"))
    active_setting_3  = db.Column(db.String(50))
    red_3             = db.Column(db.Integer, server_default=("0"))
    green_3           = db.Column(db.Integer, server_default=("0"))
    blue_3            = db.Column(db.Integer, server_default=("0"))
    brightness_3      = db.Column(db.Integer, server_default=("254"))
    active_setting_4  = db.Column(db.String(50))
    red_4             = db.Column(db.Integer, server_default=("0"))
    green_4           = db.Column(db.Integer, server_default=("0"))
    blue_4            = db.Column(db.Integer, server_default=("0"))
    brightness_4      = db.Column(db.Integer, server_default=("254"))
    active_setting_5  = db.Column(db.String(50))
    red_5             = db.Column(db.Integer, server_default=("0"))
    green_5           = db.Column(db.Integer, server_default=("0"))
    blue_5            = db.Column(db.Integer, server_default=("0"))
    brightness_5      = db.Column(db.Integer, server_default=("254"))        
    active_setting_6  = db.Column(db.String(50))
    red_6             = db.Column(db.Integer, server_default=("0"))
    green_6           = db.Column(db.Integer, server_default=("0"))
    blue_6            = db.Column(db.Integer, server_default=("0"))
    brightness_6      = db.Column(db.Integer, server_default=("254"))
    active_setting_7  = db.Column(db.String(50))
    red_7             = db.Column(db.Integer, server_default=("0"))
    green_7           = db.Column(db.Integer, server_default=("0"))
    blue_7            = db.Column(db.Integer, server_default=("0"))
    brightness_7      = db.Column(db.Integer, server_default=("254"))
    active_setting_8  = db.Column(db.String(50))
    red_8             = db.Column(db.Integer, server_default=("0"))
    green_8           = db.Column(db.Integer, server_default=("0"))
    blue_8            = db.Column(db.Integer, server_default=("0"))
    brightness_8      = db.Column(db.Integer, server_default=("254"))
    active_setting_9  = db.Column(db.String(50))
    red_9             = db.Column(db.Integer, server_default=("0"))
    green_9           = db.Column(db.Integer, server_default=("0"))
    blue_9            = db.Column(db.Integer, server_default=("0"))
    brightness_9      = db.Column(db.Integer, server_default=("254"))   

class MQTT_Devices(db.Model):
    __tablename__ = 'mqtt_devices'
    id           = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name         = db.Column(db.String(50), unique=True)
    gateway      = db.Column(db.String(50)) 
    ieeeAddr     = db.Column(db.String(50))  
    model        = db.Column(db.String(50))
    inputs       = db.Column(db.String(200))
    outputs      = db.Column(db.String(200))
    last_contact = db.Column(db.String(50))

class Plants(db.Model):
    __tablename__  = 'plants'
    id             = db.Column(db.Integer, primary_key=True, autoincrement = True)   
    name           = db.Column(db.String(50), unique=True)
    mqtt_device_id = db.Column(db.Integer, db.ForeignKey('mqtt_devices.id'))   
    watervolume    = db.Column(db.Integer)
    mqtt_device    = db.relationship('MQTT_Devices')  
    pump_key       = db.Column(db.String(50))
    sensor_key     = db.Column(db.String(50))
    control_sensor = db.Column(db.String(50))     

class Scheduler_Time_Tasks(db.Model):
    __tablename__ = 'scheduler_time_tasks'
    id     = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name   = db.Column(db.String(50), unique=True)
    day    = db.Column(db.String(50))
    hour   = db.Column(db.String(50))
    minute = db.Column(db.String(50))
    task   = db.Column(db.String(100))
    repeat = db.Column(db.String(50))

class Scheduler_Sensor_Tasks(db.Model):
    __tablename__ = 'scheduler_sensor_tasks'
    id                   = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name                 = db.Column(db.String(50), unique=True)
    task                 = db.Column(db.String(100))          
    mqtt_device_id_1     = db.Column(db.Integer)  
    mqtt_device_name_1   = db.Column(db.String(50)) 
    mqtt_device_inputs_1 = db.Column(db.String(100)) 
    sensor_key_1         = db.Column(db.String(50))    
    value_1              = db.Column(db.String(100), server_default=(""))
    operator_1           = db.Column(db.String(50))
    operator_main_1      = db.Column(db.String(50))     
    mqtt_device_id_2     = db.Column(db.Integer) 
    mqtt_device_name_2   = db.Column(db.String(50))        
    mqtt_device_inputs_2 = db.Column(db.String(100)) 
    sensor_key_2         = db.Column(db.String(50))    
    value_2              = db.Column(db.String(100), server_default=(""))
    operator_2           = db.Column(db.String(50))   
    operator_main_2      = db.Column(db.String(50))     
    mqtt_device_id_3     = db.Column(db.Integer) 
    mqtt_device_name_3   = db.Column(db.String(50))        
    mqtt_device_inputs_3 = db.Column(db.String(100)) 
    sensor_key_3         = db.Column(db.String(50))    
    value_3              = db.Column(db.String(100), server_default=(""))
    operator_3           = db.Column(db.String(50))   

class Sensordata_Jobs(db.Model):
    __tablename__  = 'sensordata_jobs'
    id               = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name             = db.Column(db.String(50), unique=True)
    filename         = db.Column(db.String(50))
    mqtt_device_id   = db.Column(db.Integer, db.ForeignKey('mqtt_devices.id'))   
    mqtt_device      = db.relationship('MQTT_Devices')  
    sensor_key       = db.Column(db.String(50)) 
    always_active    = db.Column(db.String(50))

class Snowboy_Settings(db.Model):
    __tablename__ = 'snowboy_settings'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    sensitivity = db.Column(db.Integer)
    delay       = db.Column(db.Integer)

class Snowboy_Tasks(db.Model):
    __tablename__ = 'snowboy_tasks'
    id   = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name = db.Column(db.String(50), unique = True)
    task = db.Column(db.String(100))

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

    setting_snowboy = Global_Settings(
        setting_name  = "snowboy",
        setting_value = "False",
    )
    db.session.add(setting_snowboy)    
    db.session.commit()


# create default snowboy settings
if Snowboy_Settings.query.filter_by().first() is None:
    snowboy = Snowboy_Settings(
        sensitivity  = 45,
        delay = 3,
    )
    db.session.add(snowboy)
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
    
    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> eMail Server Settings >>> changed")
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
"""     led groups      """
""" ################### """
""" ################### """


def GET_ALL_LED_GROUPS():
    return LED_Groups.query.all()   


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
            for i in range(1,25):
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

                    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> LED Group >>> " + name + " >>> added")  

                    return ""
    else:
        return "Name bereits vergeben"


def SET_LED_GROUP(id, name, led_id_1, led_name_1,
                            led_id_2, led_name_2,
                            led_id_3, led_name_3,
                            led_id_4, led_name_4,
                            led_id_5, led_name_5,
                            led_id_6, led_name_6,
                            led_id_7, led_name_7,
                            led_id_8, led_name_8,
                            led_id_9, led_name_9):

    entry = LED_Groups.query.filter_by(id=id).first()
    entry.name = name
    
    entry.led_id_1 = led_id_1
    entry.led_name_1 = led_name_1
    entry.led_id_2 = led_id_2
    entry.led_name_2 = led_name_2
    entry.led_id_3 = led_id_3
    entry.led_name_3 = led_name_3
    entry.led_id_4 = led_id_4
    entry.led_name_4 = led_name_4
    entry.led_id_5 = led_id_5
    entry.led_name_5 = led_name_5
    entry.led_id_6 = led_id_6
    entry.led_name_6 = led_name_6
    entry.led_id_7 = led_id_7
    entry.led_name_7 = led_name_7
    entry.led_id_8 = led_id_8
    entry.led_name_8 = led_name_8
    entry.led_id_9 = led_id_9
    entry.led_name_9 = led_name_9     
       
    db.session.commit()  


def UPDATE_LED_GROUP_LED_NAMES():
    groups = GET_ALL_LED_GROUPS()
    
    for group in groups:
        
        entry = LED_Groups.query.filter_by(id=group.id).first()
        
        try:
            entry.led_name_1 = GET_MQTT_DEVICE_BY_ID(entry.led_id_1).name
        except:
            pass
        try:
            entry.led_name_2 = GET_MQTT_DEVICE_BY_ID(entry.led_id_2).name 
        except:
            pass
        try:
            entry.led_name_3 = GET_MQTT_DEVICE_BY_ID(entry.led_id_3).name
        except:
            pass
        try:
            entry.led_name_4 = GET_MQTT_DEVICE_BY_ID(entry.led_id_4).name
        except:
            pass
        try:
            entry.led_name_5 = GET_MQTT_DEVICE_BY_ID(entry.led_id_5).name
        except:
            pass
        try:
            entry.led_name_6 = GET_MQTT_DEVICE_BY_ID(entry.led_id_6).name
        except:
            pass
        try:
            entry.led_name_7 = GET_MQTT_DEVICE_BY_ID(entry.led_id_7).name
        except:
            pass
        try:
            entry.led_name_8 = GET_MQTT_DEVICE_BY_ID(entry.led_id_8).name    
        except:
            pass
        try:
            entry.led_name_9 = GET_MQTT_DEVICE_BY_ID(entry.led_id_9).name
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


def LED_CHECK_EXIST(id):
    led_list = []

    entry = LED_Groups.query.filter_by(id=id).first()

    led_list.append(entry.led_id_1)
    led_list.append(entry.led_id_2)
    led_list.append(entry.led_id_3)
    led_list.append(entry.led_id_4)
    led_list.append(entry.led_id_5)
    led_list.append(entry.led_id_6)
    led_list.append(entry.led_id_7)
    led_list.append(entry.led_id_8)
    led_list.append(entry.led_id_9)

    return led_list


def REMOVE_LED_GROUP_LED(id, led):
    entry = LED_Groups.query.filter_by(id=id).first()

    if led == 2:
        entry.active_led_2 = "None"
        entry.led_id_2     = "None"
        entry.led_name_2   = "None"
    if led == 3:
        entry.active_led_3 = "None"     
        entry.led_id_3     = "None"
        entry.led_name_3   = "None" 
    if led == 4:
        entry.active_led_4 = "None"
        entry.led_id_4     = "None"
        entry.led_name_4   = "None"
    if led == 5:
        entry.active_led_5 = "None"
        entry.led_id_5     = "None"
        entry.led_name_5   = "None" 
    if led == 6:
        entry.active_led_6 = "None"
        entry.led_id_6     = "None"
        entry.led_name_6   = "None"
    if led == 7:
        entry.active_led_7 = "None"
        entry.led_id_7     = "None"
        entry.led_name_7   = "None"
    if led == 8:
        entry.active_led_8 = "None"
        entry.led_id_8     = "None"
        entry.led_name_8   = "None"
    if led == 9:
        entry.active_led_9 = "None"
        entry.led_id_9     = "None"
        entry.led_name_9   = "None"

    db.session.commit()


def DELETE_LED_GROUP(id):
    name = GET_LED_GROUP_BY_ID(id).name
    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> LED Group >>> " + name + " >>> deleted")   
    
    LED_Groups.query.filter_by(id=id).delete()
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
        for i in range(1,25):
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

                WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> LED Program >>> " + name + " >>> added")  

                return ""
    else:
        return "Name bereits vergeben"


def SET_LED_PROGRAM_NAME(id, name):
    check_entry = LED_Programs.query.filter_by(name=name).first()
    if check_entry is None:
        entry = LED_Programs.query.filter_by(id=id).first()
        entry.name = name
        db.session.commit()    


def UPDATE_LED_PROGRAM(id, content):
    entry = LED_Programs.query.filter_by(id=id).update(dict(content=content))
    db.session.commit()


def DELETE_LED_PROGRAM(name):
    name = LED_Programs.query.filter_by(name=name).name
    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> LED Program >>> " + name + " >>> deleted")  

    LED_Programs.query.filter_by(name=name).delete()
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
            for i in range(1,25):
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

                    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> LED Scene >>> " + name + " >>> added")  

                    return ""
    else:
        return "Name bereits vergeben"


def SET_LED_SCENE(id, name, red_1, green_1, blue_1, brightness_1,
                            red_2, green_2, blue_2, brightness_2,
                            red_3, green_3, blue_3, brightness_3,
                            red_4, green_4, blue_4, brightness_4,
                            red_5, green_5, blue_5, brightness_5,
                            red_6, green_6, blue_6, brightness_6,
                            red_7, green_7, blue_7, brightness_7,
                            red_8, green_8, blue_8, brightness_8,
                            red_9, green_9, blue_9, brightness_9):

    entry = LED_Scenes.query.filter_by(id=id).first()
    entry.name  = name
    entry.red_1 = red_1
    entry.green_1 = green_1   
    entry.blue_1 = blue_1
    entry.brightness_1 = brightness_1
    entry.red_2 = red_2
    entry.green_2 = green_2   
    entry.blue_2 = blue_2
    entry.brightness_2 = brightness_2
    entry.red_3 = red_3
    entry.green_3 = green_3   
    entry.blue_3 = blue_3
    entry.brightness_3 = brightness_3    
    entry.red_4 = red_4
    entry.green_4 = green_4   
    entry.blue_4 = blue_4
    entry.brightness_4 = brightness_4
    entry.red_5 = red_5
    entry.green_5 = green_5   
    entry.blue_5 = blue_5
    entry.brightness_5 = brightness_5
    entry.red_6 = red_6
    entry.green_6 = green_6   
    entry.blue_6 = blue_6
    entry.brightness_6 = brightness_6
    entry.red_7 = red_7
    entry.green_7 = green_7   
    entry.blue_7 = blue_7
    entry.brightness_7 = brightness_7
    entry.red_8 = red_8
    entry.green_8 = green_8   
    entry.blue_8 = blue_8
    entry.brightness_8 = brightness_8
    entry.red_9 = red_9
    entry.green_9 = green_9   
    entry.blue_9 = blue_9
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


def REMOVE_LED_SCENE_SETTING(id, setting):
    entry = LED_Scenes.query.filter_by(id=id).first()

    if setting == 2:
        entry.active_setting_2 = "None"
        entry.red_2            = 0
        entry.green_2          = 0
        entry.blue_2           = 0
        entry.brightness_2     = 254
    if setting == 3:
        entry.active_setting_3 = "None"
        entry.red_3            = 0
        entry.green_3          = 0
        entry.blue_3           = 0
        entry.brightness_3     = 254        
    if setting == 4:
        entry.active_setting_4 = "None"
        entry.red_4            = 0
        entry.green_4          = 0
        entry.blue_4           = 0
        entry.brightness_4     = 254
    if setting == 5:
        entry.active_setting_5 = "None"
        entry.red_5            = 0
        entry.green_5          = 0
        entry.blue_5           = 0
        entry.brightness_5     = 254
    if setting == 6:
        entry.active_setting_6 = "None"
        entry.red_6            = 0
        entry.green_6          = 0
        entry.blue_6           = 0
        entry.brightness_6     = 254
    if setting == 7:
        entry.active_setting_7 = "None"
        entry.red_7            = 0
        entry.green_7          = 0
        entry.blue_7           = 0
        entry.brightness_7     = 254
    if setting == 8:
        entry.active_setting_8 = "None"
        entry.red_8            = 0
        entry.green_8          = 0
        entry.blue_8           = 0
        entry.brightness_8     = 254
    if setting == 9:
        entry.active_setting_9 = "None"
        entry.red_9            = 0
        entry.green_9          = 0
        entry.blue_9           = 0
        entry.brightness_9     = 254

    db.session.commit()
    return


def DELETE_LED_SCENE(id):
    name = GET_LED_SCENE_BY_ID(id).name
    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> LED Scene >>> " + name + " >>> deleted")   

    LED_Scenes.query.filter_by(id=id).delete()
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
    
    if selector == "mqtt" or selector == "zigbee2mqtt":
        for device in devices:
            if device.gateway == selector:
                device_list.append(device)
                
    if selector == "sensor":
        for device in devices:
            if device.inputs:
                device_list.append(device)  
                
    if selector == "watering":
        for device in devices:
            if device.inputs and device.outputs:
                device_list.append(device)    

    if selector == "led":
        for device in devices:
            if device.model == "9290012573A":
                device_list.append(device)                                 
                
    return device_list
        

def GET_MQTT_DEVICE_INPUTS_BY_ID(id):
    return MQTT_Devices.query.filter_by(id=id).first().inputs   


def ADD_MQTT_DEVICE(name, gateway, ieeeAddr, model = "", inputs = "", outputs = "", last_contact = ""):
    # path exist ?
    check_entry = MQTT_Devices.query.filter_by(ieeeAddr=ieeeAddr).first()
    if check_entry is None:       
        # find a unused id
        for i in range(1,50):
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
                        inputs       = inputs,
                        outputs      = outputs,
                        last_contact = last_contact,
                        )
                db.session.add(device)
                db.session.commit()
                
                WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> MQTT Device >>> " + name + " >>> added >>>  Gateway: " + 
                                     gateway + " /// ieeeAddr: " + ieeeAddr + " /// Model: " + model + 
                                     " /// Inputs: " + inputs + " /// Outputs: " + outputs)

                SET_MQTT_DEVICE_LAST_CONTACT(ieeeAddr)                                  
                
    else:
        SET_MQTT_DEVICE_LAST_CONTACT(ieeeAddr)  


def SET_MQTT_DEVICE_LAST_CONTACT(ieeeAddr):
    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
    entry = MQTT_Devices.query.filter_by(ieeeAddr=ieeeAddr).first()
    entry.last_contact = timestamp
    db.session.commit()       


def SET_MQTT_DEVICE(gateway, id, name, inputs = 0):

    entry = MQTT_Devices.query.filter_by(id=id).first()

    if gateway == "mqtt":

        # values changed ?
        if (entry.name != name):

            WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> MQTT Device >>> " + entry.name + " >>> changed >>> Name: " +
                                name + " /// Gateway: " + entry.gateway + " /// ieeeAddr: " + entry.ieeeAddr + 
                                " /// Model: " + entry.model + " /// Inputs: " + str(entry.inputs) + " /// Outputs: " + 
                                entry.outputs)

            entry.name = name
            db.session.commit()    


    if gateway == "zigbee2mqtt":

        # values changed ?
        if (entry.name != name or entry.inputs != inputs):
            
            entry.inputs = inputs
            
            WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> ZigBee2MQTT Device >>> " + entry.name + " >>> changed >>> Name: " +
                                name + " /// Gateway: " + entry.gateway + " /// ieeeAddr: " + entry.ieeeAddr + 
                                " /// Model: " + entry.model + " /// Inputs: " + inputs)

            entry.name = name
            db.session.commit()    


def DELETE_MQTT_DEVICE(id):
    error_list = ""

    # check plants
    entries = GET_ALL_PLANTS()
    for entry in entries:
        if entry.mqtt_device_id == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in Bewässung >>> Pflanze >>> " + entry.name     
    
    # check sensordata
    entries = GET_ALL_SENSORDATA_JOBS()
    for entry in entries:
        if entry.mqtt_device_id == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in Sensordaten >>> Job >>> " + entry.name  
        
    # check led groups
    entries = GET_ALL_LED_GROUPS()
    for entry in entries:
        if entry.led_id_1 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED >>> LED-Gruppen >>> Gruppe >>> " + entry.name  
        if entry.led_id_2 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED >>> LED-Gruppen >>> Gruppe >>> " + entry.name     
        if entry.led_id_3 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED >>> LED-Gruppen >>> Gruppe >>> " + entry.name  
        if entry.led_id_4 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED >>> LED-Gruppen >>> Gruppe >>> " + entry.name  
        if entry.led_id_5 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED >>> LED-Gruppen >>> Gruppe >>> " + entry.name  
        if entry.led_id_6 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED >>> LED-Gruppen >>> Gruppe >>> " + entry.name   
        if entry.led_id_7 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED >>> LED-Gruppen >>> Gruppe >>> " + entry.name  
        if entry.led_id_8 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED >>> LED-Gruppen >>> Gruppe >>> " + entry.name          
        if entry.led_id_9 == id:
            device = GET_MQTT_DEVICE_BY_ID(id)
            error_list = error_list + "," + device.name + " eingetragen in LED >>> LED-Gruppen >>> Gruppe >>> " + entry.name                       
       
    if error_list != "":
        error_list = error_list[1:]
        SET_ERROR_LIST(error_list)           
    else:
        entry = GET_MQTT_DEVICE_BY_ID(id)
        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> MQTT Device >>> " + entry.name + " >>> deleted")
 
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


def ADD_PLANT(name, mqtt_device_id, watervolume, control_sensor, log = ""):
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
                        id             = i,
                        name           = name,
                        mqtt_device_id = mqtt_device_id,
                        watervolume    = watervolume, 
                        control_sensor = control_sensor,                    
                    )
                db.session.add(plant)
                db.session.commit()
                
                if log == "":
                    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Plant >>> " + name + " >>> added")               
                
                return ""

    else:
        return "Name bereits vergeben"


def SET_PLANT_SETTINGS(plant_id, name, sensor_key, pump_key, watervolume, control_sensor):        
    entry = Plants.query.filter_by(id=plant_id).first()
    old_name = entry.name

    # values changed ?
    if (entry.name != name or entry.sensor_key != sensor_key or entry.pump_key != pump_key or 
        entry.watervolume != int(watervolume) or entry.control_sensor != control_sensor):

        entry.name = name
        entry.sensor_key = sensor_key
        entry.pump_key = pump_key
        entry.watervolume = watervolume
        entry.control_sensor = control_sensor
        
        db.session.commit()  

        try:
            # with pump_id
            WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Plant >>> " + old_name + " >>> changed >>> Name: " + entry.name + 
                                " /// MQTT-Device: " + entry.mqtt_device.name + " /// Sensor: " + entry.sensor_key + 
                                " /// Pump: " + entry.pump_key + " /// Watervolume: " + str(watervolume) + " /// Control-Sensor: " +
                                entry.control_sensor)      
        except:
            # without pump_id
            WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Plant >>> " + old_name + " >>> changed >>> Name: " + entry.name + 
                                " /// MQTT-Device: " + entry.mqtt_device.name + " /// Sensor: " + entry.sensor_key + 
                                " /// Watervolume: " + str(watervolume) + " /// Control-Sensor: " + entry.control_sensor)      


def DELETE_PLANT(plant_id, log = ""):
    entry = GET_PLANT_BY_ID(plant_id)

    if log == "":
        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Plant >>> " + entry.name + " >>> deleted")   
    
    Plants.query.filter_by(id=plant_id).delete()
    db.session.commit()


""" ################## """
""" ################## """
"""      scheduler     """
""" ################## """
""" ################## """


def GET_SCHEDULER_TIME_TASK_BY_NAME(name):
    return Scheduler_Time_Tasks.query.filter_by(name=name).first()


def GET_SCHEDULER_TIME_TASK_BY_ID(id):
    return Scheduler_Time_Tasks.query.filter_by(id=id).first()


def GET_ALL_SCHEDULER_TIME_TASKS():
    return Scheduler_Time_Tasks.query.all()


def ADD_SCHEDULER_TIME_TASK(name, task, day, hour, minute, repeat):
    # name exist ?
    check_entry = Scheduler_Time_Tasks.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,25):
            if Scheduler_Time_Tasks.query.filter_by(id=i).first():
                pass
            else:
                # add the new task
                new_task = Scheduler_Time_Tasks(
                        id     = i,
                        name   = name,
                        task   = task,
                        day    = day,
                        hour   = hour,
                        minute = minute,
                        repeat = repeat,
                    )
                db.session.add(new_task)
                db.session.commit()
                
                WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Scheduler >>> Time >>> " + name + " >>> added >>> Task: " + 
                                     task + " /// Day: " + day + " /// Hour: " + str(hour) + " /// Minute: " + str(minute) + 
                                     " /// Repeat: " +  repeat)                
                
                return ""
    else:
        return "Name bereits vergeben"


def SET_SCHEDULER_TIME_TASK(id, name, task, day, hour, minute, repeat):       
    entry = Scheduler_Time_Tasks.query.filter_by(id=id).first()
    old_name = entry.name

    # values changed ?
    if (entry.name != name or entry.task != task or entry.day != day or entry.hour != hour 
        or entry.minute != minute or entry.repeat != repeat):

        entry.name = name
        entry.task = task
        entry.day = day
        entry.hour = hour
        entry.minute = minute
        entry.repeat = repeat
        db.session.commit()    

        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Scheduler >>> Time >>> " + old_name + " >>> changed >>> Name: " + 
                             entry.name + " /// Task: " + entry.task + " /// Day: " + entry.day + " /// Hour: " + 
                             entry.hour + " /// Minute: " + entry.minute + " /// Repeat: " +  entry.repeat)


def DELETE_SCHEDULER_TIME_TASK(task_id):
    entry = GET_SCHEDULER_TIME_TASK_BY_ID(task_id)
    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Scheduler >>> Time >>> " + entry.name + " >>> deleted")    
    
    Scheduler_Time_Tasks.query.filter_by(id=task_id).delete()
    db.session.commit()


def GET_SCHEDULER_SENSOR_TASK_BY_NAME(name):
    return Scheduler_Sensor_Tasks.query.filter_by(name=name).first()


def GET_SCHEDULER_SENSOR_TASK_BY_ID(id):
    return Scheduler_Sensor_Tasks.query.filter_by(id=id).first()
    

def GET_ALL_SCHEDULER_SENSOR_TASKS():
    return Scheduler_Sensor_Tasks.query.all()


def FIND_SCHEDULER_SENSOR_TASK_INPUT(incoming_ieeeAddr):
    entries = Scheduler_Sensor_Tasks.query.all()
    
    list_tasks = []
    
    for entry in entries:

        try:
            # check device 1
            device_1 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_1)
            
            if (device_1.ieeeAddr == incoming_ieeeAddr or
                device_1.ieeeAddr == incoming_ieeeAddr or
                device_1.ieeeAddr == incoming_ieeeAddr):
                
                if entry.id not in list_tasks:
                    list_tasks.append(entry.id)
                    
            if (device_1.name == incoming_ieeeAddr or
                device_1.name == incoming_ieeeAddr or
                device_1.name == incoming_ieeeAddr):
                
                if entry.id not in list_tasks:
                    list_tasks.append(entry.id)        
        except:
            pass
                
        try:
            # check device 2
            device_2 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_2)
            
            if (device_2.ieeeAddr == incoming_ieeeAddr or
                device_2.ieeeAddr == incoming_ieeeAddr or
                device_2.ieeeAddr == incoming_ieeeAddr):
                
                if entry.id not in list_tasks:
                    list_tasks.append(entry.id)  
        
            if (device_2.name == incoming_ieeeAddr or
                device_2.name == incoming_ieeeAddr or
                device_2.name == incoming_ieeeAddr):
                
                if entry.id not in list_tasks:
                    list_tasks.append(entry.id)         
        except:
            pass
        
        try:
            # check device 3
            device_3 = GET_MQTT_DEVICE_BY_ID(entry.mqtt_device_id_3)
            
            if (device_3.ieeeAddr == incoming_ieeeAddr or
                device_3.ieeeAddr == incoming_ieeeAddr or
                device_3.ieeeAddr == incoming_ieeeAddr):
                
                if entry.id not in list_tasks:
                    list_tasks.append(entry.id) 
                    
            if (device_3.name == incoming_ieeeAddr or
                device_3.name == incoming_ieeeAddr or
                device_3.name == incoming_ieeeAddr):
                
                if entry.id not in list_tasks:
                    list_tasks.append(entry.id)  
        except:
            pass
            
    if list_tasks != []:
        return list_tasks
    else:
        return ""


def ADD_SCHEDULER_SENSOR_TASK(name, task, log = ""):
    check_entry = Scheduler_Sensor_Tasks.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,25):
            if Scheduler_Sensor_Tasks.query.filter_by(id=i).first():
                pass
            else:
                # add the new task
                new_task = Scheduler_Sensor_Tasks(
                        id             = i,
                        name           = name,
                        task           = task,                        
                    )
                db.session.add(new_task)
                db.session.commit()
                
                if log == "":
                    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Scheduler >>> Sensor >>> " + name + " >>> added")               
                
                return ""
    else:
        return "Name bereits vergeben"


def ADD_SCHEDULER_SENSOR_TASK_OPTION(id):
    entry = Scheduler_Sensor_Tasks.query.filter_by(id=id).first()
    operator_main_1 = entry.operator_main_1 
    operator_main_2 = entry.operator_main_2 

    if operator_main_1 == "None" or operator_main_1 == None:
        entry.operator_main_1 = "and"
        entry.operator_main_2 = "None"

    if operator_main_1 != "None" and operator_main_1 != None:
        entry.operator_main_2 = "and"

    db.session.commit()


def REMOVE_SCHEDULER_SENSOR_TASK_OPTION(id):
    entry = Scheduler_Sensor_Tasks.query.filter_by(id=id).first()
    operator_main_1 = entry.operator_main_1 
    operator_main_2 = entry.operator_main_2 

    if operator_main_2 != "None":
        entry.operator_main_2 = "None"

    if operator_main_2 == "None" or operator_main_2 == None:
        entry.operator_main_1 = "None"

    db.session.commit()


def SET_SCHEDULER_SENSOR_TASK(id, name, task, mqtt_device_id_1, mqtt_device_name_1, mqtt_device_inputs_1,  
                                                   sensor_key_1, operator_1, value_1, operator_main_1,
                                                   mqtt_device_id_2, mqtt_device_name_2, mqtt_device_inputs_2, 
                                                   sensor_key_2, operator_2, value_2, operator_main_2,
                                                   mqtt_device_id_3, mqtt_device_name_3, mqtt_device_inputs_3, 
                                                   sensor_key_3, operator_3, value_3):        
                                                                                        
    entry = Scheduler_Sensor_Tasks.query.filter_by(id=id).first()
    old_name = entry.name

    # values changed ?
    if (entry.name != name or entry.task != task or str(entry.mqtt_device_id_1) != mqtt_device_id_1 or
        entry.sensor_key_1 != sensor_key_1 or entry.operator_1 != operator_1 or entry.value_1 != value_1 or 
        str(entry.mqtt_device_id_2) != mqtt_device_id_2 or entry.sensor_key_2 != sensor_key_2 or 
        entry.operator_2 != operator_2 or entry.value_2 != value_2 or entry.operator_main_1 != operator_main_1 or
        str(entry.mqtt_device_id_3) != mqtt_device_id_3 or entry.sensor_key_3 != sensor_key_3 or 
        entry.operator_3 != operator_3 or entry.value_3 != value_3 or entry.operator_main_2 != operator_main_2):

        entry.name = name        
        entry.task = task
        entry.mqtt_device_id_1 = mqtt_device_id_1
        entry.mqtt_device_name_1 = mqtt_device_name_1
        entry.mqtt_device_inputs_1 = mqtt_device_inputs_1
        entry.sensor_key_1 = sensor_key_1
        entry.operator_1 = operator_1
        entry.value_1 = value_1
        entry.operator_main_1=operator_main_1
        entry.mqtt_device_id_2 = mqtt_device_id_2
        entry.mqtt_device_name_2 = mqtt_device_name_2
        entry.mqtt_device_inputs_2 = mqtt_device_inputs_2
        entry.sensor_key_2 = sensor_key_2
        entry.operator_2 = operator_2
        entry.value_2 = value_2        
        entry.operator_main_2=operator_main_2
        entry.mqtt_device_id_3 = mqtt_device_id_3
        entry.mqtt_device_name_3 = mqtt_device_name_3
        entry.mqtt_device_inputs_3 = mqtt_device_inputs_3
        entry.sensor_key_3 = sensor_key_3
        entry.operator_3 = operator_3
        entry.value_3 = value_3               
        db.session.commit()    

        if operator_main_1 == "not":
            WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Scheduler >>> Sensor >>> " + old_name + 
                                  " >>> changed >>> Name: " + name + " /// Task: " + task + 
                                  " /// MQTT-Device_1: " + mqtt_device_name_1 + " /// Sensor_1: " + sensor_key_1 + 
                                  " /// Operator_1: " + str(operator_1) + " /// Value_1: " +  str(value_1)) 
                                 
        if operator_main_2 == "not":
            WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Scheduler >>> Sensor >>> " + old_name + 
                                 " >>> changed >>> Name: " + name + " /// Task: " + task + 
                                 " /// MQTT-Device_1: " + mqtt_device_name_1 + " /// Sensor_1: " + sensor_key_1 + 
                                 " /// Operator_1: " + str(operator_1) + " /// Value_1: " +  str(value_1) + 
                                 " /// MQTT-Device_2: " + mqtt_device_name_2 + " /// Sensor_2: " + sensor_key_2 + 
                                 " /// Operator_2: " + str(operator_2) + " /// Value_2: " +  str(value_2))
                                   
        else:
            WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Scheduler >>> Sensor >>> " + old_name + 
                                 " >>> changed >>> Name: " + name + " /// Task: " + task + 
                                 " /// MQTT-Device_1: " + mqtt_device_name_1 + " /// Sensor_1: " + sensor_key_1 + 
                                 " /// Operator_1: " + str(operator_1) + " /// Value_1: " +  str(value_1) + 
                                 " /// MQTT-Device_2: " + mqtt_device_name_2 + " /// Sensor_2: " + sensor_key_2 + 
                                 " /// Operator_2: " + str(operator_2) + " /// Value_2: " +  str(value_2) +
                                 " /// MQTT-Device_3: " + mqtt_device_name_3 + " /// Sensor_3: " + sensor_key_3 + 
                                 " /// Operator_3: " + str(operator_3) + " /// Value_3: " +  str(value_3))


def DELETE_SCHEDULER_SENSOR_TASK(task_id, log = ""):
    entry = GET_SCHEDULER_SENSOR_TASK_BY_ID(task_id)

    if log == "":
        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Scheduler >>> Sensor >>> " + entry.name + " >>> deleted")    
    
    Scheduler_Sensor_Tasks.query.filter_by(id=task_id).delete()
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


def ADD_SENSORDATA_JOB(name, filename, mqtt_device_id, always_active, log = ""):
    # name exist ?
    check_entry = Sensordata_Jobs.query.filter_by(name=name).first()
    if check_entry is None:        
        # find a unused id
        for i in range(1,25):
            if Sensordata_Jobs.query.filter_by(id=i).first():
                pass
            else:
                # add the new job
                sensordata_job = Sensordata_Jobs(
                        id             = i,
                        name           = name,
                        filename       = filename,
                        mqtt_device_id = mqtt_device_id, 
                        always_active  = always_active,                
                    )
                db.session.add(sensordata_job)
                db.session.commit()

                if log == "":
                    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Sensordata Job >>> " + name + " >>> added")                    
             
                return ""
    else:
        return "Name bereits vergeben"


def SET_SENSORDATA_JOB(id, name, filename, mqtt_device_id, sensor_key, always_active):        
    entry = Sensordata_Jobs.query.filter_by(id=id).first()
    old_name = entry.name

    # values changed?
    if (entry.name != name or entry.filename != filename or entry.mqtt_device_id != mqtt_device_id or 
        entry.sensor_key != sensor_key or entry.always_active != always_active):

        entry.name = name
        entry.filename = filename
        entry.mqtt_device_id = mqtt_device_id
        entry.sensor_key = sensor_key
        entry.always_active = always_active
        db.session.commit()    

        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Sensordata Job >>> " + entry.name + " >>> changed >>> Name: " + 
                             entry.name + " /// Filename: " +  entry.filename + " /// MQTT-Device: " + entry.mqtt_device.name + 
                              " /// Sensor: " + entry.sensor_key + " /// Always_Active: " + entry.always_active)    


def DELETE_SENSORDATA_JOB(id, log = ""):
    entry = GET_SENSORDATA_JOB_BY_ID(id)

    print(log)

    if log == "":
        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Sensordata Job >>> " + entry.name + " >>> deleted")
 
    Sensordata_Jobs.query.filter_by(id=id).delete()
    db.session.commit()


""" ################### """
""" ################### """
"""      snowboy        """
""" ################### """
""" ################### """


def GET_SNOWBOY_SETTINGS():
    return Snowboy_Settings.query.filter_by().first()
    

def SET_SNOWBOY_SETTINGS(sensitivity, delay):
    entry = Snowboy_Settings.query.filter_by().first()
    entry.sensitivity = sensitivity
    entry.delay = delay
    db.session.commit() 


def GET_SNOWBOY_TASK_BY_NAME(name):
    return Snowboy_Tasks.query.filter_by(name=name).first()


def GET_SNOWBOY_TASK_BY_ID(id):
    return Snowboy_Tasks.query.filter_by(id=id).first()


def GET_ALL_SNOWBOY_TASKS():
    return Snowboy_Tasks.query.all()


def ADD_SNOWBOY_TASK(name, task):
    # name exist ?
    check_entry = Snowboy_Tasks.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,25):
            if Snowboy_Tasks.query.filter_by(id=i).first():
                pass
            else:
                # add the new task
                task = Snowboy_Tasks(
                        id     = i,
                        name   = name,
                        task   = task,
                    )
                db.session.add(task)
                db.session.commit()
  
                WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Snowboy Task >>> " + name + " >>> added") 
  
                return ""
    else:
        return "Name bereits vergeben"


def SET_SNOWBOY_TASK(id, name, task):
    entry = Snowboy_Tasks.query.filter_by(id=id).first()
    old_name = entry.name
    
    # values changed ?
    if (entry.name != name or entry.task != task):
        
        entry.name = name
        entry.task = task
        db.session.commit()
        
        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Snowboy Task >>> " + old_name + " >>> changed >>> Name: " +
                             entry.name + " /// Task: " + entry.task) 


def DELETE_SNOWBOY_TASK(task_id):
    entry = GET_SNOWBOY_TASK_BY_ID(task_id)
    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Snowboy Task >>> " + entry.name + " >>> deleted")    
    
    
    Snowboy_Tasks.query.filter_by(id=task_id).delete()
    db.session.commit()


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

    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> User >>> " + user_name + " >>> added") 


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
        
        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> User >>> " + old_username + " >>> changed >>> Username: " +
                             entry.username + " /// eMail: " + entry.email + " /// Role: " + role + 
                             " /// eMail-Info: " + email_notification_info +
                             " /// eMail-Error: " + email_notification_error +
                             " /// eMail-Camera: " + email_notification_camera)


def DELETE_USER(user_id):
    entry = GET_USER_BY_ID(user_id)
    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> User >>> " + entry.username + " >>> deleted")    
    
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
