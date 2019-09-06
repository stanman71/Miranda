from flask import render_template, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps
from ping3 import ping

import os
import datetime
import json
import sys
import spotipy
import threading

from app import app
from app.components.backend_led import *
from app.database.database import *
from app.components.file_management import *
from app.components.email import SEND_EMAIL
from app.components.mqtt import *
from app.components.checks import *
from app.components.shared_resources import GET_ERROR_DELETE_MQTT_DEVICE, SET_ERROR_DELETE_MQTT_DEVICE
from app.components.backend_spotify import GET_SPOTIFY_TOKEN


# access rights
def permission_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.permission_system == "checked":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('logout'))
    return wrap
    

""" ############### """
""" host settings """
""" ############### """

def GET_CPU_TEMPERATURE():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n"," C"))


def CHECK_IP_ADDRESS(ip_address):
    try:
        for element in ip_address:
            if not element.isdigit() and element != ".":
                return False
              
        if len(ip_address.split(".")) != 4:
            return False
        
        for element in ip_address.split("."):
            if not 0 <= int(element) <= 254:
                return False
            
        return True
    
    except:
        return False
  
  
def PING_IP_ADDRESS(ip_address):
    try:
    
        if ping(ip_address, timeout=1) != None:
            return True
        if ping(ip_address, timeout=1) != None:
            return True

        return False
    
    except:
        return False


def HOST_REBOOT():
    time.sleep(10)
    os.system("sudo shutdown -r now")


def HOST_SHUTDOWN():
    time.sleep(10)
    os.system("sudo shutdown -h now")


@app.route('/system/host', methods=['GET', 'POST'])
@login_required
@permission_required
def system_host():
    error_message_host_settings = []
    
    message_shutdown         = "" 
    message_ip_config_change = False

    if request.method == "POST":   
          
        # ###############
        # start / restart
        # ###############             
          
        # restart raspi 
        if request.form.get("restart") != None:
            Thread = threading.Thread(target=HOST_REBOOT)
            Thread.start()    
            message_shutdown = "System wird in 10 Sekunden neugestartet"
            
        # shutdown raspi 
        if request.form.get("shutdown") != None:
            Thread = threading.Thread(target=HOST_SHUTDOWN)
            Thread.start()    
            message_shutdown = "System wird in 10 Sekunden heruntergefahren"
                   
 
        # ################
        # network settings
        # ################    
                   
        if request.form.get("change_host_settings") != None:
            
            save_input = True

            # check dhcp
            
            if request.form.get("set_lan_dhcp"):
                lan_dhcp = "checked" 
            else:
                lan_dhcp = ""            
            
            if request.form.get("set_wlan_dhcp"):
                wlan_dhcp = "checked" 
            else:
                wlan_dhcp = ""               

            lan_ip_address    = GET_HOST_NETWORK().lan_ip_address
            lan_gateway       = GET_HOST_NETWORK().lan_gateway  
            wlan_ip_address   = GET_HOST_NETWORK().wlan_ip_address
            wlan_gateway      = GET_HOST_NETWORK().wlan_gateway 


            # no dhcp ?
            
            if lan_dhcp != "checked" or wlan_dhcp != "checked":

                # lan
            
                if lan_dhcp != "checked":
                    
                    if request.form.get("set_lan_ip_address") != None:
                        lan_ip_address  = request.form.get("set_lan_ip_address")
                        
                    if request.form.get("set_lan_gateway") != None:
                        lan_gateway     = request.form.get("set_lan_gateway")            

                    if CHECK_IP_ADDRESS(lan_ip_address) == False:
                        error_message_host_settings.append("Ungültige LAN IP-Adresse angegeben")
                        save_input = False
                    
                    if PING_IP_ADDRESS(lan_ip_address) == True and lan_ip_address != GET_HOST_NETWORK().lan_ip_address:
                        error_message_host_settings.append("LAN IP-Adresse bereits vergeben")
                        save_input = False
                    
                    if CHECK_IP_ADDRESS(lan_gateway) == False:
                        error_message_host_settings.append("Ungültiges LAN Gateway angegeben")
                        save_input = False
                        
                    if CHECK_IP_ADDRESS(lan_gateway) == True and PING_IP_ADDRESS(lan_gateway) == False:
                        error_message_host_settings.append("LAN Gateway nicht gefunden")
                        save_input = False

                # wlan
                
                if wlan_dhcp != "checked":                    
                        
                    if request.form.get("set_wlan_ip_address") != None:
                        wlan_ip_address  = request.form.get("set_wlan_ip_address")
                        
                    if request.form.get("set_wlan_gateway") != None:
                        wlan_gateway     = request.form.get("set_wlan_gateway")   
                                                
                    if CHECK_IP_ADDRESS(wlan_ip_address) == False:
                        error_message_host_settings.append("Ungültige WLAN IP-Adresse angegeben")
                        save_input = False
                    
                    if PING_IP_ADDRESS(wlan_ip_address) == True and wlan_ip_address != GET_HOST_NETWORK().wlan_ip_address:
                        error_message_host_settings.append("WLAN IP-Adresse bereits vergeben")
                        save_input = False
                    
                    if CHECK_IP_ADDRESS(wlan_gateway) == False:
                        error_message_host_settings.append("Ungültiges WLAN Gateway angegeben")
                        save_input = False

                    if CHECK_IP_ADDRESS(wlan_gateway) == True and PING_IP_ADDRESS(wlan_gateway) == False:
                        error_message_host_settings.append("WLAN Gateway nicht gefunden")
                        save_input = False

                
                # lan + wlan
                
                if lan_dhcp != "checked" and wlan_dhcp != "checked":                     
                    
                    if lan_ip_address == "" and wlan_ip_address == "":
                        error_message_host_settings.append("Keine IP-Adresse angegeben")
                        save_input = False
                        
                    if lan_ip_address == wlan_ip_address:
                        error_message_host_settings.append("Gleiche IP-Adressen (LAN + WLAN) angegeben")
                        save_input = False


            # wlan credentials              
                
            wlan_ssid       = request.form.get("set_wlan_ssid")
            wlan_password   = request.form.get("set_wlan_password")    
                
            if wlan_ssid == "" or wlan_password == "":
                error_message_host_settings.append("WLAN Zugangsdaten unvollständig")
                save_input = False                    
            
            
            # default interface
            
            default_interface = request.form.get("set_default_interface")
            
            if (default_interface == "LAN" and (lan_ip_address == "" or lan_gateway == "" or
                CHECK_IP_ADDRESS(lan_ip_address) == False or CHECK_IP_ADDRESS(lan_gateway) == False)):
                
                error_message_host_settings.append("Unvollständige Angeben LAN-Netzwerk")
                default_interface = GET_HOST_NETWORK().default_interface
                save_input = False
            
            if (default_interface == "WLAN" and (wlan_ip_address == "" or wlan_gateway == "" or
                CHECK_IP_ADDRESS(wlan_ip_address) == False or CHECK_IP_ADDRESS(wlan_gateway) == False)):
                
                error_message_host_settings.append("Unvollständige Angeben WLAN-Netzwerk")
                default_interface = GET_HOST_NETWORK().default_interface
                save_input = False


            # port
            
            port = request.form.get("set_port") 
            
            if port == "":
                error_message_host_settings.append("Keinen Port angegeben")
                save_input = False
                
            if port.isdigit() == False:
                error_message_host_settings.append("Ungültigen Port angegeben (Zahl von 0 bis 65535)")
                save_input = False
                
            if not 0 <= int(port) <= 65535:
                error_message_host_settings.append("Ungültigen Port angegeben (Zahl von 0 bis 65535)")
                save_input = False           
              
              
            # save settings  
              
            if save_input == True:
                SET_HOST_NETWORK(lan_ip_address, lan_gateway, wlan_ip_address, wlan_gateway)
                UPDATE_NETWORK_SETTINGS_FILE(lan_dhcp, lan_ip_address, lan_gateway, wlan_dhcp, wlan_ip_address, wlan_gateway)
                
                SET_WLAN_CREDENTIALS(wlan_ssid, wlan_password)
                UPDATE_WLAN_CREDENTIALS_FILE(wlan_ssid, wlan_password)
                
                SET_HOST_DHCP(lan_dhcp, wlan_dhcp)
                SET_HOST_DEFAULT_INTERFACE(default_interface)  
                SET_HOST_PORT(port)        
        
                message_ip_config_change = True
               
        
    cpu_temperature             = GET_CPU_TEMPERATURE()
    dropdown_default_interfaces = ["LAN", "WLAN"]
 
    lan_dhcp          = GET_HOST_NETWORK().lan_dhcp
    lan_ip_address    = GET_HOST_NETWORK().lan_ip_address
    lan_gateway       = GET_HOST_NETWORK().lan_gateway
    wlan_dhcp         = GET_HOST_NETWORK().wlan_dhcp  
    wlan_ip_address   = GET_HOST_NETWORK().wlan_ip_address
    wlan_gateway      = GET_HOST_NETWORK().wlan_gateway
    wlan_ssid         = GET_HOST_NETWORK().wlan_ssid
    wlan_password     = GET_HOST_NETWORK().wlan_password    
    default_interface = GET_HOST_NETWORK().default_interface
    port              = GET_HOST_NETWORK().port       
 

    if (wlan_ssid != "" or wlan_password != "") and wlan_ip_address == "":
        error_message_host_settings.append("Falsche WLAN Zugangsdaten eingegeben")
        
 
    return render_template('system_host.html',
                            error_message_host_settings=error_message_host_settings,
                            message_shutdown=message_shutdown,
                            message_ip_config_change=message_ip_config_change,
                            cpu_temperature=cpu_temperature,
                            lan_dhcp=lan_dhcp,
                            lan_ip_address=lan_ip_address,
                            lan_gateway=lan_gateway,
                            wlan_dhcp=wlan_dhcp,
                            wlan_ip_address=wlan_ip_address,
                            wlan_gateway=wlan_gateway,
                            wlan_ssid=wlan_ssid,
                            wlan_password=wlan_password,                           
                            default_interface=default_interface,
                            port=port,
                            dropdown_default_interfaces=dropdown_default_interfaces,
                           
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system, 
                            )



