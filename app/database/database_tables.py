from flask_sqlalchemy  import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from app import app

# connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/smarthome.sqlite3'
db = SQLAlchemy(app)


""" ###################### """
""" define table structure """
""" ###################### """


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id       = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(50), unique=True)
    email    = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    role     = db.Column(db.String(20), server_default=("user"))

class Schedular(db.Model):
    __tablename__ = 'schedular'
    id     = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name   = db.Column(db.String(50), unique=True)
    day    = db.Column(db.String(50))
    hour   = db.Column(db.String(50))
    minute = db.Column(db.String(50))
    task   = db.Column(db.String(100))
    repeat = db.Column(db.String(50))

class Bridge(db.Model):
    __tablename__ = 'bridge'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    ip = db.Column(db.String(50), unique = True)

class LED(db.Model):
    __tablename__ = 'LED'
    id      = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name    = db.Column(db.String(50), unique = True)

class Programs(db.Model):
    __tablename__ = 'programs'
    id      = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name    = db.Column(db.String(50), unique = True)
    content = db.Column(db.Text)

class Scenes(db.Model):
    __tablename__ = 'scenes'
    id   = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name = db.Column(db.String(50))

class Scene_01(db.Model):
    __tablename__ = 'scene_01'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("1"))
    scene_name  = db.relationship('Scenes') # connection to an other table (Scenes)
    LED_id      = db.Column(db.Integer, db.ForeignKey('LED.id'), unique = True)
    LED_name    = db.relationship('LED')    # connection to an other table (LED)
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_02(db.Model):
    __tablename__ = 'scene_02'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("2"))
    scene_name  = db.relationship('Scenes')
    LED_id      = db.Column(db.Integer, db.ForeignKey('LED.id'), unique = True)
    LED_name    = db.relationship('LED')    
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_03(db.Model):
    __tablename__ = 'scene_03'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("3"))
    scene_name  = db.relationship('Scenes')
    LED_id      = db.Column(db.Integer, db.ForeignKey('LED.id'), unique = True)
    LED_name    = db.relationship('LED')
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_04(db.Model):
    __tablename__ = 'scene_04'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("4"))
    scene_name  = db.relationship('Scenes')
    LED_id      = db.Column(db.Integer, db.ForeignKey('LED.id'), unique = True)
    LED_name    = db.relationship('LED')
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_05(db.Model):
    __tablename__ = 'scene_05'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("5"))
    scene_name  = db.relationship('Scenes')
    LED_id      = db.Column(db.Integer, db.ForeignKey('LED.id'), unique = True)
    LED_name    = db.relationship('LED') 
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_06(db.Model):
    __tablename__ = 'scene_06'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("6"))
    scene_name  = db.relationship('Scenes')
    LED_id      = db.Column(db.Integer, db.ForeignKey('LED.id'), unique = True)
    LED_name    = db.relationship('LED')    
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_07(db.Model):
    __tablename__ = 'scene_07'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("7"))
    scene_name  = db.relationship('Scenes')
    LED_id      = db.Column(db.Integer, db.ForeignKey('LED.id'), unique = True)
    LED_name    = db.relationship('LED')
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_08(db.Model):
    __tablename__ = 'scene_08'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("8"))
    scene_name  = db.relationship('Scenes')
    LED_id      = db.Column(db.Integer, db.ForeignKey('LED.id'), unique = True)
    LED_name    = db.relationship('LED')
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

class Scene_09(db.Model):
    __tablename__ = 'scene_09'
    id          = db.Column(db.Integer, primary_key=True, autoincrement = True)
    scene_id    = db.Column(db.Integer, db.ForeignKey('scenes.id'), server_default=("9"))
    scene_name  = db.relationship('Scenes')
    LED_id      = db.Column(db.Integer, db.ForeignKey('LED.id'), unique = True)
    LED_name    = db.relationship('LED') 
    color_red   = db.Column(db.Integer, server_default=("0"))
    color_green = db.Column(db.Integer, server_default=("0"))
    color_blue  = db.Column(db.Integer, server_default=("0"))
    brightness  = db.Column(db.Integer, server_default=("254"))

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


""" ################################ """
""" create tables and default values """
""" ################################ """

# create all database tables
db.create_all()

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

# Create default bridge settings
if Bridge.query.filter_by().first() is None:
    bridge = Bridge(
        id = '1',
        ip = 'default',
    )
    db.session.add(bridge)
    db.session.commit()

# Create default scenes
if Scenes.query.filter_by().first() is None:   
    for i in range(1,10):
        scene = Scenes(
            id   = i,
            name = "",
        )
        db.session.add(scene)
        db.session.commit()

# create sensors
if Sensor.query.filter_by().first() is None:   
    for i in range(0,8):
        sensor = Sensor(
            id   = i,
            name = "GPIO_A0" + str(i),
        )
        db.session.add(sensor)
     
    for i in range(9,12):
        sensor = Sensor(
            id   = i,
            name = "MQTT_0" + str(i - 9),
        )
        db.session.add(sensor)
        db.session.commit()