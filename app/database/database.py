from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
import re
import time

from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/smarthome.sqlite3'
db = SQLAlchemy(app)


""" ###################### """
""" ###################### """
""" define table structure """
""" ###################### """
""" ###################### """

class Settings(db.Model):
    __tablename__ = 'settings'
    id            = db.Column(db.Integer, primary_key=True, autoincrement = True)
    setting_name  = db.Column(db.String(50), unique=True)
    setting_value = db.Column(db.String(50))

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id       = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(50), unique=True)
    email    = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    role     = db.Column(db.String(20), server_default=("user"))

class Schedular_Tasks(db.Model):
    __tablename__ = 'schedular_tasks'
    id     = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name   = db.Column(db.String(50), unique=True)
    day    = db.Column(db.String(50))
    hour   = db.Column(db.String(50))
    minute = db.Column(db.String(50))
    task   = db.Column(db.String(100))
    repeat = db.Column(db.String(50))

class MQTT_Devices(db.Model):
    __tablename__ = 'mqtt_devices'
    id           = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name         = db.Column(db.String(50), unique=True)
    channel_path = db.Column(db.String(50))
    modell       = db.Column(db.String(50))
    inputs       = db.Column(db.Integer)
    outputs      = db.Column(db.Integer)
    last_contact = db.Column(db.String(50))

class Snowboy(db.Model):
    __tablename__ = 'snowboy'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    sensitivity = db.Column(db.Integer)

class Snowboy_Tasks(db.Model):
    __tablename__ = 'snowboy_tasks'
    id   = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name = db.Column(db.String(50), unique = True)
    task = db.Column(db.String(100))

class HUE_Bridge(db.Model):
    __tablename__ = 'hue_bridge'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    ip = db.Column(db.String(50), unique = True)

class Plants(db.Model):
    __tablename__ = 'plants'
    id               = db.Column(db.Integer, primary_key=True, autoincrement = True)   
    name             = db.Column(db.String(50), unique=True)
    mqtt_device_id   = db.Column(db.Integer, db.ForeignKey('mqtt_devices.id'))   
    mqtt_device_name = db.relationship('MQTT_Devices')    
    sensor_id        = db.Column(db.Integer)
    moisture         = db.Column(db.Integer) 
    moisture_voltage = db.Column(db.Integer)    
    water_volume     = db.Column(db.Integer)
    pump_id          = db.Column(db.Integer)

class LED(db.Model):
    __tablename__ = 'led'
    id      = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name    = db.Column(db.String(50), unique = True)

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
    scene_name  = db.relationship('Scenes') # connection to an other table (Scenes)
    led_id      = db.Column(db.Integer, db.ForeignKey('led.id'), unique = True)
    led_name    = db.relationship('LED')    # connection to an other table (led)
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


""" ################################ """
""" ################################ """
""" create tables and default values """
""" ################################ """
""" ################################ """


# create all database tables
db.create_all()


# create default settings
if Settings.query.filter_by().first() is None:
    setting = Settings(
        setting_name  = "hue_bridge",
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

    setting = Settings(
        setting_name  = "mqtt",
        setting_value = "False",
    )
    db.session.add(setting)    
    db.session.commit()


# create default snowboy
if Snowboy.query.filter_by().first() is None:
    snowboy = Snowboy(
        sensitivity  = "50",
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


# Create default scenes
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


""" ################### """
""" ################### """
""" database operations """
""" ################### """
""" ################### """


""" ######## """
""" settings """
""" ######## """

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


""" ####### """
""" snowboy """
""" ####### """

def GET_SNOWBOY_SENSITIVITY():
    entry = Snowboy.query.filter_by().first()
    return (entry.sensitivity)  


def SET_SNOWBOY_SENSITIVITY(value):
    entry = Snowboy.query.filter_by().first()
    entry.sensitivity = value
    db.session.commit() 


""" #### """
""" mqtt """
""" #### """

def GET_MQTT_DEVICE(id):
    return MQTT_Devices.query.filter_by(id=id).first()


def GET_ALL_MQTT_DEVICES():
    return MQTT_Devices.query.all()


def GET_MQTT_DEVICE_NAME(id):
    device_name = MQTT_Devices.query.filter_by(id=id).first()
    return device_name.name  


def ADD_MQTT_DEVICE(name, channel_path, modell = "", inputs = 0, outputs = 0, last_contact = ""):
    # name exist ?
    check_entry = MQTT_Devices.query.filter_by(name=name).first()
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
                        channel_path = channel_path,
                        modell       = modell,
                        inputs       = inputs,
                        outputs      = outputs,
                        last_contact = last_contact,
                        )
                db.session.add(device)
                db.session.commit()
                return ""
    else:
        return "Name bereits vergeben"


def UPDATE_MQTT_DEVICE_INFORMATIONS(id, modell, inputs, outputs, last_contact):
    entry = MQTT_Devices.query.filter_by(id=id).first()
    entry.modell = modell
    entry.inputs = inputs
    entry.outputs = outputs
    entry.last_contact = last_contact
    db.session.commit()     


def UPDATE_MQTT_DEVICE_LAST_CONTACT(id, last_contact):
    entry = MQTT_Devices.query.filter_by(id=id).first()
    entry.last_contact = last_contact
    db.session.commit()        


def DELETE_MQTT_DEVICE(id):
    MQTT_Devices.query.filter_by(id=id).delete()
    db.session.commit() 
    return "MQTT-Device gelöscht"


""" ############### """
""" task management """
""" ############### """

def GET_SCHEDULAR_TASK(name):
    return Schedular_Tasks.query.filter_by(name=name).first()


def GET_ALL_SCHEDULAR_TASKS():
    return Schedular_Tasks.query.all()


def ADD_SCHEDULAR_TASK(name, day, hour, minute, task, repeat):
    # name exist ?
    check_entry = Schedular_Tasks.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,25):
            if Schedular_Tasks.query.filter_by(id=i).first():
                pass
            else:
                # add the new task
                task = Schedular_Tasks(
                        id     = i,
                        name   = name,
                        day    = day,
                        hour   = hour,
                        minute = minute,
                        task   = task,
                        repeat = repeat,
                    )
                db.session.add(task)
                db.session.commit()
                return ""
    else:
        return "Name bereits vergeben"


