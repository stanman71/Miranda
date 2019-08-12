import os
import threading
import netifaces

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mobility import Mobility

from app.components.colorpicker_local import colorpicker

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
Bootstrap(app)
Mobility(app)

from app.sites import index, signup, dashboard, camera, led, scheduler, programs, sensordata, spotify, system, watering
from app.database.database import *
from app.speechcontrol.microphone_led_control import MICROPHONE_LED_CONTROL
from app.components.file_management import *
from app.components.mqtt import MQTT_RECEIVE_THREAD, MQTT_PUBLISH, MQTT_GET_INCOMING_MESSAGES, ZIGBEE2MQTT_CHECK_SETTING_PROCESS
from app.components.process_management import PROCESS_MANAGEMENT_THREAD
from app.components.shared_resources import REFRESH_MQTT_INPUT_MESSAGES_THREAD
from app.components.backend_spotify import REFRESH_SPOTIFY_TOKEN_THREAD
from app.components.email import SEND_EMAIL


""" ################## """
""" update ip settings """
""" ################## """

time.sleep(10)

# lan

try:
    lan_ip_address = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]["addr"]  
except:
    lan_ip_address = ""
    
try:
    lan_gateway = ""
    
    for element in netifaces.gateways()[2]: 
        if element[1] == "eth0":
            lan_gateway = element[0]
        
except:
    lan_gateway = ""
    
# wlan

try:
    wlan_ip_address = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]["addr"]
except:
    wlan_ip_address = ""
    
try:
    wlan_gateway = ""
    
    for element in netifaces.gateways()[2]: 
        if element[1] == "wlan0":
            wlan_gateway = element[0]
                     
except:
    wlan_gateway = ""       


# no seperate wlan gateway 
if wlan_ip_address != "" and wlan_gateway == "":
    wlan_gateway = lan_gateway
    

print("###################################")

SET_HOST_NETWORK(lan_ip_address, lan_gateway, wlan_ip_address, wlan_gateway)


# get wlan credentials
try:
    wlan_ssid     = READ_WLAN_CREDENTIALS_FILE()[0]
    wlan_password = READ_WLAN_CREDENTIALS_FILE()[1]

    SET_WLAN_CREDENTIALS(wlan_ssid, wlan_password)
except:
    pass


# check credential error
if (GET_HOST_NETWORK().wlan_ssid != "" or GET_HOST_NETWORK().wlan_password != "") and GET_HOST_NETWORK().wlan_ip_address == "":
    print("ERROR: WLAN | Wrong Credentials")
    WRITE_LOGFILE_SYSTEM("ERROR", "WLAN | Wrong Credentials")      
    SEND_EMAIL("ERROR", "WLAN | Wrong Credentials")       


# check default interface
if wlan_ip_address == "" and lan_ip_address != "" and GET_HOST_NETWORK().default_interface == "WLAN":
    SET_HOST_DEFAULT_INTERFACE("LAN") 
    
if lan_ip_address == "" and wlan_ip_address != "" and GET_HOST_NETWORK().default_interface == "LAN":
    SET_HOST_DEFAULT_INTERFACE("WLAN") 


""" ################## """
"""     colorpicker    """
""" ################## """

host = GET_HOST_DEFAULT_NETWORK() + ":" + str(GET_HOST_PORT())
colorpicker(host, app)


""" ################## """
""" background threads """
""" ################## """

PROCESS_MANAGEMENT_THREAD()
REFRESH_MQTT_INPUT_MESSAGES_THREAD()
REFRESH_SPOTIFY_TOKEN_THREAD(3000)


""" ##### """
""" flask """
""" ##### """

# start flask
def START_FLASK():

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
            app.run(host = GET_HOST_DEFAULT_NETWORK(), port = GET_HOST_PORT())

    except Exception as e:
        print("ERROR: FLASK | " + str(e))
     
     
try:
    Thread = threading.Thread(target=START_FLASK)
    Thread.start() 
    
except Exception as e:
    print("ERROR: Start Flask | " + str(e))
    WRITE_LOGFILE_SYSTEM("ERROR", "Thread | Refresh MQTT Messages | " + str(e))      
    SEND_EMAIL("ERROR", "Thread | Refresh MQTT Messages | " + str(e))  


""" #### """
""" mqtt """
""" #### """

# start MQTT
if GET_GLOBAL_SETTING_VALUE("mqtt") == "True":
    try:
        print("###### Start MQTT ######")
        MQTT_RECEIVE_THREAD()

    except Exception as e:
        print("ERROR: MQTT | " + str(e))
        WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | " + str(e)) 
        SEND_EMAIL("ERROR", "MQTT | " + str(e)) 

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
        print("ZigBee2MQTT | Connected") 
        
        WRITE_LOGFILE_SYSTEM("EVENT", "ZigBee2MQTT | Connected")

        pairing_setting = GET_ZIGBEE2MQTT_PAIRING()             
            
        if pairing_setting == "True":
            
            # check current pairing setting
            zigbee_check = False
            
            for message in MQTT_GET_INCOMING_MESSAGES(5):
                
                if message[1] == "SmartHome/zigbee2mqtt/bridge/config" and message[2] == '{"log_level":"info","permit_join":true}':
                    zigbee_check = True
                     
            # current setting wrong
            if zigbee_check == False:  
                
                MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/permit_join", "true")  
                time.sleep(3)

                # check current pairing setting
                zigbee_check = False
                
                for message in MQTT_GET_INCOMING_MESSAGES(5):
                    
                    if message[1] == "SmartHome/zigbee2mqtt/bridge/config" and message[2] == '{"log_level":"info","permit_join":true}':
                        zigbee_check = True
                        
                if zigbee_check == True:             
                    WRITE_LOGFILE_SYSTEM("WARNING", "ZigBee2MQTT | Pairing enabled") 
                else:             
                    WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | Pairing enabled | Setting not confirmed")                             
                     
        else:
            
            # check current pairing setting
            zigbee_check = False
            
            for message in MQTT_GET_INCOMING_MESSAGES(5):
                
                if message[1] == "SmartHome/zigbee2mqtt/bridge/config" and message[2] == '{"log_level":"info","permit_join":false}':
                    zigbee_check = True
                    
            # current setting wrong
            if zigbee_check == True:              
            
                MQTT_PUBLISH("SmartHome/zigbee2mqtt/bridge/config/permit_join", "false")
                time.sleep(3)

                # check current pairing setting
                zigbee_check = False
                
                for message in MQTT_GET_INCOMING_MESSAGES(5):
                    
                    if message[1] == "SmartHome/zigbee2mqtt/bridge/config" and message[2] == '{"log_level":"info","permit_join":true}':
                        zigbee_check = True
                        
                if zigbee_check == True:             
                    WRITE_LOGFILE_SYSTEM("EVENT", "ZigBee2MQTT | Pairing disabled") 
                else:             
                    WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | Pairing disabled | Setting not confirmed")    
                
                
    else:
        print("ERROR: ZigBee2MQTT | No connection | " + str(zigbee_connection)) 
        
        WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | No Connection")        
        SEND_EMAIL("ERROR", "ZigBee2MQTT | No Connection")          


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
            print("ERROR: SnowBoy | " + str(e))
            WRITE_LOGFILE_SYSTEM("ERROR", "Snowboy | " + str(e)) 
            SEND_EMAIL("ERROR", "Snowboy | " + str(e)) 

    # deactivate pixel_ring
    MICROPHONE_LED_CONTROL(GET_SNOWBOY_SETTINGS().snowboy_microphone, "off")
