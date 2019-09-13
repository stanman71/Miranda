import datetime
import time
import heapq

from app import app
from app.database.database import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM
from app.components.mqtt import CHECK_ZIGBEE2MQTT_SETTING_THREAD
from app.components.shared_resources import process_management_queue


""" ####################### """
"""  change heater setting  """
""" ####################### """


def CHANGE_HEATER_SETTING(heater, temperature):

    heating_setting          = '{"current_heating_setpoint":' + str(temperature) + '}'
    heating_setting_formated = 'current_heating_setpoint: ' + str(temperature)
    
    if not heating_setting[1:-1] in heater.mqtt_device.last_values:                          

        channel  = "miranda/" + heater.mqtt_device.gateway + "/" + heater.mqtt_device.ieeeAddr + "/set"                        
        msg      = heating_setting

        heapq.heappush(process_management_queue, (1, ("heating", "change_setting", channel, msg)))   

        CHECK_ZIGBEE2MQTT_SETTING_THREAD(heater.mqtt_device.name, heating_setting, 5, 20) 

    else:
            
        WRITE_LOGFILE_SYSTEM("STATUS", "Zigbee2MQTT | Device - " + heater.mqtt_device.name + " | " + heating_setting_formated) 


""" ###################### """
"""      heater process    """
""" ###################### """


def HEATER_PROCESS(heater_id):
    
    heater = GET_HEATER_BY_ID(heater_id)
    
    now = datetime.datetime.now()
    current_day    = now.strftime('%a')
    current_hour   = now.strftime('%H')
    current_minute = now.strftime('%M')
    
    if current_day == "Mon":
       
        if str(heater.monday_time_1.split(":")[0]) == str(current_hour) and str(heater.monday_time_1.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.monday_temperature_1)
        if str(heater.monday_time_2.split(":")[0]) == str(current_hour) and str(heater.monday_time_2.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.monday_temperature_2)     
        if str(heater.monday_time_3.split(":")[0]) == str(current_hour) and str(heater.monday_time_3.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.monday_temperature_3)     
        if str(heater.monday_time_4.split(":")[0]) == str(current_hour) and str(heater.monday_time_4.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.monday_temperature_4)     

    if current_day == "Tue":
       
        if str(heater.tuesday_time_1.split(":")[0]) == str(current_hour) and str(heater.tuesday_time_1.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.tuesday_temperature_1)
        if str(heater.tuesday_time_2.split(":")[0]) == str(current_hour) and str(heater.tuesday_time_2.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.tuesday_temperature_2)     
        if str(heater.tuesday_time_3.split(":")[0]) == str(current_hour) and str(heater.tuesday_time_3.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.tuesday_temperature_3)     
        if str(heater.tuesday_time_4.split(":")[0]) == str(current_hour) and str(heater.tuesday_time_4.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.tuesday_temperature_4)     

    if current_day == "Wed":
       
        if str(heater.wednesday_time_1.split(":")[0]) == str(current_hour) and str(heater.wednesday_time_1.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.wednesday_temperature_1)
        if str(heater.wednesday_time_2.split(":")[0]) == str(current_hour) and str(heater.wednesday_time_2.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.wednesday_temperature_2)     
        if str(heater.wednesday_time_3.split(":")[0]) == str(current_hour) and str(heater.wednesday_time_3.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.wednesday_temperature_3)     
        if str(heater.wednesday_time_4.split(":")[0]) == str(current_hour) and str(heater.wednesday_time_4.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.wednesday_temperature_4)     

    if current_day == "Thu":
       
        if str(heater.thursday_time_1.split(":")[0]) == str(current_hour) and str(heater.thursday_time_1.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.thursday_temperature_1)
        if str(heater.thursday_time_2.split(":")[0]) == str(current_hour) and str(heater.thursday_time_2.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.thursday_temperature_2)     
        if str(heater.thursday_time_3.split(":")[0]) == str(current_hour) and str(heater.thursday_time_3.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.thursday_temperature_3)     
        if str(heater.thursday_time_4.split(":")[0]) == str(current_hour) and str(heater.thursday_time_4.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.thursday_temperature_4)     

    if current_day == "Fri":     
        
        if str(heater.friday_time_1.split(":")[0]) == str(current_hour) and str(heater.friday_time_1.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.friday_temperature_1)
        if str(heater.friday_time_2.split(":")[0]) == str(current_hour) and str(heater.friday_time_2.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.friday_temperature_2)     
        if str(heater.friday_time_3.split(":")[0]) == str(current_hour) and str(heater.friday_time_3.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.friday_temperature_3)     
        if str(heater.friday_time_4.split(":")[0]) == str(current_hour) and str(heater.friday_time_4.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.friday_temperature_4)
            
    if current_day == "Sat":
       
        if str(heater.saturday_time_1.split(":")[0]) == str(current_hour) and str(heater.saturday_time_1.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.saturday_temperature_1)
        if str(heater.saturday_time_2.split(":")[0]) == str(current_hour) and str(heater.saturday_time_2.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.saturday_temperature_2)     
        if str(heater.saturday_time_3.split(":")[0]) == str(current_hour) and str(heater.saturday_time_3.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.saturday_temperature_3)     
        if str(heater.saturday_time_4.split(":")[0]) == str(current_hour) and str(heater.saturday_time_4.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.saturday_temperature_4)     

    if current_day == "Sun":
       
        if str(heater.sunday_time_1.split(":")[0]) == str(current_hour) and str(heater.sunday_time_1.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.sunday_temperature_1)
        if str(heater.sunday_time_2.split(":")[0]) == str(current_hour) and str(heater.sunday_time_2.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.sunday_temperature_2)     
        if str(heater.sunday_time_3.split(":")[0]) == str(current_hour) and str(heater.sunday_time_3.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.sunday_temperature_3)     
        if str(heater.sunday_time_4.split(":")[0]) == str(current_hour) and str(heater.sunday_time_4.split(":")[1]) == str(current_minute):
            CHANGE_HEATER_SETTING(heater, heater.sunday_temperature_4)     

            