""" ##################### """
""" device administration """
""" ##################### """

# dashboard email settings
@app.route('/system/device_administration', methods=['GET', 'POST'])
@login_required
@permission_required
def system_device_administration():
    error_message = ""

    # exception sensor name changed ?
    UPDATE_DEVICE_EXCEPTION_SENSOR_NAMES()

    
    if request.method == "POST":
    
        if request.form.get("change_device_settings") != None:  
            
            for i in range (1,21):
                
                try:
                        
                    device = GET_MQTT_DEVICE_BY_ID(i)
                    
                    if device in GET_ALL_MQTT_DEVICES("device"):
                        
                        
                        # ####################
                        #   Exception Options
                        # ####################

                        exception_option  = request.form.get("set_exception_option_" + str(i))
                        exception_option  = exception_option.replace(" ","")
                        exception_setting = request.form.get("set_exception_setting_" + str(i))
                                               
                        if exception_setting == "" or exception_setting == None:
                            exception_setting = "None"  
          
                        # ######
                        # Sensor
                        # ######

                        if GET_MQTT_DEVICE_BY_NAME(exception_option) or exception_option.isdigit(): 

                            if exception_option.isdigit():        
                                exception_sensor_ieeeAddr     = GET_MQTT_DEVICE_BY_ID(exception_option).ieeeAddr
                                exception_sensor_input_values = GET_MQTT_DEVICE_BY_ID(exception_option).input_values       
                                exception_option              = GET_MQTT_DEVICE_BY_ID(exception_option).name
                                
                            else:
                                exception_sensor_ieeeAddr     = GET_MQTT_DEVICE_BY_NAME(exception_option).ieeeAddr
                                exception_sensor_input_values = GET_MQTT_DEVICE_BY_NAME(exception_option).input_values                                  
                        
                            # set device exception value 1
                            if device.exception_option == "IP-Address":
                                exception_value_1 = "None" 
                        
                            else:
                                exception_value_1 = request.form.get("set_exception_value_1_" + str(i))

                                if exception_value_1 != None:                  
                                    exception_value_1 = exception_value_1.replace(" ", "")

                                    # replace array_position to sensor name 
                                    if exception_value_1.isdigit():
                                        
                                        # first two array elements are no sensors
                                        if exception_value_1 == "0" or exception_value_1 == "1":
                                            exception_value_1 = "None"
                                            
                                        else:           
                                            sensor_list       = GET_MQTT_DEVICE_BY_IEEEADDR(exception_sensor_ieeeAddr).input_values
                                            sensor_list       = sensor_list.split(",")
                                            exception_value_1 = sensor_list[int(exception_value_1)-2]
                                            
                                else:
                                   exception_value_1 = "None" 


                            # set device exception value 2
                            exception_value_2 = request.form.get("set_exception_value_2_" + str(i))
                            
                            if exception_value_2 == "" or exception_value_2 == None:
                                exception_value_2 = "None"       
                            
                            
                            # set device exception value 3
                            exception_value_3 = request.form.get("set_exception_value_3_" + str(i))
                            
                            if exception_value_3 == "" or exception_value_3 == None:
                                exception_value_3 = "None"       


                        # ##########
                        # IP Address
                        # ##########

                        elif exception_option == "IP-Address":
                            
                            # set device exception value 1
                            exception_value_1 = request.form.get("set_exception_value_1_" + str(i))
                           
                            if exception_value_1 == "" or exception_value_1 == None:
                                exception_value_1 = "None" 
                                  
                            exception_sensor_ieeeAddr     = "None"
                            exception_sensor_input_values = "None"
                            exception_value_2             = "None"                        
                            exception_value_3             = "None"   
               
                                                              
                        else:
                            
                            exception_option              = "None" 
                            exception_value_1             = "None" 
                            exception_value_2             = "None"  
                            exception_value_3             = "None"  
                            exception_sensor_ieeeAddr     = "None"
                            exception_sensor_input_values = "None"                                                            

                        SET_MQTT_DEVICE_EXCEPTION(device.ieeeAddr, exception_option, exception_setting,
                                                            exception_sensor_ieeeAddr, exception_sensor_input_values,
                                                            exception_value_1, exception_value_2, exception_value_3)
                    
                    
                    else:
                        
                        if exception_option == "None":
                        
                            exception_setting             = "None" 
                            exception_value_1             = "None" 
                            exception_value_2             = "None"  
                            exception_value_3             = "None"  
                            exception_sensor_ieeeAddr     = "None"
                            exception_sensor_input_values = "None"                                                            

                            SET_MQTT_DEVICE_EXCEPTION(device.ieeeAddr, exception_option, exception_setting, exception_sensor_ieeeAddr,
                                                      exception_sensor_input_values, exception_value_1, exception_value_2, exception_value_3)                   
                
                except Exception as e:
                    if "NoneType" not in str(e):
                        print(e)                        
 

    dropdown_list_exception_options = ["IP-Address"] 
    dropdown_list_operators         = ["=", ">", "<"]
    
    list_devices = GET_ALL_MQTT_DEVICES("device")
    list_sensors = GET_ALL_MQTT_DEVICES("sensor")    

    error_message_exceptions = CHECK_DEVICE_EXCEPTION_SETTINGS(GET_ALL_MQTT_DEVICES("device")) 
 
    # get sensor list
    try:
        mqtt_device_1_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(1).input_values
        mqtt_device_1_input_values = mqtt_device_1_input_values.replace(" ", "")
    except:
        mqtt_device_1_input_values = ""
    try:
        mqtt_device_2_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(2).input_values
        mqtt_device_2_input_values = mqtt_device_2_input_values.replace(" ", "")
    except:
        mqtt_device_2_input_values = ""
    try:        
        mqtt_device_3_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(3).input_values
        mqtt_device_3_input_values = mqtt_device_3_input_values.replace(" ", "")
    except:
        mqtt_device_3_input_values = ""
    try:        
        mqtt_device_4_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(4).input_values
        mqtt_device_4_input_values = mqtt_device_4_input_values.replace(" ", "")
    except:
        mqtt_device_4_input_values = ""
    try:        
        mqtt_device_5_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(5).input_values
        mqtt_device_5_input_values = mqtt_device_5_input_values.replace(" ", "")
    except:
        mqtt_device_5_input_values = ""
    try:        
        mqtt_device_6_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(6).input_values
        mqtt_device_6_input_values = mqtt_device_6_input_values.replace(" ", "")
    except:
        mqtt_device_6_input_values = ""
    try:        
        mqtt_device_7_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(7).input_values
        mqtt_device_7_input_values = mqtt_device_7_input_values.replace(" ", "")
    except:
        mqtt_device_7_input_values = ""
    try:        
        mqtt_device_8_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(8).input_values
        mqtt_device_8_input_values = mqtt_device_8_input_values.replace(" ", "")
    except:
        mqtt_device_8_input_values = ""
    try:        
        mqtt_device_9_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(9).input_values
        mqtt_device_9_input_values = mqtt_device_9_input_values.replace(" ", "")
    except:
        mqtt_device_9_input_values = ""
    try:        
        mqtt_device_10_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(10).input_values
        mqtt_device_10_input_values = mqtt_device_10_input_values.replace(" ", "")
    except:
        mqtt_device_10_input_values = ""
    try:        
        mqtt_device_11_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(11).input_values
        mqtt_device_11_input_values = mqtt_device_11_input_values.replace(" ", "")
    except:
        mqtt_device_11_input_values = ""
    try:        
        mqtt_device_12_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(12).input_values
        mqtt_device_12_input_values = mqtt_device_12_input_values.replace(" ", "")
    except:
        mqtt_device_12_input_values = ""
    try:        
        mqtt_device_13_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(13).input_values
        mqtt_device_13_input_values = mqtt_device_13_input_values.replace(" ", "")
    except:
        mqtt_device_13_input_values = ""
    try:        
        mqtt_device_14_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(14).input_values
        mqtt_device_14_input_values = mqtt_device_14_input_values.replace(" ", "")
    except:
        mqtt_device_14_input_values = ""
    try:        
        mqtt_device_15_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(15).input_values
        mqtt_device_15_input_values = mqtt_device_15_input_values.replace(" ", "")
    except:
        mqtt_device_15_input_values = ""    
    try:        
        mqtt_device_16_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(16).input_values
        mqtt_device_16_input_values = mqtt_device_16_input_values.replace(" ", "")
    except:
        mqtt_device_16_input_values = ""
    try:        
        mqtt_device_17_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(17).input_values
        mqtt_device_17_input_values = mqtt_device_17_input_values.replace(" ", "")
    except:
        mqtt_device_17_input_values = ""
    try:        
        mqtt_device_18_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(18).input_values
        mqtt_device_18_input_values = mqtt_device_18_input_values.replace(" ", "")
    except:
        mqtt_device_18_input_values = ""
    try:        
        mqtt_device_19_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(19).input_values
        mqtt_device_19_input_values = mqtt_device_19_input_values.replace(" ", "")
    except:
        mqtt_device_19_input_values = ""
    try:        
        mqtt_device_20_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(20).input_values
        mqtt_device_20_input_values = mqtt_device_20_input_values.replace(" ", "")
    except:
        mqtt_device_20_input_values = ""   
    try:        
        mqtt_device_21_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(21).input_values
        mqtt_device_21_input_values = mqtt_device_21_input_values.replace(" ", "")
    except:
        mqtt_device_21_input_values = ""   
    try:        
        mqtt_device_22_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(22).input_values
        mqtt_device_22_input_values = mqtt_device_22_input_values.replace(" ", "")
    except:
        mqtt_device_22_input_values = ""   
    try:        
        mqtt_device_23_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(23).input_values
        mqtt_device_23_input_values = mqtt_device_23_input_values.replace(" ", "")
    except:
        mqtt_device_23_input_values = ""   
    try:        
        mqtt_device_24_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(24).input_values
        mqtt_device_24_input_values = mqtt_device_24_input_values.replace(" ", "")
    except:
        mqtt_device_24_input_values = ""   
    try:        
        mqtt_device_25_input_values = "None,-----------------------------------," + GET_MQTT_DEVICE_BY_ID(25).input_values
        mqtt_device_25_input_values = mqtt_device_25_input_values.replace(" ", "")
    except:
        mqtt_device_25_input_values = ""
        

    return render_template('system_device_administration.html',
                            error_message=error_message,
                            error_message_exceptions=error_message_exceptions,                           
                            dropdown_list_exception_options=dropdown_list_exception_options,
                            dropdown_list_operators=dropdown_list_operators,
                            list_devices=list_devices,
                            list_sensors=list_sensors,
                           
                            mqtt_device_1_input_values=mqtt_device_1_input_values,
                            mqtt_device_2_input_values=mqtt_device_2_input_values,
                            mqtt_device_3_input_values=mqtt_device_3_input_values,
                            mqtt_device_4_input_values=mqtt_device_4_input_values,
                            mqtt_device_5_input_values=mqtt_device_5_input_values,
                            mqtt_device_6_input_values=mqtt_device_6_input_values,
                            mqtt_device_7_input_values=mqtt_device_7_input_values,
                            mqtt_device_8_input_values=mqtt_device_8_input_values,
                            mqtt_device_9_input_values=mqtt_device_9_input_values,
                            mqtt_device_10_input_values=mqtt_device_10_input_values,
                            mqtt_device_11_input_values=mqtt_device_11_input_values,
                            mqtt_device_12_input_values=mqtt_device_12_input_values,
                            mqtt_device_13_input_values=mqtt_device_13_input_values,
                            mqtt_device_14_input_values=mqtt_device_14_input_values,
                            mqtt_device_15_input_values=mqtt_device_15_input_values,
                            mqtt_device_16_input_values=mqtt_device_16_input_values,
                            mqtt_device_17_input_values=mqtt_device_17_input_values,
                            mqtt_device_18_input_values=mqtt_device_18_input_values,
                            mqtt_device_19_input_values=mqtt_device_19_input_values,
                            mqtt_device_20_input_values=mqtt_device_20_input_values,  
                            mqtt_device_21_input_values=mqtt_device_21_input_values,
                            mqtt_device_22_input_values=mqtt_device_22_input_values,  
                            mqtt_device_23_input_values=mqtt_device_23_input_values,
                            mqtt_device_24_input_values=mqtt_device_24_input_values,
                            mqtt_device_25_input_values=mqtt_device_25_input_values,
                           
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system,                            
                            )


