from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
import re
import time
import datetime

from app import app
from app.components.file_management import WRITE_LOGFILE_SYSTEM

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/smarthome.sqlite3'
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

class HUE_Bridge(db.Model):
    __tablename__ = 'hue_bridge'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    ip = db.Column(db.String(50), unique = True)  

class LED(db.Model):
    __tablename__ = 'led'
    id      = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name    = db.Column(db.String(50), unique = True)

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
    moisture       = db.Column(db.String(50), server_default=("normal"))     

class Programs(db.Model):
    __tablename__ = 'programs'
    id      = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name    = db.Column(db.String(50), unique = True)
    content = db.Column(db.Text)

class Scenes(db.Model):
    __tablename__ = 'scenes'
    id            = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name          = db.Column(db.String(50), unique = True)
    voice_control = db.Column(db.String(50), unique = True)

class Scene_01(db.Model):
    __tablename__ = 'scene_01'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("1"))
    scene_name  = db.relationship('Scenes') 
    led_id      = db.Column(db.Integer, db.ForeignKey('led.id'), unique = True)
    led_name    = db.relationship('LED')    
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_02(db.Model):
    __tablename__ = 'scene_02'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("2"))
    scene_name  = db.relationship('Scenes')
    led_id      = db.Column(db.Integer, db.ForeignKey('led.id'), unique = True)
    led_name    = db.relationship('LED')    
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_03(db.Model):
    __tablename__ = 'scene_03'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("3"))
    scene_name  = db.relationship('Scenes')
    led_id      = db.Column(db.Integer, db.ForeignKey('led.id'), unique = True)
    led_name    = db.relationship('LED')
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_04(db.Model):
    __tablename__ = 'scene_04'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("4"))
    scene_name  = db.relationship('Scenes')
    led_id      = db.Column(db.Integer, db.ForeignKey('led.id'), unique = True)
    led_name    = db.relationship('LED')
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_05(db.Model):
    __tablename__ = 'scene_05'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("5"))
    scene_name  = db.relationship('Scenes')
    led_id      = db.Column(db.Integer, db.ForeignKey('led.id'), unique = True)
    led_name    = db.relationship('LED') 
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_06(db.Model):
    __tablename__ = 'scene_06'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("6"))
    scene_name  = db.relationship('Scenes')
    led_id      = db.Column(db.Integer, db.ForeignKey('led.id'), unique = True)
    led_name    = db.relationship('LED')    
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_07(db.Model):
    __tablename__ = 'scene_07'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("7"))
    scene_name  = db.relationship('Scenes')
    led_id      = db.Column(db.Integer, db.ForeignKey('led.id'), unique = True)
    led_name    = db.relationship('LED')
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_08(db.Model):
    __tablename__ = 'scene_08'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("8"))
    scene_name  = db.relationship('Scenes')
    led_id      = db.Column(db.Integer, db.ForeignKey('led.id'), unique = True)
    led_name    = db.relationship('LED')
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_09(db.Model):
    __tablename__ = 'scene_09'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("9"))
    scene_name  = db.relationship('Scenes')
    led_id      = db.Column(db.Integer, db.ForeignKey('led.id'), unique = True)
    led_name    = db.relationship('LED') 
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_10(db.Model):
    __tablename__ = 'scene_10'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("10"))
    scene_name  = db.relationship('Scenes')
    led_id      = db.Column(db.Integer, db.ForeignKey('led.id'), unique = True)
    led_name    = db.relationship('LED') 
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_99(db.Model):
    __tablename__ = 'scene_99'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("99"))
    scene_name  = db.relationship('Scenes')
    led_id      = db.Column(db.Integer, db.ForeignKey('led.id'), unique = True)
    led_name    = db.relationship('LED') 
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Sensordata_Jobs(db.Model):
    __tablename__  = 'sensordata_jobs'
    id               = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name             = db.Column(db.String(50), unique=True)
    filename         = db.Column(db.String(50))
    mqtt_device_id   = db.Column(db.Integer, db.ForeignKey('mqtt_devices.id'))   
    mqtt_device      = db.relationship('MQTT_Devices')  
    sensor_key       = db.Column(db.String(50)) 
    always_active    = db.Column(db.String(50))

