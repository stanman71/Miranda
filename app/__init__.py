import os
import threading

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mobility import Mobility

from app.components.colorpicker_local import colorpicker

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Bootstrap(app)
colorpicker(app)
Mobility(app)

from app.sites import index, user_login, dashboard, camera, led, scheduler, programs, sensordata, spotify, system, watering
from app.database.database import *
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL
from app.components.file_management import WRITE_LOGFILE_SYSTEM
from app.components.mqtt import MQTT_THREAD, MQTT_PUBLISH, MQTT_GET_INCOMING_MESSAGES
from app.components.process_management import PROCESS_MANAGEMENT_THREAD
from app.components.shared_resources import REFRESH_MQTT_INPUT_MESSAGES_THREAD



""" ################## """
""" background threads """
""" ################## """

Thread = threading.Thread(target=PROCESS_MANAGEMENT_THREAD)
Thread.start() 

Thread = threading.Thread(target=REFRESH_MQTT_INPUT_MESSAGES_THREAD)
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
    
    zigbee_connected = False
    time.sleep(3)
    
    for message in MQTT_GET_INCOMING_MESSAGES(5):
        
        if message[1] == "SmartHome/zigbee2mqtt/bridge/state" and message[2] == "online":
            
            zigbee_connected = True 
            break
         
    if zigbee_connected == True: 
        
        WRITE_LOGFILE_SYSTEM("EVENT", "ZigBee2MQTT | Connected")
        
        # set pairing setting  
        pairing_setting = GET_ZIGBEE2MQTT_PAIRING()          
        
        if pairing_setting == "True":
            
            MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/permit_join", "true")  
            time.sleep(1)
            zigbee_check = False
            
            for message in MQTT_GET_INCOMING_MESSAGES(5):
                
                if message[1] == "SmartHome/zigbee2mqtt/bridge/config" and message[2] == '{"log_level":"info","permit_join":true}':
                    zigbee_check = True
            
            if zigbee_check == True:             
                WRITE_LOGFILE_SYSTEM("EVENT", "ZigBee2MQTT | Pairing enabled") 
            else:             
                WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | Pairing enabled | Setting not confirmed")             
                     
        else:
            MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/permit_join", "false")
            time.sleep(1)
            zigbee_check = False
            
            for message in MQTT_GET_INCOMING_MESSAGES(5):
                
                if message[1] == "SmartHome/zigbee2mqtt/bridge/config" and message[2] == '{"log_level":"info","permit_join":false}':
                    zigbee_check = True
            
            if zigbee_check == True:             
                WRITE_LOGFILE_SYSTEM("EVENT", "ZigBee2MQTT | Pairing disabled") 
            else:             
                WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | Pairing disabled | Setting not confirmed")    
                
                
    else:
        WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | No Connection")        
        

# always disable pairing when zigbee2mqtt running without activation
if GET_GLOBAL_SETTING_VALUE("zigbee2mqtt") != "True":
    
    try:
        MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/permit_join", "false") 
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
    MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().snowboy_microphone, "off")