""" ############# """
""" mqtt settings """
""" ############# """

@app.route('/system/mqtt', methods=['GET', 'POST'])
@login_required
@permission_required
def system_mqtt():   
    error_message = ""
    error_message_mqtt = ""
    error_message_change_settings = ""
    
    broker   = GET_MQTT_BROKER_SETTINGS().broker    
    user     = GET_MQTT_BROKER_SETTINGS().user
    password = GET_MQTT_BROKER_SETTINGS().password
    
    mqtt_device_name       = ""   
    check_value_mqtt       = ["", ""]
    collapse_mqtt_settings = ""
    collapse_mqtt_log      = ""

    # get mqtt device delete errors
    if GET_ERROR_DELETE_MQTT_DEVICE() != "":
        error_message_change_settings = GET_ERROR_DELETE_MQTT_DEVICE()
        SET_ERROR_DELETE_MQTT_DEVICE("")
        
    
    if request.method == "POST":     
        # change mqtt settings   
        if request.form.get("set_setting_mqtt") != None:
            setting_mqtt = str(request.form.get("radio_mqtt"))
            SET_GLOBAL_SETTING_VALUE("mqtt", setting_mqtt)


    # change radio check  
    mqtt_setting = GET_GLOBAL_SETTING_VALUE("mqtt")    
    if mqtt_setting == "True":
        check_value_mqtt[0] = "checked = 'on'"
        check_value_mqtt[1] = ""
    else:
        check_value_mqtt[0] = ""
        check_value_mqtt[1] = "checked = 'on'"


    if mqtt_setting == "True":

        # check mqtt
        try:
            CHECK_MQTT()
        except Exception as e:
            error_message_mqtt = "Fehler in MQTT: " + str(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "MQTT | " + str(e)) 
            SEND_EMAIL("ERROR", "MQTT | " + str(e)) 


        # change table settings
        if request.form.get("change_table_settings") != None:  

            for i in range (1,26):
                if request.form.get("set_name_" + str(i)) != "" and request.form.get("set_name_" + str(i)) != None:
                                
                    # rename devices                   
                    new_name = request.form.get("set_name_" + str(i))
                    old_name = GET_MQTT_DEVICE_BY_ID(i).name

                    if new_name != old_name:          
                        if not GET_MQTT_DEVICE_BY_NAME(new_name):  
                            ieeeAddr = GET_MQTT_DEVICE_BY_ID(i).ieeeAddr                  
                            SET_MQTT_DEVICE_NAME(ieeeAddr, new_name)                         
                        else: 
                            error_message_change_settings = "Name bereits vergeben >>> " + new_name


        # update device list
        if request.form.get("update_mqtt_devices") != None:
            error_message_change_settings = UPDATE_MQTT_DEVICES("mqtt")
            

        # save mqtt broker setting
        if request.form.get("save_general_settings") is not None:
                          
            collapse_mqtt_settings = "in"

            broker   = request.form.get("set_broker")
            user     = request.form.get("set_user")
            password = request.form.get("set_password")
            
            SET_MQTT_BROKER_SETTINGS(broker, user, password)

            mqtt_update_hour   = request.form.get("get_mqtt_update_hour")
            mqtt_update_minute = request.form.get("get_mqtt_update_minute")

            mqtt_update_task = GET_SCHEDULER_TASK_BY_NAME("mqtt_update")
            
            if mqtt_update_task == None:
                ADD_SCHEDULER_TASK("mqtt_update", "no_scheduler_task")
                mqtt_update_task = GET_SCHEDULER_TASK_BY_NAME("mqtt_update")
                
            i = mqtt_update_task.id
                
            SET_SCHEDULER_TASK(i, "mqtt_update", "mqtt_update_devices", 
                                  "checked", "None", "None", "None", "checked", 
                                  "*", mqtt_update_hour, mqtt_update_minute,
                                  "None", "None", "None",
                                  "None", "None", "None", 
                                  "None", "None", "None", "None",
                                  "None", "None", "None", 
                                  "None", "None", "None", "None",
                                  "None", "None", "None", 
                                  "None", "None", "None",
                                  "None", "None", "None")                    
                 

        # reset logfile
        if request.form.get("reset_logfile") != None: 
            RESET_LOGFILE("log_mqtt")   
            
            
    mqtt_device_list = GET_ALL_MQTT_DEVICES("mqtt")
    
    if GET_SCHEDULER_TASK_BY_NAME("mqtt_update") != None:
        mqtt_update_hour   = GET_SCHEDULER_TASK_BY_NAME("mqtt_update").hour
        mqtt_update_minute = GET_SCHEDULER_TASK_BY_NAME("mqtt_update").minute
    else:
        mqtt_update_hour   = "Stunde"        
        mqtt_update_minute = "Minute"
   
    dropdown_list_hours   = [ "*", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24] 
                                 
    dropdown_list_minutes = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 
                             21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 
                             41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59]    
    
    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 

    return render_template('system_mqtt.html',                    
                            error_message=error_message,
                            error_message_mqtt=error_message_mqtt,
                            error_message_change_settings=error_message_change_settings,
                            broker=broker,
                            user=user,
                            password=password,                           
                            mqtt_update_hour=mqtt_update_hour,
                            mqtt_update_minute=mqtt_update_minute,
                            dropdown_list_hours=dropdown_list_hours,
                            dropdown_list_minutes=dropdown_list_minutes,
                            mqtt_device_name=mqtt_device_name,
                            mqtt_setting=mqtt_setting,
                            check_value_mqtt=check_value_mqtt,
                            mqtt_device_list=mqtt_device_list,
                            collapse_mqtt_settings=collapse_mqtt_settings,
                            collapse_mqtt_log=collapse_mqtt_log,
                            timestamp=timestamp,
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system, 
                            )
     