class Settings(db.Model):
    __tablename__ = 'settings'
    id            = db.Column(db.Integer, primary_key=True, autoincrement = True)
    setting_name  = db.Column(db.String(50), unique=True)
    setting_value = db.Column(db.String(50))   

class Snowboy(db.Model):
    __tablename__ = 'snowboy'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    sensitivity = db.Column(db.Integer)

class Snowboy_Tasks(db.Model):
    __tablename__ = 'snowboy_tasks'
    id   = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name = db.Column(db.String(50), unique = True)
    task = db.Column(db.String(100))

class Taskmanagement_Time(db.Model):
    __tablename__ = 'taskmanagement_time'
    id     = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name   = db.Column(db.String(50), unique=True)
    day    = db.Column(db.String(50))
    hour   = db.Column(db.String(50))
    minute = db.Column(db.String(50))
    task   = db.Column(db.String(100))
    repeat = db.Column(db.String(50))

class Taskmanagement_Sensor(db.Model):
    __tablename__ = 'taskmanagement_sensor'
    id             = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name           = db.Column(db.String(50), unique=True)
    task           = db.Column(db.String(100))
    mqtt_device_id = db.Column(db.Integer, db.ForeignKey('mqtt_devices.id'))   
    mqtt_device    = db.relationship('MQTT_Devices')  
    sensor_key     = db.Column(db.String(50))    
    value          = db.Column(db.String(100))
    operator       = db.Column(db.String(50))
    settings       = db.Column(db.String(200))

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

class ZigBee(db.Model):
    __tablename__ = 'zigbee'
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


# create default scenes
if Scenes.query.filter_by().first() is None:   
    for i in range(1,11):
        scene = Scenes(
            id   = i,
            name = "",
        )        
        db.session.add(scene)
        db.session.commit()

    scene = Scenes(
        id   = 99,
        name = "",
    )        
    db.session.add(scene)
    db.session.commit()


# create default settings
if Settings.query.filter_by().first() is None:
    setting = Settings(
        setting_name  = "hue_bridge",
        setting_value = "False",
    )
    db.session.add(setting)
    db.session.commit()

    setting = Settings(
        setting_name  = "mqtt",
        setting_value = "False",
    )
    db.session.add(setting)    
    db.session.commit()
    
    setting = Settings(
        setting_name  = "zigbee",
        setting_value = "False",
    )
    db.session.add(setting)    
    db.session.commit()

    setting = Settings(
        setting_name  = "snowboy",
        setting_value = "False",
    )
    db.session.add(setting)    
    db.session.commit()


