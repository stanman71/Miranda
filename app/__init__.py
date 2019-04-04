import threading

from flask import Flask
from flask_bootstrap import Bootstrap

from app.components.colorpicker_local import colorpicker

""" ###### """
""" flasks """
""" ###### """

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
Bootstrap(app)
colorpicker(app)

from app.sites import index, user_login, dashboard, led, taskmanagement, plants, sensordata, settings
from app.database.database import *
from app.components.pixel_ring import PIXEL_RING_CONTROL
from app.components.file_management import WRITE_LOGFILE_SYSTEM


# deactivate pixel_ring
PIXEL_RING_CONTROL("off")


# start flask
class flask_Thread(threading.Thread):
    def __init__(self, ID = 1, name = "flask_Thread"):
        threading.Thread.__init__(self)
        self.ID = ID
        self.name = name

    def run(self):
        print("###### Start FLASK ######")

        @app.before_first_request
        def initialisation():
            pass
         
        app.run(host='0.0.0.0', port=5000)
        #app.run()
     
t1 = flask_Thread()
t1.start()


# start MQTT
if GET_SETTING_VALUE("mqtt") == "True":
    class mqtt_Thread(threading.Thread):
        def __init__(self, ID = 2, name = "mqtt_Thread"):
            threading.Thread.__init__(self)
            self.ID = ID
            self.name = name

        def run(self):
            try:
                from app.components.mqtt import MQTT_START

                print("###### Start MQTT ######")
                MQTT_START()

            except Exception as e:
                print("Fehler in MQTT: " + str(e))
                WRITE_LOGFILE_SYSTEM("ERROR", "MQTT >>> " + str(e)) 
    
    t2 = mqtt_Thread()
    t2.start()


# start snowboy
if GET_SETTING_VALUE("snowboy") == "True":
    
    try:
        from app.snowboy.snowboy import SNOWBOY_START

        print("###### Start SNOWBOY ######")
        SNOWBOY_START()

    except Exception as e:
        if "signal only works in main thread" not in str(e): 
            print("Fehler in SnowBoy: " + str(e))
            WRITE_LOGFILE_SYSTEM("ERROR", "Snowboy >>> " + str(e)) 