# change mqtt device position 
@app.route('/system/mqtt/position/<string:direction>/<string:device_type>/<int:id>')
@login_required
@permission_required
def change_mqtt_device_position(id, direction, device_type):
    CHANGE_MQTT_DEVICE_POSITION(id, device_type, direction)
    return redirect(url_for('system_mqtt'))


# remove mqtt device
@app.route('/system/mqtt/delete/<string:ieeeAddr>')
@login_required
@permission_required
def remove_mqtt_device(ieeeAddr):
    device_name = GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr).name
    result      = DELETE_MQTT_DEVICE(ieeeAddr) 
    
    if result != True:
        SET_ERROR_DELETE_MQTT_DEVICE(result)
        
    return redirect(url_for('system_mqtt'))
     
     
# download mqtt logfile
@app.route('/system/mqtt/download/<path:filepath>')
@login_required
@permission_required
def download_mqtt_logfile(filepath): 
    try:
        path = GET_PATH() + "/logs/"     
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /logs/" + filepath + " | downloaded")
        return send_from_directory(path, filepath)
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/" + filepath + " | " + str(e))
             

""" #################### """
""" zigbee2mqtt settings """
""" #################### """

@app.route('/system/zigbee2mqtt', methods=['GET', 'POST'])
@login_required
@permission_required
def system_zigbee2mqtt():
    error_message = ""
    error_message_zigbee2mqtt = ""
    error_message_change_settings = ""
    error_message_zigbee2mqtt_pairing = ""
    
    check_value_zigbee2mqtt       = ["", ""]
    check_value_pairing           = ["", ""]
    zigbee_topology_show          = False
    collapse_zigbee2mqtt_settings = ""
    collapse_zigbee2mqtt_topology = ""    
    collapse_zigbee2mqtt_log      = ""


    # get zigbee2mqtt device delete errors
    if GET_ERROR_DELETE_MQTT_DEVICE() != "":
        error_message_change_settings = GET_ERROR_DELETE_MQTT_DEVICE()
        SET_ERROR_DELETE_MQTT_DEVICE("")

    if request.method == "POST":  
           
        # change mqtt settings   
        if request.form.get("set_setting_zigbee2mqtt") is not None:
            setting_zigbee2mqtt = str(request.form.get("radio_zigbee2mqtt"))
            SET_GLOBAL_SETTING_VALUE("zigbee2mqtt", setting_zigbee2mqtt)

    # change radio check  
    zigbee2mqtt_setting = GET_GLOBAL_SETTING_VALUE("zigbee2mqtt")    
    
    if zigbee2mqtt_setting == "True":
        check_value_zigbee2mqtt[0] = "checked = 'on'"
        check_value_zigbee2mqtt[1] = ""
    else:
        check_value_zigbee2mqtt[0] = ""
        check_value_zigbee2mqtt[1] = "checked = 'on'"


    if zigbee2mqtt_setting == "True":
        
        error_message_zigbee2mqtt = MQTT_PUBLISH("miranda/zigbee2mqtt/bridge/config/", "")
        
        if request.method == 'POST':

            # change name
            if request.form.get("change_settings") != None:
                
                for i in range (1,26):

                    if (request.form.get("set_name_" + str(i)) != "" and request.form.get("set_name_" + str(i)) != None):
                            
                        new_name = request.form.get("set_name_" + str(i))
                        old_name = GET_MQTT_DEVICE_BY_ID(i).name 
                        
                        if new_name != old_name:
                        
                            # name already exist
                            if not GET_MQTT_DEVICE_BY_NAME(new_name):

                                # no connection to mqtt
                                if MQTT_PUBLISH("miranda/zigbee2mqtt/bridge/config/rename", 
                                                '{"old": "' + old_name + '", "new": "' + new_name + '"}') != "Keine Verbindung zu MQTT":

                                    time.sleep(3)

                                    # error in zigbee2mqtt
                                    if CHECK_MQTT_NAME_CHANGED():       
                                        ieeeAddr = GET_MQTT_DEVICE_BY_ID(i).ieeeAddr                  
                                        SET_MQTT_DEVICE_NAME(ieeeAddr, new_name)  

                                    else:
                                        error_message_change_settings = "Name konnte in ZigBee2MQTT nicht verändert werden"
                                        UPDATE_MQTT_DEVICES("zigbee2mqtt")

                                else:
                                    error_message_change_settings = "Ohne eine Verbindung zu MQTT können die Namen der Geräte nicht verändert werden !"
                                
                            else:
                                error_message_change_settings = "Name bereits vergeben >>> " + new_name

            # update device list
            if request.form.get("update_zigbee2mqtt_devices") != None:
                error_message_change_settings = UPDATE_MQTT_DEVICES("zigbee2mqtt")


            def DISABLE_ZIGBEE_PAIRING():
                
                time.sleep(1800)
                
                SET_ZIGBEE2MQTT_PAIRING("false")
                
                MQTT_PUBLISH("miranda/zigbee2mqtt/bridge/config/permit_join", "false")
                time.sleep(1)

                zigbee_check = CHECK_ZIGBEE2MQTT_SETTING_PROCESS("bridge/config", '"permit_join":false', 1, 5)
                
                if zigbee_check == "":                
                    WRITE_LOGFILE_SYSTEM("SUCCESS", "ZigBee2MQTT | Pairing disabled") 
                else:             
                    WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | Pairing disabled | Setting not confirmed")  


            # change pairing setting
            if request.form.get("set_pairing") != None: 
                
                collapse_zigbee2mqtt_settings = "in"
                
                setting_pairing = str(request.form.get("radio_pairing"))
                SET_ZIGBEE2MQTT_PAIRING(setting_pairing)

                if setting_pairing == "True":
                        
                    MQTT_PUBLISH("miranda/zigbee2mqtt/bridge/config/permit_join", "true")
                    Thread = threading.Thread(target=DISABLE_ZIGBEE_PAIRING)
                    Thread.start()                      
                    time.sleep(1)

                    zigbee_check = CHECK_ZIGBEE2MQTT_SETTING_PROCESS("bridge/config", '"permit_join":true', 1, 5)
                    
                    if zigbee_check == "":             
                        WRITE_LOGFILE_SYSTEM("WARNING", "ZigBee2MQTT | Pairing enabled") 
                        SEND_EMAIL("WARNING", "ZigBee2MQTT | Pairing enabled")
                    else:             
                        WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | Pairing enabled | Setting not confirmed")   
                        error_message_zigbee2mqtt_pairing = "Pairing Einstellung nicht bestätigt"   
                                                
                else:
                    
                    MQTT_PUBLISH("miranda/zigbee2mqtt/bridge/config/permit_join", "false")
                    time.sleep(1)

                    zigbee_check = CHECK_ZIGBEE2MQTT_SETTING_PROCESS("bridge/config", '"permit_join":false', 1, 5)
                    
                    if zigbee_check == "":                
                        WRITE_LOGFILE_SYSTEM("SUCCESS", "ZigBee2MQTT | Pairing disabled") 
                    else:             
                        WRITE_LOGFILE_SYSTEM("ERROR", "ZigBee2MQTT | Pairing disabled | Setting not confirmed")  
                        error_message_zigbee2mqtt_pairing = "Pairing Einstellung nicht bestätigt"  


            # request zigbee topology
            if request.form.get("request_zigbee_topology") != None: 
                
                collapse_zigbee2mqtt_topology = "in"
                
                MQTT_PUBLISH("miranda/zigbee2mqtt/bridge/networkmap", "graphviz")
                zigbee_topology_show = True
                time.sleep(1)


            # reset logfile
            if request.form.get("reset_logfile") != None: 
                RESET_LOGFILE("log_zigbee2mqtt")
     
     
    # set pairing checkbox  
    pairing_setting = GET_ZIGBEE2MQTT_PAIRING()    
    
    if pairing_setting == "True":
        check_value_pairing[0] = "checked = 'on'"
        check_value_pairing[1] = ""        

    else:
        check_value_pairing[0] = ""
        check_value_pairing[1] = "checked = 'on'"        


    zigbee2mqtt_device_list = GET_ALL_MQTT_DEVICES("zigbee2mqtt")

    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return render_template('system_zigbee2mqtt.html',
                            error_message=error_message,
                            error_message_zigbee2mqtt=error_message_zigbee2mqtt,
                            error_message_change_settings=error_message_change_settings,
                            error_message_zigbee2mqtt_pairing=error_message_zigbee2mqtt_pairing,
                            check_value_zigbee2mqtt=check_value_zigbee2mqtt,  
                            check_value_pairing=check_value_pairing,
                            zigbee2mqtt_device_list=zigbee2mqtt_device_list, 
                            zigbee2mqtt_setting=zigbee2mqtt_setting, 
                            zigbee_topology_show=zigbee_topology_show,        
                            collapse_zigbee2mqtt_settings=collapse_zigbee2mqtt_settings,
                            collapse_zigbee2mqtt_topology=collapse_zigbee2mqtt_topology,  
                            collapse_zigbee2mqtt_log=collapse_zigbee2mqtt_log,                                   
                            timestamp=timestamp,
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system, 
                            )