# create default snowboy
if Snowboy.query.filter_by().first() is None:
    snowboy = Snowboy(
        sensitivity  = "45",
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


# create default zigbee
if ZigBee.query.filter_by().first() is None:
    zigbee = ZigBee(
        pairing = "False",
    )
    db.session.add(zigbee)
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
"""         led         """
""" ################### """
""" ################### """


def GET_DROPDOWN_LIST_LED():
    entry_list = []
    # get all led entries
    entries = LED.query.all()
    for entry in entries:
        # select the led names only
        entry_list.append(entry.name)

    return entry_list


def GET_ALL_LEDS():
    return LED.query.all()


def UPDATE_LED(led_list):
    try:
        for i in range (len(led_list)):
            # check entries and replace them if nessessary
            try:
                check_entry = LED.query.filter_by(id=i+1).first()
                if check_entry.name is not led_list[i]:
                    check_entry.name = led_list[i]
            # add new entires, if they not exist
            except:
                led = LED(
                    id = i + 1,
                    name = led_list[i],
                )    
                db.session.add(led)     

            db.session.commit()  
    except:
        return False    


def ADD_LED(Scene, Name):
    # search for the selected LED entry 
    entry = LED.query.filter_by(name=Name).first() 

    if Scene == 1:
        # LED already exist ?
        check_entry = Scene_01.query.filter_by(led_id=entry.id).first()
        # add new led
        if check_entry is None:
            scene = Scene_01(
                led_id = entry.id,
            )
    if Scene == 2:
        check_entry = Scene_02.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_02(
                led_id = entry.id,
            )
    if Scene == 3:
        check_entry = Scene_03.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_03(
                led_id = entry.id,
            )
    if Scene == 4:
        check_entry = Scene_04.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_04(
                led_id = entry.id,
            )
    if Scene == 5:
        check_entry = Scene_05.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_05(
                led_id = entry.id,
            )      
    if Scene == 6:
        check_entry = Scene_06.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_06(
                led_id = entry.id,
            )
    if Scene == 7:
        check_entry = Scene_07.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_07(
                led_id = entry.id,
            )
    if Scene == 8:
        check_entry = Scene_08.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_08(
                led_id = entry.id,
            )
    if Scene == 9:
        check_entry = Scene_09.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_09(
                led_id = entry.id,
            )      
    if Scene == 10:
        check_entry = Scene_10.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_10(
                led_id = entry.id,
            )  
    if Scene == 99:
        check_entry = Scene_99.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_99(
                led_id = entry.id,
            )  
    try:        
        db.session.add(scene)
        db.session.commit()        
    except:
        pass    


def DEL_LED(Scene, ID): 
    if Scene == 1:
        Scene_01.query.filter_by(led_id=ID).delete()
        if Scene_01.query.filter_by().first() is None:
            entry = Scenes.query.get(Scene)
            entry.name = ""
    if Scene == 2:
        Scene_02.query.filter_by(led_id=ID).delete()
        if Scene_02.query.filter_by().first() is None:
            entry = Scenes.query.get(Scene)
            entry.name = ""
    if Scene == 3:
        Scene_03.query.filter_by(led_id=ID).delete()
        if Scene_03.query.filter_by().first() is None:
            entry = Scenes.query.get(Scene)
            entry.name = ""
    if Scene == 4:
        Scene_04.query.filter_by(led_id=ID).delete()
        if Scene_04.query.filter_by().first() is None:
            entry = Scenes.query.get(Scene)
            entry.name = ""
    if Scene == 5:
        Scene_05.query.filter_by(led_id=ID).delete()
        if Scene_05.query.filter_by().first() is None:
            entry = Scenes.query.get(Scene)
            entry.name = ""
    if Scene == 6:
        Scene_06.query.filter_by(led_id=ID).delete()
        if Scene_06.query.filter_by().first() is None:
            entry = Scenes.query.get(Scene)
            entry.name = ""
    if Scene == 7:
        Scene_07.query.filter_by(led_id=ID).delete()
        if Scene_07.query.filter_by().first() is None:
            entry = Scenes.query.get(Scene)
            entry.name = ""
    if Scene == 8:
        Scene_08.query.filter_by(led_id=ID).delete()
        if Scene_08.query.filter_by().first() is None:
            entry = Scenes.query.get(Scene)
            entry.name = ""
    if Scene == 9:
        Scene_09.query.filter_by(led_id=ID).delete()
        if Scene_09.query.filter_by().first() is None:
            entry = Scenes.query.get(Scene)
            entry.name = ""
    if Scene == 10:
        Scene_10.query.filter_by(led_id=ID).delete()
        if Scene_10.query.filter_by().first() is None:
            entry = Scenes.query.get(Scene)
            entry.name = ""
    if Scene == 99:
        Scene_99.query.filter_by(led_id=ID).delete()
        if Scene_99.query.filter_by().first() is None:
            entry = Scenes.query.get(Scene)
            entry.name = ""

    db.session.commit()


""" ################### """
""" ################### """
"""    led programs     """
""" ################### """
""" ################### """


def GET_ALL_PROGRAMS():
    return Programs.query.all()   


def GET_PROGRAM_BY_NAME(name):
    return Programs.query.filter_by(name=name).first()


def GET_PROGRAM_BY_ID(id):
    return Programs.query.filter_by(id=id).first()


def NEW_PROGRAM(name):
    # name exist ?
    check_entry = Programs.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,25):
            if Programs.query.filter_by(id=i).first():
                pass
            else:
                # add the new program
                program = Programs(
                        id = i,
                        name = name,
                        content = "",
                    )
                db.session.add(program)
                db.session.commit()
                return ("")
    else:
        return ("Name bereits vergeben")


def SET_PROGRAM_NAME(id, name):
    check_entry = Programs.query.filter_by(name=name).first()
    if check_entry is None:
        entry = Programs.query.filter_by(id=id).first()
        entry.name = name
        db.session.commit()    


def UPDATE_PROGRAM(id, content):
    entry = Programs.query.filter_by(id=id).update(dict(content=content))
    db.session.commit()


