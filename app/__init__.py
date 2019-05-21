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
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Bootstrap(app)
colorpicker(app)

from app.sites import index, user_login, dashboard, led, scheduler, plants, sensordata, settings
from app.database.database import *
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL
from app.components.file_management import WRITE_LOGFILE_SYSTEM, READ_LOGFILE_MQTT, WRITE_LOGFILE_SYSTEM_THREAD
from app.components.mqtt import MQTT_PUBLISH
from app.components.mqtt_functions import MQTT_STOP_ALL_OUTPUTS

# deactivate pixel_ring
MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().microphone, "off")

# turn_off all outputs
if GET_GLOBAL_SETTING_VALUE("mqtt") == "True":
    try:    
        MQTT_STOP_ALL_OUTPUTS()
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | " + str(e)) 


# start flask
def START_FLASK_THREAD(start):
    print("###### Start FLASK ######")

    @app.before_first_request
    def initialisation():
        pass
        
    #app.run(host='0.0.0.0', port=5000)
    app.run()
     
Thread = threading.Thread(target=START_FLASK_THREAD, args=("",))
Thread.start() 


# start write logfile system thread
Thread = threading.Thread(target=WRITE_LOGFILE_SYSTEM_THREAD, args=())
Thread.start() 


""" ###### """
"""  mqtt  """
""" ###### """

# start MQTT
def START_MQTT_THREAD(start):
    try:
        from app.components.mqtt import MQTT_START

        print("###### Start MQTT ######")
        MQTT_START()

    except Exception as e:
        print("Fehler in MQTT: " + str(e))
        WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | " + str(e)) 
    

if GET_GLOBAL_SETTING_VALUE("mqtt") == "True":
    Thread = threading.Thread(target=START_MQTT_THREAD, args=("",))
    Thread.start() 
    
    
""" ###### """
""" zigbee """
""" ###### """
 
# start zigbee    
if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") == "True":
    
    time.sleep(3)
    
    if READ_LOGFILE_MQTT("zigbee2mqtt", "",5) != "Message nicht gefunden":
        WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | No connection") 
    
    # set pairing setting  
    pairing_setting = GET_ZIGBEE2MQTT_PAIRING()    
    if pairing_setting == "True":
        channel = "SmartHome/zigbee2mqtt/bridge/config/permit_join"
        MQTT_PUBLISH(channel, "true")   
    else:
        channel = "SmartHome/zigbee2mqtt/bridge/config/permit_join"
        MQTT_PUBLISH(channel, "false")

# disable pairing
if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") != "True":
    try:
        channel = "SmartHome/zigbee2mqtt/bridge/config/permit_join"
        MQTT_PUBLISH(channel, "false") 
    except:
        pass


""" ############# """
""" speechcontrol """
""" ############# """

# start snowboy
if GET_GLOBAL_SETTING_VALUE("speechcontrol") == "speech_recognition_provider":
    
    try:
        from app.speechcontrol.snowboy.snowboy import SNOWBOY_START

        print("###### Start SPEECH CONTROL ######")
        SNOWBOY_START()       

    except Exception as e:
        if "signal only works in main thread" not in str(e): 
            print("Fehler in SnowBoy: " + str(e))
            WRITE_LOGFILE_SYSTEM("ERROR", "Snowboy | " + str(e)) 
            