# change zigbee2mqtt device position 
@app.route('/system/zigbee2mqtt/position/<string:direction>/<string:device_type>/<int:id>')
@login_required
@permission_required
def change_zigbee2mqtt_device_position(id, direction, device_type):
    CHANGE_MQTT_DEVICE_POSITION(id, device_type, direction)

    return redirect(url_for('system_zigbee2mqtt'))


# remove zigbee2mqtt device
@app.route('/system/zigbee2mqtt/delete/<string:ieeeAddr>')
@login_required
@permission_required
def remove_zigbee2mqtt_device(ieeeAddr):
    device_name = GET_MQTT_DEVICE_BY_IEEEADDR(ieeeAddr).name
    result      = DELETE_MQTT_DEVICE(ieeeAddr) 
    
    if result != True:
        SET_ERROR_DELETE_MQTT_DEVICE(result)
    else:
        MQTT_PUBLISH("miranda/zigbee2mqtt/bridge/config/remove", device_name) 
    
    return redirect(url_for('system_zigbee2mqtt'))


# download zigbee2mqtt logfile
@app.route('/system/zigbee2mqtt/download/<path:filepath>')
@login_required
@permission_required
def download_zigbee2mqtt_logfile(filepath): 
    try:
        path = GET_PATH() + "/logs/"     
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /logs/" + filepath + " | downloaded")
        return send_from_directory(path, filepath)
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/" + filepath + " | " + str(e))        


""" ############ """
"""  controller  """
""" ############ """

@app.route('/system/controller', methods=['GET', 'POST'])
@login_required
@permission_required
def system_controller():
    error_message_add_controller = ""
    error_message_controller_tasks = ""
    
    RESET_CONTROLLER_COLLAPSE()
    UPDATE_CONTROLLER_EVENTS()


    if request.method == "POST": 

        if request.form.get("add_controller") != None: 
            
            if request.form.get("set_mqtt_device_ieeeAddr") != None:
                mqtt_device_ieeeAddr         = request.form.get("set_mqtt_device_ieeeAddr")
                error_message_add_controller = ADD_CONTROLLER(mqtt_device_ieeeAddr)

            else:
                error_message_add_controller = "Keinen Controller angegeben"  
   
        if request.form.get("save_task_settings") != None: 

            for i in range (1,21):

                if request.form.get("set_task_1_" + str(i)) != None:
                    
                    SET_CONTROLLER_COLLAPSE(i)   

                    ### set tasks
                    if request.form.get("set_task_1_" + str(i)) != "":
                        task_1 = request.form.get("set_task_1_" + str(i))
                    else:
                        task_1 = "None"                   
                    if request.form.get("set_task_2_" + str(i)) != "":
                        task_2 = request.form.get("set_task_2_" + str(i))
                    else:
                        task_2 = "None"  
                    if request.form.get("set_task_3_" + str(i)) != "":
                        task_3 = request.form.get("set_task_3_" + str(i))
                    else:
                        task_3 = "None"  
                    if request.form.get("set_task_4_" + str(i)) != "":
                        task_4 = request.form.get("set_task_4_" + str(i))
                    else:
                        task_4 = "None"                   
                    if request.form.get("set_task_5_" + str(i)) != "":
                        task_5 = request.form.get("set_task_5_" + str(i))
                    else:
                        task_5 = "None"  
                    if request.form.get("set_task_6_" + str(i)) != "":
                        task_6 = request.form.get("set_task_6_" + str(i))
                    else:
                        task_6 = "None"  
                    if request.form.get("set_task_7_" + str(i)) != "":
                        task_7 = request.form.get("set_task_7_" + str(i))
                    else:
                        task_7 = "None"                   
                    if request.form.get("set_task_8_" + str(i)) != "":
                        task_8 = request.form.get("set_task_8_" + str(i))
                    else:
                        task_8 = "None"  
                    if request.form.get("set_task_9_" + str(i)) != "":
                        task_9 = request.form.get("set_task_9_" + str(i))
                    else:
                        task_9 = "None"  
                        
                    SET_CONTROLLER_TASKS(i, task_1, task_2, task_3, task_4, task_5, task_6, task_7, task_8, task_9)

                                                        
    error_message_controller_tasks = CHECK_TASKS(GET_ALL_CONTROLLER(), "controller")

    data_controller = GET_ALL_CONTROLLER()
    dropdown_list_controller = GET_ALL_MQTT_DEVICES("controller")
  
  
    # list device command option    
    list_device_command_options = []
    
    for device in GET_ALL_MQTT_DEVICES("device"):
        list_device_command_options.append((device.name, device.commands))
         
          
    # list spotify devices / playlists
    spotify_token = GET_SPOTIFY_TOKEN()    
    
    try:
        sp       = spotipy.Spotify(auth=spotify_token)
        sp.trace = False
        
        spotify_devices   = sp.devices()["devices"]        
        spotify_playlists = sp.current_user_playlists(limit=20)["items"]   
        
    except:
        spotify_devices   = ""       
        spotify_playlists = ""             
          
   
    return render_template('system_controller.html',
                            error_message_add_controller=error_message_add_controller,
                            error_message_controller_tasks=error_message_controller_tasks, 
                            data_controller=data_controller,
                            dropdown_list_controller=dropdown_list_controller, 
                            list_device_command_options=list_device_command_options,    
                            spotify_devices=spotify_devices,
                            spotify_playlists=spotify_playlists,                                                             
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system, 
                            )


# change controller position 
@app.route('/system/controller/position/<string:direction>/<int:id>')
@login_required
@permission_required
def change_controller_position(id, direction):
    CHANGE_CONTROLLER_POSITION(id, direction)
    return redirect(url_for('system_controller'))


# delete controller
@app.route('/system/controller/delete/<int:id>')
@login_required
@permission_required
def delete_controller(id):
    DELETE_CONTROLLER(id)
    return redirect(url_for('system_controller'))



""" ############### """
"""  speechcontrol  """
""" ############### """