def DELETE_PROGRAM(name):
    Programs.query.filter_by(name=name).delete()
    db.session.commit() 


""" ################### """
""" ################### """
"""    led scenes     """
""" ################### """
""" ################### """


def GET_SCENE(Scene):
    entries = None
    name    = None
    if Scene == 1:
        # scene exist ?
        if Scene_01.query.all():
            # get all settings
            entries = Scene_01.query.all()
            # get the scene name of an other table
            name = entries[0].scene_name.name
    if Scene == 2:
        if Scene_02.query.all():
            entries = Scene_02.query.all()
            name = entries[0].scene_name.name
    if Scene == 3:
        if Scene_03.query.all():
            entries = Scene_03.query.all()
            name = entries[0].scene_name.name
    if Scene == 4:
        if Scene_04.query.all():
            entries = Scene_04.query.all()  
            name = entries[0].scene_name.name
    if Scene == 5:
        if Scene_05.query.all():
            entries = Scene_05.query.all()
            name = entries[0].scene_name.name
    if Scene == 6:
        if Scene_06.query.all():
            entries = Scene_06.query.all()
            name = entries[0].scene_name.name
    if Scene == 7:
        if Scene_07.query.all():
            entries = Scene_07.query.all()
            name = entries[0].scene_name.name
    if Scene == 8:
        if Scene_08.query.all():
            entries = Scene_08.query.all()  
            name = entries[0].scene_name.name
    if Scene == 9:
        if Scene_09.query.all():
            entries = Scene_09.query.all()
            name = entries[0].scene_name.name
    if Scene == 10:
        if Scene_10.query.all():
            entries = Scene_10.query.all()
            name = entries[0].scene_name.name
    if Scene == 99:
        if Scene_99.query.all():
            entries = Scene_99.query.all()
            name = entries[0].scene_name.name

    return (entries, name)


def GET_ALL_SCENES():
    return Scenes.query.all()   


def SET_SCENE_NAME(Scene, name):
    check_entry = Scenes.query.filter_by(name=name).first()
    if check_entry is None:
        entry = Scenes.query.filter_by(id=Scene).first()
        entry.name = name
        db.session.commit()
        return ("")
    else:
        return ("Name bereits vergeben")


def SET_SCENE_COLOR(Scene, rgb_scene):
    if Scene == 1:
        # check all array entries
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                # get scene settings
                entry = Scene_01.query.filter_by(led_id=i+1).first()
                # get the rgb values only (source: rgb(xxx, xxx, xxx))
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 2:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_02.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 3:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_03.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 4:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_04.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 5:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_05.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break 
    if Scene == 6:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_06.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 7:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_07.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 8:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_08.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 9:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_09.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break 
    if Scene == 10:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_10.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break 
    if Scene == 99:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_99.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break 

    try:
        entry.color_red   = rgb_color[0]
        entry.color_green = rgb_color[1]           
        entry.color_blue  = rgb_color[2]
        db.session.commit()
    except:
        pass


def SET_SCENE_BRIGHTNESS(Scene, brightness):
    if Scene == 1:
        # check all array entries
        for i in range(len(brightness)):
            if brightness[i] is not None:
                # get scene settings
                entry = Scene_01.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 2:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_02.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 3:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_03.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break            
    if Scene == 4:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_04.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 5:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_05.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 6:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_06.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 7:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_07.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break            
    if Scene == 8:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_08.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 9:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_09.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 10:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_10.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 99:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_99.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break

    try:
        entry.brightness = brightness
        db.session.commit()
    except:
        pass


def DEL_SCENE(Scene):
    if Scene == 1:
        Scene_01.query.delete()
    if Scene == 2:
        Scene_02.query.delete()
    if Scene == 3:
        Scene_03.query.delete()
    if Scene == 4:
        Scene_04.query.delete()
    if Scene == 5:
        Scene_05.query.delete()
    if Scene == 6:
        Scene_06.query.delete()
    if Scene == 7:
        Scene_07.query.delete()
    if Scene == 8:
        Scene_08.query.delete()
    if Scene == 9:
        Scene_09.query.delete()
    if Scene == 10:
        Scene_10.query.delete()
    if Scene == 99:
        Scene_99.query.delete()

    # delete scene name
    entry = Scenes.query.get(Scene)
    entry.name = ""
    db.session.commit()