def DELETE_SCHEDULAR_TASK(task_id):
    Schedular_Tasks.query.filter_by(id=task_id).delete()
    db.session.commit()


def GET_SNOWBOY_TASK(name):
    return Snowboy_Tasks.query.filter_by(name=name).first()


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
                return ""
    else:
        return "Name bereits vergeben"


def DELETE_SNOWBOY_TASK(task_id):
    Snowboy_Tasks.query.filter_by(id=task_id).delete()
    db.session.commit()


""" ############### """
""" user management """
""" ############### """

def GET_USER_BY_ID(user_id):
    return User.query.get(int(user_id))


def GET_USER_BY_NAME(user_name):
    return User.query.filter_by(username=user_name).first()


def GET_ALL_USERS():
    return User.query.all()


def ADD_USER(user_name, email, password):
    new_user = User(username=user_name, email=email, password=password, role="user")
    db.session.add(new_user)
    db.session.commit()


def ACTIVATE_USER(user_id):
    entry = User.query.get(user_id)
    entry.role = "superuser"
    db.session.commit()


def DELETE_USER(user_id):
    User.query.filter_by(id=user_id).delete()
    db.session.commit()


def GET_EMAIL(email):
    return User.query.filter_by(email=email).first()


""" ### """
""" led """
""" ### """

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


""" ###### """
""" scenes """
""" ###### """

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


""" ############ """
""" led programs """
""" ############ """

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


def GET_DROPDOWN_LIST_PROGRAMS():
    entry_list = []
    # get all Programs
    entries = Programs.query.all()
    for entry in entries:
        # select the Programs names only
        entry_list.append(entry.name)

    return entry_list


def GET_ALL_PROGRAMS():
    return Programs.query.all()   


def GET_PROGRAM_NAME(name):
    return Programs.query.filter_by(name=name).first()


def GET_PROGRAM_ID(id):
    return Programs.query.filter_by(id=id).first()


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


""" ###### """
""" plants """
""" ###### """

def GET_PLANT(plant_id):
    return Plants.query.filter_by(id=plant_id).first()


def GET_ALL_PLANTS():
    return Plants.query.all()


def ADD_PLANT(name, mqtt_device_id, sensor_id, pump_id, water_volume):
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
                        sensor_id      = sensor_id,
                        pump_id        = pump_id,
                        moisture       = 0,
                        water_volume   = water_volume,
                    )
                db.session.add(plant)
                db.session.commit()
                return ""

    else:
        return "Name bereits vergeben"


def CHANGE_MOISTURE(plant_id, moisture):    
    entry = Plants.query.filter_by(id=plant_id).first()
    entry.moisture = moisture
    # calculate voltage value
    voltage_value = round((float(moisture) * 1.6) / 100, 2) 
    moisture_voltage = round(2.84 - voltage_value, 2)   
    entry.moisture_voltage = moisture_voltage
    db.session.commit()  


def CHANGE_WATER_VOLUME(plant_id, water_volume):        
    entry = Plants.query.filter_by(id=plant_id).first()
    entry.water_volume = water_volume
    db.session.commit()    


def DELETE_PLANT(plant_id):
    Plants.query.filter_by(id=plant_id).delete()
    db.session.commit()