@app.route('/system/speechcontrol', methods=['GET', 'POST'])
@login_required
@permission_required
def system_speechcontrol():
    error_message_snowboy = ""
    error_message_change_snowboy_settings = ""
    error_message_fileupload = ""
    error_message_hotword = ""
    error_message_speech_recognition_provider_keywords = ""
    error_message_add_speechcontrol_device_task = ""
    error_message_add_speechcontrol_program_task = ""  
    check_value_speechcontrol = ["", ""]
    snowboy_name = ""
    snowboy_task = ""   
    device_task  = ""
    program_task = ""    
    collapse_tasks_led              = ""
    collapse_tasks_devices          = ""
    collapse_tasks_programs         = ""
    collapse_tasks_spotify          = ""    
    collapse_speechcontrol_settings = ""
    collapse_fileupload             = ""
    

    if request.method == "POST":     
        # change speechcontrol global setting   
        if request.form.get("radio_speechcontrol") is not None:
            global_setting_speechcontrol = str(request.form.get("radio_speechcontrol"))
            SET_GLOBAL_SETTING_VALUE("speechcontrol", global_setting_speechcontrol) 

    # change radio check    
    if GET_GLOBAL_SETTING_VALUE("speechcontrol") == "True":
        check_value_speechcontrol[0] = "checked = 'on'"
        check_value_speechcontrol[1] = ""
    else:
        check_value_speechcontrol[0] = ""
        check_value_speechcontrol[1] = "checked = 'on'"


    ##################
    # general settings
    ##################

    if GET_GLOBAL_SETTING_VALUE("speechcontrol") == "True":

        # check snowboy
        def START_SNOWBOY():
            from app.speechcontrol.snowboy.snowboy import SNOWBOY_THREAD
            SNOWBOY_THREAD()
          
        try:
            START_SNOWBOY()
        except Exception as e:  
            if "signal only works in main thread" not in str(e):      
                error_message_snowboy = "Fehler in SnowBoy: " + str(e)
                WRITE_LOGFILE_SYSTEM("ERROR", "Snowboy | " + str(e)) 
                
        if request.method == 'POST':


            #########################
            # speechcontrol led tasks
            #########################
            
            if request.form.get("change_speechcontrol_led_tasks") != None: 
                
                collapse_tasks_led = "in"
               
                for i in range (1,26):
                    
                    if request.form.get("set_speechcontrol_led_task_keyword_" + str(i)) != None:

                        if request.form.get("set_speechcontrol_led_task_keyword_" + str(i)) != "":   
                            keywords = request.form.get("set_speechcontrol_led_task_keyword_" + str(i))    
                            
                        else:
                            keywords = "None"                
                                         
                        UPDATE_SPEECHCONTROL_LED_TASK(i, keywords)               


            ############################
            # speechcontrol device tasks
            ############################

            # add device task
            if request.form.get("add_speechcontrol_device_task") != None:

                collapse_tasks_devices = "in"

                # check name
                if (request.form.get("set_speechcontrol_device_task") != "" and 
                    GET_SPEECHCONTROL_DEVICE_TASK_BY_TASK(request.form.get("set_speechcontrol_device_task")) == None):
                    device_task = request.form.get("set_speechcontrol_device_task") 
                            
                    mqtt_device_ieeeAddr = request.form.get("set_speechcontrol_device_task_mqtt_device_ieeeAddr") 
                    
                    if mqtt_device_ieeeAddr != "None":
                        error_message_add_speechcontrol_device_task = ADD_SPEECHCONTROL_DEVICE_TASK(device_task, mqtt_device_ieeeAddr)  
                    else:
                        error_message_add_speechcontrol_device_task = "Kein Gerät ausgewählt"                                                   
                    
                else:
                    error_message_add_speechcontrol_device_task = "Ungültige Eingabe (leeres Feld / Name schon vergeben)"             


            # change speechcontrol device tasks
            if request.form.get("change_speechcontrol_device_tasks") != None: 
                for i in range (1,26):
                    
                    if request.form.get("set_speechcontrol_device_task_setting_" + str(i)) != None:  

                        collapse_tasks_devices = "in"
                    
                        if request.form.get("set_speechcontrol_device_task_setting_" + str(i)) != None:  
                            setting = request.form.get("set_speechcontrol_device_task_setting_" + str(i))
                        else:
                            setting = "None"
                            
                        if request.form.get("set_speechcontrol_device_task_keyword_" + str(i)) != "":  
                            keywords = request.form.get("set_speechcontrol_device_task_keyword_" + str(i))               
                        else:
                            keywords = "None"         
                                  
                        UPDATE_SPEECHCONTROL_DEVICE_TASK(i, setting, keywords)   
                       

            #############################
            # speechcontrol program tasks
            #############################

            # add program task
            if request.form.get("add_speechcontrol_program_task") != None:

                collapse_tasks_programs = "in"

                # check name
                if (request.form.get("set_speechcontrol_program_task") != "" and 
                    GET_SPEECHCONTROL_PROGRAM_TASK_BY_TASK(request.form.get("set_speechcontrol_program_task")) == None):
                    program_task = request.form.get("set_speechcontrol_program_task") 
                            
                    program_id = request.form.get("set_speechcontrol_program_task_program_id") 
                    
                    if program_id != "None":
                        error_message_add_speechcontrol_program_task = ADD_SPEECHCONTROL_PROGRAM_TASK(program_task, program_id) 
                    else:
                        error_message_add_speechcontrol_program_task = "Kein Programm ausgewählt"                      
                    
                else:
                    error_message_add_speechcontrol_program_task = "Ungültige Eingabe (leeres Feld / Name schon vergeben)"             


            # change speechcontrol program tasks
            if request.form.get("change_speechcontrol_program_tasks") != None: 
                for i in range (1,26):
                    
                    if request.form.get("set_speechcontrol_program_task_command_" + str(i)) != None: 
                        
                        collapse_tasks_programs = "in" 
                    
                        if request.form.get("set_speechcontrol_program_task_command_" + str(i)) != None:  
                            command = request.form.get("set_speechcontrol_program_task_command_" + str(i))
                        else:
                            command = "None"
                            
                        if request.form.get("set_speechcontrol_program_task_keyword_" + str(i)) != "":  
                            keywords = request.form.get("set_speechcontrol_program_task_keyword_" + str(i))               
                        else:
                            keywords = "None"         
                                  
                        UPDATE_SPEECHCONTROL_PROGRAM_TASK(i, command, keywords)   


            #############################
            # speechcontrol spotify tasks
            #############################
            
            if request.form.get("change_speechcontrol_spotify_tasks") != None: 
                
                collapse_tasks_spotify = "in"
               
                for i in range (1,26):
                    
                    if request.form.get("set_speechcontrol_spotify_task_keyword_" + str(i)) != None:

                        if request.form.get("set_speechcontrol_spotify_task_keyword_" + str(i)) != "":   
                            keywords = request.form.get("set_speechcontrol_spotify_task_keyword_" + str(i))    
                            
                        else:
                            keywords = "None"                
                                         
                        UPDATE_SPEECHCONTROL_SPOTIFY_TASK(i, keywords)     


            ########################
            # speechcontrol settings
            ########################

            if request.form.get("save_speechcontrol_settings") != None: 
                
                collapse_speechcontrol_settings = "in"
                
                
                # #################
                #  snowboy settings
                # #################
                  
                snowboy_sensitivity = request.form.get("set_snowboy_sensitivity")   
                snowboy_timeout     = request.form.get("set_snowboy_timeout") 
                snowboy_microphone  = request.form.get("set_snowboy_microphone")                                            
             
                SET_SNOWBOY_SETTINGS(snowboy_sensitivity, snowboy_timeout, snowboy_microphone)  


                #############################
                # speech recognition provider
                #############################
     
                snowboy_hotword                         = request.form.get("set_snowboy_hotword")        
                speech_recognition_provider             = request.form.get("set_speech_recognition_provider")
                speech_recognition_provider_username    = request.form.get("set_speech_recognition_provider_username")
                speech_recognition_provider_key         = request.form.get("set_speech_recognition_provider_key")
                speech_recognition_provider_sensitivity = request.form.get("set_speech_recognition_provider_sensitivity")

                SET_SPEECH_RECOGNITION_PROVIDER_SETTINGS(snowboy_hotword, 
                                                         speech_recognition_provider, 
                                                         speech_recognition_provider_username, 
                                                         speech_recognition_provider_key,
                                                         speech_recognition_provider_sensitivity)    


            #############
            # file upload
            #############
                    
            if request.form.get("file_upload") is not None:
                
                collapse_fileupload = "in"
                
                if 'file' not in request.files:
                    error_message_fileupload = "Keine Datei angegeben"
                else:
                    file = request.files['file']
                    error_message_fileupload = UPLOAD_HOTWORD_FILE(file)


    # snowboy settings
    speechcontrol_global_setting = GET_GLOBAL_SETTING_VALUE("speechcontrol")
    
    snowboy_sensitivity = GET_SNOWBOY_SETTINGS().snowboy_sensitivity
    snowboy_timeout     = GET_SNOWBOY_SETTINGS().snowboy_timeout
    snowboy_microphone  = GET_SNOWBOY_SETTINGS().snowboy_microphone

    dropdown_list_microphone_options = ["ReSpeaker 2-Mics Pi HAT", "ReSpeaker Mic 4 Array v2.0", "Other"]   

    hotword_file_list = GET_ALL_HOTWORD_FILES()

    # speech_recognition_provider only
    snowboy_hotword                          = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().snowboy_hotword
    speech_recognition_provider              = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider
    speech_recognition_provider_username     = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_username
    speech_recognition_provider_key          = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_key
    speech_recognition_provider_sensitivity  = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().speech_recognition_provider_sensitivity
    
    error_message_speechcontrol_led_tasks     = CHECK_SPEECHCONTROL_LED_TASKS(GET_ALL_SPEECHCONTROL_LED_TASKS())
    error_message_speechcontrol_device_tasks  = CHECK_SPEECHCONTROL_TASKS(GET_ALL_SPEECHCONTROL_DEVICE_TASKS(), "devices")
    error_message_speechcontrol_program_tasks = CHECK_SPEECHCONTROL_TASKS(GET_ALL_SPEECHCONTROL_PROGRAM_TASKS(), "programs")
    error_message_speechcontrol_spotify_tasks = CHECK_SPEECHCONTROL_SPOTIFY_TASKS(GET_ALL_SPEECHCONTROL_SPOTIFY_TASKS())

    speechcontrol_led_task_list     = GET_ALL_SPEECHCONTROL_LED_TASKS()
    speechcontrol_device_task_list  = GET_ALL_SPEECHCONTROL_DEVICE_TASKS()
    speechcontrol_program_task_list = GET_ALL_SPEECHCONTROL_PROGRAM_TASKS()
    speechcontrol_spotify_task_list = GET_ALL_SPEECHCONTROL_SPOTIFY_TASKS()

    dropdown_list_speech_recognition_provider = ["Google Cloud Speech", "Google Speech Recognition",
                                                 "Houndify", "IBM Speech", "Microsoft Azure Speech", 
                                                 "Microsoft Bing Voice Recognition", "Wit.ai"]
                                                 
    dropdown_list_mqtt_devices = GET_ALL_MQTT_DEVICES("device")
    dropdown_list_programs     = GET_ALL_PROGRAMS()   
    
    error_message_speech_recognition_provider_settings = CHECK_SPEECH_RECOGNITION_PROVIDER_SETTINGS(GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS())

    return render_template('system_speechcontrol.html',
                            error_message_snowboy=error_message_snowboy,   
                            error_message_change_snowboy_settings=error_message_change_snowboy_settings,                                   
                            error_message_fileupload=error_message_fileupload,
                            error_message_hotword=error_message_hotword,                       
                            error_message_speech_recognition_provider_settings=error_message_speech_recognition_provider_settings,
                            error_message_speechcontrol_led_tasks=error_message_speechcontrol_led_tasks,                              
                            error_message_add_speechcontrol_device_task=error_message_add_speechcontrol_device_task,
                            error_message_speechcontrol_device_tasks=error_message_speechcontrol_device_tasks,                    
                            error_message_add_speechcontrol_program_task=error_message_add_speechcontrol_program_task,
                            error_message_speechcontrol_program_tasks=error_message_speechcontrol_program_tasks,       
                            error_message_speechcontrol_spotify_tasks=error_message_speechcontrol_spotify_tasks,   
                           
                            speechcontrol_global_setting=speechcontrol_global_setting,
                            check_value_speechcontrol=check_value_speechcontrol,
                            snowboy_sensitivity=snowboy_sensitivity,
                            snowboy_timeout=snowboy_timeout,
                            snowboy_microphone=snowboy_microphone,
                            dropdown_list_microphone_options=dropdown_list_microphone_options,

                            hotword_file_list=hotword_file_list,
                            snowboy_hotword=snowboy_hotword,
                            dropdown_list_speech_recognition_provider=dropdown_list_speech_recognition_provider,
                            dropdown_list_mqtt_devices=dropdown_list_mqtt_devices,
                            dropdown_list_programs=dropdown_list_programs,     
                            device_task=device_task,
                            program_task=program_task,
                            
                            collapse_tasks_led=collapse_tasks_led,
                            collapse_tasks_devices=collapse_tasks_devices,
                            collapse_tasks_programs=collapse_tasks_programs,
                            collapse_tasks_spotify=collapse_tasks_spotify,                            
                            collapse_speechcontrol_settings=collapse_speechcontrol_settings,
                            collapse_fileupload=collapse_fileupload,
                                                                           
                            speechcontrol_led_task_list=speechcontrol_led_task_list,
                            speechcontrol_device_task_list=speechcontrol_device_task_list,
                            speechcontrol_program_task_list=speechcontrol_program_task_list,
                            speechcontrol_spotify_task_list=speechcontrol_spotify_task_list,                            
                            speech_recognition_provider=speech_recognition_provider,
                            speech_recognition_provider_username=speech_recognition_provider_username,
                            speech_recognition_provider_key=speech_recognition_provider_key,
                            speech_recognition_provider_sensitivity=speech_recognition_provider_sensitivity,
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system, 
                            )