""" ################### """
""" ################### """
"""        mqtt         """
""" ################### """
""" ################### """


def GET_MQTT_DEVICE(id):
    return MQTT_Devices.query.filter_by(id=id).first()


def GET_ALL_MQTT_DEVICES(selector):
    device_list = []
    devices = MQTT_Devices.query.all()
    
    if selector == "mqtt" or selector == "zigbee":
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
                
    return device_list
        

def GET_MQTT_DEVICE_NAME(id):
    return MQTT_Devices.query.filter_by(id=id).first().name
    

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


def SET_MQTT_DEVICE_MQTT(id, name):
    entry = MQTT_Devices.query.filter_by(id=id).first()

    # values changed ?
    if (entry.name != name):

        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> MQTT Device >>> " + entry.name + " >>> changed >>> Name: " +
                            name + " /// Gateway: " + entry.gateway + " /// ieeeAddr: " + entry.ieeeAddr + 
                            " /// Model: " + entry.model + " /// Inputs: " + str(entry.inputs) + " /// Outputs: " + 
                            entry.outputs)

        entry.name = name
        db.session.commit()    


def SET_MQTT_DEVICE_ZigBee(id, name, inputs):
    entry = MQTT_Devices.query.filter_by(id=id).first()

    # values changed ?
    if (entry.name != name or entry.inputs != inputs):
        
        entry.inputs = inputs
        
        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> MQTT Device >>> " + entry.name + " >>> changed >>> Name: " +
                            name + " /// Gateway: " + entry.gateway + " /// ieeeAddr: " + entry.ieeeAddr + 
                            " /// Model: " + entry.model + " /// Inputs: " + inputs)

        entry.name = name
        db.session.commit()    


def DELETE_MQTT_DEVICE(id):
    if Plants.query.filter_by(mqtt_device_id=id).first():
        entry = GET_MQTT_DEVICE(id)
        SET_ERROR_LIST(entry.name + " wird in Bewässerung verwendet")
    elif Sensordata_Jobs.query.filter_by(mqtt_device_id=id).first():
        entry = GET_MQTT_DEVICE(id)
        SET_ERROR_LIST(entry.name + " wird in Sensordaten verwendet")      
    else:
        entry = GET_MQTT_DEVICE(id)
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


def CHECK_PLANTS():
    string_errors = ""
    entries = Plants.query.all()
    for entry in entries:
        if ((entry.sensor_key == "None" or entry.sensor_key == None) or
            (entry.pump_key == "None" or entry.pump_key == None) or
            (entry.moisture == "None" or entry.moisture == None)):
            
            string_errors = string_errors + str(entry.name) + " "
     
    if string_errors != "":
        return ("Einstellungen unvollständig ( Pflanzen-Name: " + string_errors + ")")
    else:
        return ""


def ADD_PLANT(name, mqtt_device_id, watervolume, moisture, log = ""):
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
                        moisture       = moisture,                    
                    )
                db.session.add(plant)
                db.session.commit()
                
                if log == "":
                    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Plant >>> " + name + " >>> added")               
                
                return ""

    else:
        return "Name bereits vergeben"


def SET_PLANT_SETTINGS(plant_id, name, sensor_key, pump_key, watervolume, moisture):        
    entry = Plants.query.filter_by(id=plant_id).first()
    old_name = entry.name

    # values changed ?
    if (entry.name != name or entry.sensor_key != sensor_key or entry.pump_key != pump_key or 
        entry.watervolume != int(watervolume) or entry.moisture != moisture):

        entry.name = name
        entry.sensor_key = sensor_key
        entry.pump_key = pump_key
        entry.watervolume = watervolume
        entry.moisture = moisture
        
        db.session.commit()  

        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Plant >>> " + old_name + " >>> changed >>> Name: " + entry.name + 
                             " /// MQTT-Device: " + entry.mqtt_device.name + " /// Sensor: " + entry.sensor_key + 
                             " /// Pump: " + entry.pump_key + " /// Watervolume: " + str(watervolume) + " /// Moisture: " +
                             entry.moisture)                


def DELETE_PLANT(plant_id, log = ""):
    entry = GET_PLANT_BY_ID(plant_id)

    if log == "":
        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Plant >>> " + entry.name + " >>> deleted")   
    
    Plants.query.filter_by(id=plant_id).delete()
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


