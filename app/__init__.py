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

from app.sites import index, user_login, dashboard, camera, led, scheduler, programs, plants, sensordata, spotify, settings
from app.database.database import *
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL
from app.components.file_management import WRITE_LOGFILE_SYSTEM, READ_LOGFILE_MQTT
from app.components.mqtt import MQTT_THREAD, MQTT_PUBLISH
from app.components.process_management import PROCESS_MANAGEMENT_THREAD



""" ################## """
""" process_management """
""" ################## """

Thread = threading.Thread(target=PROCESS_MANAGEMENT_THREAD)
Thread.start() 


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


""" #### """
""" mqtt """
""" #### """

# start MQTT
if GET_GLOBAL_SETTING_VALUE("mqtt") == "True":
    try:
        print("###### Start MQTT ######")
        Thread = threading.Thread(target=MQTT_THREAD)	
        Thread.start()

    except Exception as e:
        print("Fehler in MQTT: " + str(e))
        WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | " + str(e)) 


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

# snowboy operates in main only
# start snowboy

if GET_GLOBAL_SETTING_VALUE("speechcontrol") == "True":
    
    try:
        from app.speechcontrol.snowboy.snowboy import SNOWBOY_THREAD

        print("###### Start SPEECH CONTROL ######")
        SNOWBOY_THREAD()       

    except Exception as e:
        if "signal only works in main thread" not in str(e): 
            print("Fehler in SnowBoy: " + str(e))
            WRITE_LOGFILE_SYSTEM("ERROR", "Snowboy | " + str(e)) 

    # deactivate pixel_ring
    MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().microphone, "off")