# change device task position 
@app.route('/system/speechcontrol/device_task/position/<string:direction>/<int:id>')
@login_required
@permission_required
def change_speechcontrol_device_task_position(id, direction):
    CHANGE_SPEECHCONTROL_DEVICE_TASK_POSITION(id, direction)
    return redirect(url_for('system_speechcontrol'))
    

# delete device task  
@app.route('/system/speechcontrol/device_task/delete/<int:id>')
@login_required
@permission_required
def delete_speechcontrol_device_task(id):
    DELETE_SPEECHCONTROL_DEVICE_TASK(id)
    return redirect(url_for('system_speechcontrol'))


# change program task position 
@app.route('/system/speechcontrol/program_task/position/<string:direction>/<int:id>')
@login_required
@permission_required
def change_speechcontrol_program_task_position(id, direction):
    CHANGE_SPEECHCONTROL_PROGRAM_TASK_POSITION(id, direction)
    return redirect(url_for('system_speechcontrol'))
    

# delete program task  
@app.route('/system/speechcontrol/program_task/delete/<int:id>')
@login_required
@permission_required
def delete_speechcontrol_program_task(id):
    DELETE_SPEECHCONTROL_PROGRAM_TASK(id)
    return redirect(url_for('system_speechcontrol'))


# download hotword file
@app.route('/system/speechcontrol/download/hotword/<path:filepath>')
@login_required
@permission_required
def download_hotword_file(filepath):
    if filepath is None:
        print("Ungültiger Pfad angegeben")     
    try:
        path = GET_PATH() + "/app/speechcontrol/snowboy/resources/"     
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /app/speechcontrol/snowboy/resources/" + filepath + " | downloaded")
        return send_from_directory(path, filepath)
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /app/speechcontrol/snowboy/resources/" + filepath + " | " + str(e)) 


# delete snowboy hotwords
@app.route('/system/speechcontrol/delete/hotword/<string:filename>')
@login_required
@permission_required
def delete_snowboy_hotword(filename):
    DELETE_HOTWORD_FILE(filename)
    return redirect(url_for('system_speechcontrol'))


""" ############# """
""" user settings """
""" ############# """

# dashboard user management
@app.route('/system/user', methods=['GET', 'POST'])
@login_required
@permission_required
def system_user():
    error_message_add_user = []
    error_change_settings = ""
    message_admin_password_not_changed = ""
    
    username        = ""
    email           = ""
    password        = ""
    hashed_password = ""
    
    RESET_USER_TASK_ERRORS()        
    RESET_USER_COLLAPSE()


    if request.method == "POST":
        
        # add user
        if request.form.get("add_user") != None: 
            
            if request.form.get("set_username") != None:
                # missing name
                if request.form.get("set_username") == "":
                    error_message_add_user.append("Keinen Benutzernamen angegeben")                                    
                else:         
                    username = request.form.get("set_username")
                    
            if request.form.get("set_email") != None:
                # missing email address
                if request.form.get("set_email") == "":
                    error_message_add_user.append("Keine eMail-Adresse angegeben")                                    
                else:         
                    email = request.form.get("set_email")  
        
            if request.form.get("set_password") != None:
                # missing password
                if request.form.get("set_password") == "":
                    error_message_add_user.append("Kein Passwort angegeben")                                    
                else:         
                    password = request.form.get("set_password")

                    if 8 <= len(password) <= 20:                
                        hashed_password = generate_password_hash(password, method='sha256')
                    else:
                        error_message_add_user.append("Passwort muss zwischen 8 und 20 Zeichen haben")


            if username != "" and email != "" and hashed_password != "":
                ADD_USER(username, email, hashed_password)
                
                username = ""
                email    = ""
                password = ""
                    
  
        # change user settings
        if request.form.get("change_user_settings") != None:
            
            for i in range (1,26): 
                
                if request.form.get("set_username_" + str(i)) != None:
                    
                    SET_USER_COLLAPSE(i)  
                         
                    check_permission_system = False
            
                    # current user has permission_system ?
                    if request.form.get("checkbox_permission_system_" + str(i)) == "on":
                        check_permission_system = True
                        
                    else:
                        
                        # another user has permission_system ?
                        for j in range (1,26): 
                            
                            try:
                                if (i != j) and GET_USER_BY_ID(j).permission_system == "checked":      
                                    check_permission_system = True
                                    continue      
                                    
                            except:
                                pass


                    # one user has permission system
                    if check_permission_system == True: 


                        # check name
                        if (request.form.get("set_username_" + str(i)) != "" and 
                            GET_USER_BY_NAME(request.form.get("set_username_" + str(i))) == None):
                            username = request.form.get("set_username_" + str(i)) 
                            
                        elif request.form.get("set_username_" + str(i)) == GET_USER_BY_ID(i).username:
                            username = GET_USER_BY_ID(i).username
                            
                        else:
                            username = GET_USER_BY_ID(i).username 
                            error_change_settings = error_change_settings + "|" + "Ungültige Eingabe >>> Keinen Name angegeben"                         
                        
                        
                        # check email
                        if (request.form.get("set_email_" + str(i)) != "" and 
                            GET_EMAIL(request.form.get("set_email_" + str(i))) == None):
                            email = request.form.get("set_email_" + str(i)) 
                        
                        elif request.form.get("set_email_" + str(i)) == GET_USER_BY_ID(i).email:
                            email = GET_USER_BY_ID(i).email
                        
                        else:
                            email = GET_USER_BY_ID(i).email 
                            error_change_settings = error_change_settings + "|" + "Ungültige Eingabe >>> Keine eMail-Adresse angegeben"


                        # change user permissions
                        if request.form.get("checkbox_permission_dashboard_" + str(i)):
                            permission_dashboard = "checked"
                        else:
                            permission_dashboard = ""
                        if request.form.get("checkbox_permission_scheduler_" + str(i)):
                            permission_scheduler = "checked"
                        else:
                            permission_scheduler = ""
                        if request.form.get("checkbox_permission_programs_" + str(i)):
                            permission_programs = "checked"
                        else:
                            permission_programs = ""
                        if request.form.get("checkbox_permission_watering_" + str(i)):
                            permission_watering = "checked"
                        else:
                            permission_watering = ""
                        if request.form.get("checkbox_permission_camera_" + str(i)):
                            permission_camera = "checked"
                        else:
                            permission_camera = ""
                        if request.form.get("checkbox_permission_led_" + str(i)):
                            permission_led = "checked"
                        else:
                            permission_led = ""
                        if request.form.get("checkbox_permission_sensordata_" + str(i)):
                            permission_sensordata = "checked"
                        else:
                            permission_sensordata = ""
                        if request.form.get("checkbox_permission_spotify_" + str(i)):
                            permission_spotify = "checked"
                        else:
                            permission_spotify = ""
                        if request.form.get("checkbox_permission_system_" + str(i)):
                            permission_system = "checked"
                        else:
                            permission_system = ""


                        # change email notification
                        if request.form.get("checkbox_email_notification_warning_" + str(i)):
                            email_notification_warning = "checked"
                        else:
                            email_notification_warning = ""
                        if request.form.get("checkbox_email_notification_error_" + str(i)):
                            email_notification_error = "checked"
                        else:
                            email_notification_error = ""
                      
                            
                        SET_USER_SETTINGS(i, username, email, 
                                          permission_dashboard,   
                                          permission_scheduler,        
                                          permission_programs,   
                                          permission_watering,     
                                          permission_camera,      
                                          permission_led,      
                                          permission_sensordata,   
                                          permission_spotify,     
                                          permission_system,     
                                          email_notification_warning,   
                                          email_notification_error)    
        
        
                        # reset password
                        if request.form.get("set_password_" + str(i)) != "":                        
                            password = request.form.get("set_password_" + str(i))
                            
                            try:
                                
                                if 8 <= len(password) <= 20:
                                    
                                    if str(password) == str(request.form.get("set_password_check_" + str(i))):
                                        
                                        hashed_password = generate_password_hash(password, method='sha256')
                            
                                        RESET_USER_PASSWORD(i, hashed_password)
                                         
                                    else:
                                        error_change_settings = error_change_settings + "|" + "Eingegebene Passwörter sind nicht identisch"
                                    
                                else:    
                                    error_change_settings = error_change_settings + "|" + "Passwort muss zwischen 8 und 20 Zeichen haben"
                                    
                            except:
                                error_change_settings = error_change_settings + "|" + "Passwort muss zwischen 8 und 20 Zeichen haben"
                                
             
                    # no user has permission system
                    else:    
                        error_change_settings = error_change_settings + "|" + "Mindestens ein Benutzer muss Zugriffsrechte für 'System' haben"  
                            
                    SET_USER_CHANGE_ERRORS(i, error_change_settings[1:])
                            
                       
    user_list = GET_ALL_USERS()

    try:                                        
        if GET_USER_BY_NAME("admin").password == "sha256$OeDkVenT$bc8d974603b713097e69fc3efa1132991bfb425c59ec00f207e4b009b91f4339":
            message_admin_password_not_changed = "Passwort von Benutzer >admin< muss geändert werden"
    except:
        pass


    return render_template('system_user.html',
                            error_message_add_user=error_message_add_user,
                            message_admin_password_not_changed=message_admin_password_not_changed,
                            username=username,
                            email=email,
                            password=password,
                            user_list=user_list,
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system, 
                            )