def CHECK_SENSORDATA_JOBS():
    string_errors = ""
    entries = Sensordata_Jobs.query.all()
    for entry in entries:
        if entry.sensor_key == "None" or entry.sensor_key == None:
            string_errors = string_errors + str(entry.id) + " "
            
    if string_errors != "":
        return ("Einstellungen unvollständig ( Job-ID: " + string_errors + ")")
    else:
        return ""


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
"""      settings       """
""" ################### """
""" ################### """


def GET_SETTING_VALUE(name):
    entry = Settings.query.filter_by(setting_name=name).first()
    return entry.setting_value


def SET_SETTING_VALUE(name, value):
    entry = Settings.query.filter_by(setting_name=name).first()
    entry.setting_value = value
    db.session.commit()    


def GET_HUE_BRIDGE_IP():
    entry = HUE_Bridge.query.filter_by().first()
    return (entry.ip)  


def SET_HUE_BRIDGE_IP(IP):
    entry = HUE_Bridge.query.filter_by().first()
    entry.ip = IP
    db.session.commit() 


def REMOVE_LED(id):
    if Scene_01.query.filter_by(led_id=id).first():
        return "LED in Szene 1 verwendet"
    if Scene_02.query.filter_by(led_id=id).first():
        return "LED in Szene 2 verwendet"
    if Scene_03.query.filter_by(led_id=id).first():
        return "LED in Szene 3 verwendet"
    if Scene_04.query.filter_by(led_id=id).first():
        return "LED in Szene 4 verwendet" 
    if Scene_05.query.filter_by(led_id=id).first():
        return "LED in Szene 5 verwendet"
    if Scene_06.query.filter_by(led_id=id).first():
        return "LED in Szene 6 verwendet"
    if Scene_07.query.filter_by(led_id=id).first():
        return "LED in Szene 7 verwendet"
    if Scene_08.query.filter_by(led_id=id).first():
        return "LED in Szene 8 verwendet"
    if Scene_09.query.filter_by(led_id=id).first():
        return "LED in Szene 9 verwendet"
    if Scene_10.query.filter_by(led_id=id).first():
        return "LED in Szene 10 verwendet"
    if Scene_99.query.filter_by(led_id=id).first():
        return "LED in Szene 99 verwendet"

    LED.query.filter_by(id=id).delete()
    db.session.commit()    

    return "LED erfolgreich gelöscht"


""" ################### """
""" ################### """
"""      snowboy        """
""" ################### """
""" ################### """


def GET_SNOWBOY_SENSITIVITY():
    entry = Snowboy.query.filter_by().first()
    return (entry.sensitivity)  


def SET_SNOWBOY_SENSITIVITY(value):
    entry = Snowboy.query.filter_by().first()
    entry.sensitivity = value
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
    entry = GET_SNOWBOY_TASK_ID(task_id)
    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Snowboy Task >>> " + entry.name + " >>> deleted")    
    
    
    Snowboy_Tasks.query.filter_by(id=task_id).delete()
    db.session.commit()


""" ################## """
""" ################## """
"""   taskmanagement   """
""" ################## """
""" ################## """


def GET_TASKMANAGEMENT_TIME_TASK_BY_NAME(name):
    return Taskmanagement_Time.query.filter_by(name=name).first()


def GET_TASKMANAGEMENT_TIME_TASK_BY_ID(id):
    return Taskmanagement_Time.query.filter_by(id=id).first()


def GET_ALL_TASKMANAGEMENT_TIME_TASKS():
    return Taskmanagement_Time.query.all()


def ADD_TASKMANAGEMENT_TIME_TASK(name, task, day, hour, minute, repeat):
    # name exist ?
    check_entry = Taskmanagement_Time.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,25):
            if Taskmanagement_Time.query.filter_by(id=i).first():
                pass
            else:
                # add the new task
                new_task = Taskmanagement_Time(
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
                
                WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Taskmanagement (Time) >>> " + name + " >>> added >>> Task: " + 
                                     task + " /// Day: " + day + " /// Hour: " + str(hour) + " /// Minute: " + str(minute) + 
                                     " /// Repeat: " +  repeat)                
                
                return ""
    else:
        return "Name bereits vergeben"


