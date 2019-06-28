import threading
import heapq
import time

from app import app
from app.database.database import *
from app.components.file_management import *
from app.components.shared_resources import process_management_queue

program_running = None
stop_program    = False
repeat_program  = False


def START_PROGRAM_THREAD(program_id):
    global program_running

    Thread = threading.Thread(target=PROGRAM_THREAD, args=(program_id, ))
    Thread.start()    
    
    program_name = GET_PROGRAM_BY_ID(program_id).name
    WRITE_LOGFILE_SYSTEM("EVENT", "Program - " + program_name + " | started") 
    program_running = program_name
    
    
def STOP_PROGRAM_THREAD():
    global stop_program, program_running, repeat_program
    stop_program    = True
    program_running = None
    repeat_program  = False
    
   
def REPEAT_PROGRAM_THREAD():
    global repeat_program
    repeat_program = True

    
def GET_REPEAT_PROGRAM():
    global repeat_program
    return repeat_program       

    
def GET_PROGRAM_RUNNING():
    global program_running
    return program_running   
   

def PROGRAM_THREAD(program_id):
    global stop_program, repeat_program, program_running

    try:
        content      = GET_PROGRAM_BY_ID(program_id).content
        program_name = GET_PROGRAM_BY_ID(program_id).name
        
        lines_total  = len(content.splitlines())
        repeat       = True

        while repeat == True:

            line_number = 1

            for line in content.splitlines():
                
                # stop program
                if stop_program == True:
                    stop_program = False
                    
                    WRITE_LOGFILE_SYSTEM("EVENT", "Program - " + program_name + " | stopped")
                    break
       
       
                else:
                    
                    # update program info
                    if repeat_program == True:
                        program_running = program_name + " ( " + str(line_number) + " | " + str(lines_total) + " | repeat )"
                    else:
                        program_running = program_name + " ( " + str(line_number) + " | " + str(lines_total) + " )"
                    
                    
                    # #######
                    #  break
                    # #######           
                            
                    if "pause" in line:
                            
                        line_content = line.split(":")
                        time.sleep(int(line_content[1]))          
                        
                        
                    # ########
                    #  device
                    # ########
                             
                    if "device" in line:
                            
                        line_content = line.split(":")
                        
                        try:
                        
                            device_name = line_content[1]    
                            device      = ""
                            device      = GET_MQTT_DEVICE_BY_NAME(device_name)
                            
                            setting_value = line_content[2].upper()
                            setting_value = setting_value.replace(" ", "")
                    
                            # new device setting ?
                            if setting_value != device.previous_setting_value:
                               
                                device_commands = device.commands.split(",")
                                setting_key     = None
                                                        
                                # setting key
                                for device_command in device_commands:
                                  
                                    if device_command.split("=")[1] == setting_value:
                                        setting_key = device_command.split("=")[0]
                                        setting_key = setting_key.replace(" ", "")
                                        continue     
                             
                                # setting key founded ?
                                if setting_key != None:
                                        
                                    if device.gateway == "mqtt":   
                                        heapq.heappush(process_management_queue, (30,  ("program", "device", device.gateway, device.ieeeAddr, setting_key, setting_value)))
                                            
                                    if device.gateway == "zigbee2mqtt":
                                        heapq.heappush(process_management_queue, (30,  ("program", "device", device.gateway, device.name, setting_key, setting_value)))
                                        
                                else:
                                    WRITE_LOGFILE_SYSTEM("ERROR", "Program - " + program_name + " | Device - " + device_name + " | Command not valid")
                                
                                       
                            else:
                                    
                                if device.gateway == "mqtt":   
                                    WRITE_LOGFILE_SYSTEM("STATUS", "MQTT | Device - " + device_name + " | " + setting_value)
                                    
                                if device.gateway == "zigbee2mqtt":
                                    WRITE_LOGFILE_SYSTEM("STATUS", "Zigbee2MQTT | Device - " + device_name + " | " + setting_value)


                        except Exception as e:
                            print(e)    
                            WRITE_LOGFILE_SYSTEM("ERROR", "Program - " + program_name + " | Device - " + device_name + " | not founded")               
                        
                        
                    # #####
                    #  led
                    # #####
                             
                    if "led" in line:
                            
                        line_content = line.split(":")
                        
                        try:
                            led_name = line_content[1]    
                            led_type = GET_MQTT_DEVICE_BY_NAME(led_name).device_type
                            
                            
                            # setting led_rgb or led_white                      
                            if (led_type == "led_rgb" or led_type == "led_white") and line_content[2] != "off": 
                                
                                led_color_setting = line_content[2]
                                led_brightness    = line_content[3]                      
                                heapq.heappush(process_management_queue, (30,  ("program", led_type, led_name, led_color_setting, led_brightness)))
                         
                         
                            # setting led_simple                           
                            elif led_type == "led_simple" and line_content[2] != "off":      
                                        
                                led_brightness = line_content[2]                         
                                heapq.heappush(process_management_queue, (30,  ("program", led_type, led_name, led_brightness)))                        
                             
                               
                            # setting led turn_off   
                            else:  
                                    
                                heapq.heappush(process_management_queue, (30,  ("program", "turn_off", led_name)))                              
                          
                            
                        except:
                            WRITE_LOGFILE_SYSTEM("ERROR", "Program - " + program_name + " | LED - " + led_name + " | not founded")
                            

                    line_number = line_number + 1
                    time.sleep(1)
                 
                 
            # repeat program ?
            if repeat_program == True:        
                repeat = True
            else:
                repeat = False
                
        
        program_running = None    
        time.sleep(5)
        WRITE_LOGFILE_SYSTEM("SUCCESS", "Program - " + program_name + " | finished")
                

    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Programm - " + GET_PROGRAM_BY_ID(program_id).name + " | " + str(e))
        return str(e)
    