# change users position 
@app.route('/system/user/position/<string:direction>/<int:id>')
@login_required
@permission_required
def change_user_position(id, direction):
    CHANGE_USER_POSITION(id, direction)
    return redirect(url_for('system_user'))


# delete user
@app.route('/system/user/delete/<int:id>')
@login_required
@permission_required
def delete_user(id):
    DELETE_USER(id)
    return redirect(url_for('system_user'))


""" ############## """
""" email settings """
""" ############## """

# dashboard email settings
@app.route('/system/email', methods=['GET', 'POST'])
@login_required
@permission_required
def system_email():
    error_message = ""
    error_message_test = ""
    
    message_test                 = ""
    collapse_test_email_settings = ""
    

    if request.method == "POST":     
        # update email settings
        if request.form.get("change_email_settings") != None:      
            set_server_address = request.form.get("set_server_address")
            set_server_port    = request.form.get("set_server_port")
            set_encoding       = request.form.get("set_encoding")
            set_username       = request.form.get("set_username")               
            set_password       = request.form.get("set_password")

            error_message = SET_EMAIL_SETTINGS(set_server_address, set_server_port, set_encoding, set_username, set_password)

        # test email settings
        if request.form.get("test_email_config") != None:  
            collapse_test_email_settings = "in" 
            error_message_test = SEND_EMAIL("TEST", "TEST")

    settings         = GET_EMAIL_SETTINGS()
    encoding_options = ["TLS", "SSL"]
    
    # eMail-Muster
    # SEND_EMAIL(GET_EMAIL_ADDRESS("info"), "TEST", "Das ist eine eMail mit Anhang")

    return render_template('system_email.html',
                            error_message=error_message,
                            error_message_test=error_message_test,
                            settings=settings,
                            encoding_options=encoding_options,   
                            collapse_test_email_settings=collapse_test_email_settings,                       
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system, 
                            )


""" ############### """
""" backup settings """
""" ############### """

@app.route('/system/backup', methods=['GET', 'POST'])
@login_required
@permission_required
def system_backup():
    error_message = ""
    
    new_backup_location_path = False
    collapse_backup_settings = ""
    
    if request.method == "POST":   
              
        # save backup setting
        if request.form.get("save_backup_setting") is not None:
            
            collapse_backup_settings = "in"
            
            # time
            backup_hour = request.form.get("get_backup_hour")

            backup_task = GET_SCHEDULER_TASK_BY_NAME("backup_database")
            
            if backup_task == None:
                ADD_SCHEDULER_TASK("backup_database", "no_scheduler_task")
                backup_task = GET_SCHEDULER_TASK_BY_NAME("backup_database")
                
            i = backup_task.id
                
            SET_SCHEDULER_TASK(i, "backup_database", "save_database", 
                                  "checked", "None", "None", "None", "checked", 
                                  "*", backup_hour, "0",
                                  "None", "None", "None",
                                  "None", "None", "None", 
                                  "None", "None", "None", "None",
                                  "None", "None", "None", 
                                  "None", "None", "None", "None",
                                  "None", "None", "None", 
                                  "None", "None", "None",
                                  "None", "None", "None")  
                                  
            # location
            backup_location_path = request.form.get("get_backup_location_path")
            
            if backup_location_path != GET_CONFIG_BACKUP_LOCATION():
                SET_CONFIG_BACKUP_LOCATION(backup_location_path)
            
                 
        # save database   
        if request.form.get("database_save") is not None:
            SAVE_DATABASE() 
 
    file_list = GET_BACKUP_FILES()

    if GET_SCHEDULER_TASK_BY_NAME("backup_database") != None:
        backup_hour = GET_SCHEDULER_TASK_BY_NAME("backup_database").hour
    else: 
        backup_hour = "Stunde"
   
    backup_location_path = GET_CONFIG_BACKUP_LOCATION() 
        
    if GET_CONFIG_BACKUP_LOCATION()[1] == True:
        new_backup_location_path = True
        backup_location_path     = GET_CONFIG_BACKUP_LOCATION()[0]
        
    dropdown_list_hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

    return render_template('system_backup.html',
                            error_message=error_message,
                            file_list=file_list,
                            backup_hour=backup_hour,
                            backup_location_path=backup_location_path,
                            new_backup_location_path=new_backup_location_path,
                            dropdown_list_hours=dropdown_list_hours,         
                            collapse_backup_settings=collapse_backup_settings,                                           
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system, 
                            )


# restore database backup
@app.route('/system/backup/restore/backup_database/<string:filename>')
@login_required
@permission_required
def restore_database_backup(filename):
    RESTORE_DATABASE(filename)
    return redirect(url_for('system_backup'))


# delete database backup
@app.route('/system/backup/delete/backup_database/<string:filename>')
@login_required
@permission_required
def delete_database_backup(filename):
    DELETE_DATABASE_BACKUP(filename)
    return redirect(url_for('system_backup'))


""" ########### """
""" system logs """
""" ########### """

@app.route('/system/log', methods=['GET', 'POST'])
@login_required
@permission_required
def system_log():
    error_message = ""
    
    selected_type_event    = "selected"
    selected_type_status   = "selected"
    selected_type_database = "selected"    
    selected_type_success  = "selected"   
    selected_type_warning  = "selected"                                                      
    selected_type_error    = "selected"
    log_search             = ""    

    # create log types list
    selected_log_types = ["EVENT", "STATUS", "DATABASE", "SUCCESS", "WARNING", "ERROR"]     
   
    # change log selection 
    if request.form.get("get_log_output") != None:   
   
        selected_type_event    = ""
        selected_type_status   = ""
        selected_type_database = ""        
        selected_type_success  = ""   
        selected_type_warning  = ""                                                     
        selected_type_error    = ""
        
        selected_log_types = [] 
   
        list_selection = request.form.getlist('set_log_types[]')
        
        for element in list_selection:
            
            if element == "EVENT":
                selected_type_event = "selected"
                selected_log_types.append("EVENT")
            if element == "STATUS":
                selected_type_status = "selected"
                selected_log_types.append("STATUS")    
            if element == "DATABASE":
                selected_type_database = "selected"
                selected_log_types.append("DATABASE")                               
            if element == "SUCCESS":
                selected_type_success = "selected"
                selected_log_types.append("SUCCESS")                
            if element == "WARNING":
                selected_type_warning = "selected"
                selected_log_types.append("WARNING")                
            if element == "ERROR":
                selected_type_error = "selected"
                selected_log_types.append("ERROR")     

        log_search = request.form.get('set_log_search')
       

    # get log entries
    if GET_LOGFILE_SYSTEM(selected_log_types, 50, log_search) is not None:
        data_log_system = GET_LOGFILE_SYSTEM(selected_log_types, 50, log_search)
        
    else:
        data_log_system = ""
        error_message_log = "Keine Einträge gefunden"                      

    timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 

    return render_template('system_log.html',
                            error_message=error_message,
                            timestamp=timestamp,
                            selected_type_event=selected_type_event,
                            selected_type_status=selected_type_status,
                            selected_type_database=selected_type_database,                            
                            selected_type_success=selected_type_success,    
                            selected_type_warning=selected_type_warning,                                                      
                            selected_type_error=selected_type_error,                    
                            data_log_system=data_log_system,                                                       
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system, 
                            )


# download system logfile
@app.route('/system/log/download/<path:filepath>')
@login_required
@permission_required
def download_system_logfile(filepath): 
    try:
        path = GET_PATH() + "/logs/"    
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /logs/" + filepath + " | downloaded")
        return send_from_directory(path, filepath)
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/" + filepath + " | " + str(e))