def SET_TASKMANAGEMENT_TIME_TASK(id, name, task, day, hour, minute, repeat):       
    entry = Taskmanagement_Time.query.filter_by(id=id).first()
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

        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Taskmanagement (Time) >>> " + old_name + " >>> changed >>> Name: " + 
                             entry.name + " /// Task: " + entry.task + " /// Day: " + entry.day + " /// Hour: " + 
                             entry.hour + " /// Minute: " + entry.minute + " /// Repeat: " +  entry.repeat)


def DELETE_TASKMANAGEMENT_TIME_TASK(task_id):
    entry = GET_TASKMANAGEMENT_TIME_TASK_BY_ID(task_id)
    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Taskmanagement (Time) >>> " + entry.name + " >>> deleted")    
    
    Taskmanagement_Time.query.filter_by(id=task_id).delete()
    db.session.commit()


def GET_TASKMANAGEMENT_SENSOR_TASK_BY_NAME(name):
    return Taskmanagement_Sensor.query.filter_by(name=name).first()


def GET_TASKMANAGEMENT_SENSOR_TASK_BY_ID(id):
    return Taskmanagement_Sensor.query.filter_by(id=id).first()
    

def GET_ALL_TASKMANAGEMENT_SENSOR_TASKS():
    return Taskmanagement_Sensor.query.all()


def CHECK_TASKMANAGEMENT_SENSOR_TASKS():
    string_errors = ""
    entries = Taskmanagement_Sensor.query.all()
    for entry in entries:
        if entry.sensor_key == "None" or entry.sensor_key == None:
            string_errors = string_errors + str(entry.name) + " "
            
    if string_errors != "":
        return ("Einstellungen unvollständig ( Aufgabenname: " + string_errors + ")")
    else:
        return ""


def ADD_TASKMANAGEMENT_SENSOR_TASK(name, task, mqtt_device_id, operator, value, log = ""):
    # name exist ?
    check_entry = Taskmanagement_Sensor.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,25):
            if Taskmanagement_Sensor.query.filter_by(id=i).first():
                pass
            else:
                # add the new task
                new_task = Taskmanagement_Sensor(
                        id             = i,
                        name           = name,
                        task           = task,                        
                        mqtt_device_id = mqtt_device_id,
                        operator       = operator,
                        value          = value,
                    )
                db.session.add(new_task)
                db.session.commit()
                
                if log == "":
                    WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Taskmanagement (Sensor) >>> " + name + " >>> added")               
                
                return ""
    else:
        return "Name bereits vergeben"


def SET_TASKMANAGEMENT_SENSOR_TASK(id, name, task, mqtt_device_id, sensor_key, operator, value):
    entry = Taskmanagement_Sensor.query.filter_by(id=id).first()
    old_name = entry.name

    # values changed ?
    if (entry.name != name or entry.task != task or str(entry.mqtt_device_id) != mqtt_device_id or
        entry.sensor_key != sensor_key or entry.operator != operator or entry.value != value):
            
        entry.name = name        
        entry.task = task
        entry.mqtt_device_id = mqtt_device_id
        entry.sensor_key = sensor_key
        entry.operator = operator
        entry.value = value
        db.session.commit()    

        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Taskmanagement (Sensor) >>> " + old_name + " >>> changed >>> Name: " +
                             entry.name + " /// Task: " + entry.task + " /// MQTT-Device: " + entry.mqtt_device.name + 
                             " /// Sensor: " + entry.sensor_key + " /// Operator: " + entry.operator + " /// Value: " +  
                             entry.value)


def DELETE_TASKMANAGEMENT_SENSOR_TASK(task_id, log = ""):
    entry = GET_TASKMANAGEMENT_SENSOR_TASK_BY_ID(task_id)

    if log == "":
        WRITE_LOGFILE_SYSTEM("EVENT", "Database >>> Taskmanagement (Sensor) >>> " + entry.name + " >>> deleted")    
    
    Taskmanagement_Sensor.query.filter_by(id=task_id).delete()
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
"""        zigbee       """
""" ################### """
""" ################### """

    
def GET_ZIGBEE_PAIRING():
    return ZigBee.query.filter_by().first().pairing


def SET_ZIGBEE_PAIRING(setting):
    entry = ZigBee.query.filter_by().first()
    entry.pairing = setting
    db.session.commit()
