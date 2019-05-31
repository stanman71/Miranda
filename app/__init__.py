import os
import threading

from flask import Flask
from flask_bootstrap import Bootstrap

from app.components.colorpicker_local import colorpicker

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Bootstrap(app)
colorpicker(app)

from app.sites import index, user_login, dashboard, led, scheduler, plants, sensordata, settings
from app.database.database import *
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL
from app.components.file_management import WRITE_LOGFILE_SYSTEM, READ_LOGFILE_MQTT
from app.components.mqtt_functions import MQTT_PUBLISH, MQTT_STOP_ALL_OUTPUTS


# deactivate pixel_ring
MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().microphone, "off")

# turn_off all outputs
if GET_GLOBAL_SETTING_VALUE("mqtt") == "True":
    try:    
        MQTT_STOP_ALL_OUTPUTS()
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | " + str(e)) 


""" ##### """
""" flask """
""" ##### """

# start flask
def START_FLASK_THREAD():

    try:
        print("###### Start FLASK ######")

        @app.before_first_request
        def initialisation():
            pass

        # windows
        if os.name == "nt":                 
            app.run()
        # linux
        else:                               
            app.run(host='0.0.0.0', port=5000)

    except:
        pass
     
Thread = threading.Thread(target=START_FLASK_THREAD)
Thread.start() 


""" ############# """
""" speechcontrol """
""" ############# """

# snowboy operates in main only
# start snowboy

if GET_GLOBAL_SETTING_VALUE("speechcontrol") == "speech_recognition_provider":
    
    try:
        from app.components.process_management import SNOWBOY_START

        print("###### Start SPEECH CONTROL ######")
        SNOWBOY_START()       

    except Exception as e:
        if "signal only works in main thread" not in str(e): 
            print("Fehler in SnowBoy: " + str(e))
            WRITE_LOGFILE_SYSTEM("ERROR", "Snowboy | " + str(e)) 

