import datetime
import os
import shutil
import csv
import yaml
import json

import pandas as pd

from flask import send_from_directory
from werkzeug.utils import secure_filename

from app import app


""" #### """
""" path """
""" #### """

# windows
if os.name == "nt":                 
    PATH = os.path.abspath("") 
# linux
else:                               
    PATH = os.path.abspath("") + "/miranda"


UPLOAD_FOLDER = PATH + "/app/speechcontrol/snowboy/resources/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def GET_PATH():
    return (PATH)

backup_location_temp_path = ""


""" #### """
""" logs """
""" #### """

def CREATE_LOGFILE(filename):
    try:
        # create csv file
        file = PATH + "/logs/" + filename + ".csv"
        with open(file, 'w', encoding='utf-8') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)    

            if filename == "log_mqtt":                   
                filewriter.writerow(['Timestamp','Channel','Message'])
            if filename == "log_zigbee2mqtt":                   
                filewriter.writerow(['Timestamp','Channel','Message'])                
            if filename == "log_system":                   
                filewriter.writerow(['Timestamp','Type','Description'])                
            
            csvfile.close()

        WRITE_LOGFILE_SYSTEM("EVENT", "File | /logs/" + filename + ".csv | created")      

    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/" + filename + ".csv | " + str(e))  

        
def RESET_LOGFILE(filename):
    if os.path.isfile(PATH + "/logs/" + filename + ".csv"):
        os.remove (PATH + "/logs/" + filename + ".csv")

        WRITE_LOGFILE_SYSTEM("EVENT", "File | /logs/" + filename + ".csv | deleted")
        
    CREATE_LOGFILE(filename)
        

def WRITE_LOGFILE_MQTT(gateway, channel, msg):
    
    # create file if not exist
    if os.path.isfile(PATH + "/logs/log_" + gateway + ".csv") is False:
        CREATE_LOGFILE("log_" + gateway)
        
    # replace file if size > 2,5 mb
    file_size = os.path.getsize(PATH + "/logs/log_" + gateway + ".csv")
    file_size = round(file_size / 1024 / 1024, 2)
    
    if file_size > 2.5:
        RESET_LOGFILE("log_" + gateway)

    try:
        
        # open csv file
        file = PATH + "/logs/log_" + gateway + ".csv"
        with open(file, 'a', newline='', encoding='utf-8') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)                                        
            filewriter.writerow( [str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), str(channel), msg ])
            csvfile.close()

    except Exception as e:
        print(str(e))


def WRITE_LOGFILE_SYSTEM(log_type, description):

    # create file if not exist
    if os.path.isfile(PATH + "/logs/log_system.csv") is False:
        CREATE_LOGFILE("log_system")

    # replace file if size > 2.5 mb
    file_size = os.path.getsize(PATH + "/logs/log_system.csv")
    file_size = round(file_size / 1024 / 1024, 2)
    
    if file_size > 2.5:
        RESET_LOGFILE("log_system")

    try:
        # open csv file
        file = PATH + "/logs/log_system.csv"

        with open(file, 'a', newline='', encoding='utf-8') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)   
            filewriter.writerow( [str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), log_type, description])
            csvfile.close()
       
    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/log_system.csv | " + str(e))
        return ("ERROR: " + str(e))
        
    
def GET_LOGFILE_SYSTEM(selected_log_types, rows):   
    
    try:
        # open csv file
        file = PATH + "/logs/log_system.csv"
        
        with open(file, 'r', newline='', encoding='utf-8') as csvfile:
            rowReader = csv.reader(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            data = [row for row in rowReader] 
            csvfile.close()
            
            headers = data.pop(0)                 # get headers and remove from data
            data_reversed = data[::-1]            # reverse the data

            # get the selected log entries
            data_reversed_filtered = []

            for element in data_reversed:
                if element[1] in selected_log_types:
                    data_reversed_filtered.append(element)
                
            return data_reversed_filtered[0:rows]
            
            
    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/log_system.csv | " + str(e)) 
        return ("ERROR: " + str(e))         


""" ############# """
"""  file config  """
""" ############# """

try:
    # open config file
    with open(PATH + "/config/config.yaml", "r") as file_config:
        config = yaml.load(file_config, Loader=yaml.SafeLoader)
        file_config.close()

    # print check
    print("Version: " + str(config['config']['version']))
    
except Exception as e:
    print("##### ERROR: config file not founded #####")
    WRITE_LOGFILE_SYSTEM("ERROR", "File | config/config.ymal | " + str(e) + " | !!! DEFAULT SETTINGS LOADED !!! ")


def GET_CONFIG_VERSION():
    try:
        return str(config['config']['version'])
    except:
        return "DEFAULT SETTINGS"
        

def GET_CONFIG_MQTT_BROKER():
    try:
        return str(config['config']['mqtt_broker'])
    except:
        
        return "localhost"
        
        
def GET_CONFIG_DATABASE():
    try:
        return str(config['config']['database'])
    except:
        return "sqlite:///database/smarthome.sqlite3"
        
        
def GET_CONFIG_BACKUP_LOCATION():
    global backup_location_temp_path
    
    if backup_location_temp_path == "": 
    
        try:
            return str(config['config']['backup_location'])
        except:
            return ("/home/pi/SmartHome/backup/", False)        
    
    else:
        return (backup_location_temp_path, True)
        
        
def GET_SPOTIFY_CLIENT_ID():
    try:
        return str(config['spotify']['client_id'])
    except:
        return ""        


def GET_SPOTIFY_CLIENT_SECRET():
    try:
        return str(config['spotify']['client_secret'])
    except:
        return ""     


def GET_SPOTIFY_REFRESH_TOKEN():
    try:
        return str(config['spotify']['refresh_token'])
    except:
        return ""     


def SET_SPOTIFY_REFRESH_TOKEN(REFRESH_TOKEN):
    
    try:
        with open(PATH + "/config/config.yaml") as file_config:
            upload_config = yaml.load(file_config)

        upload_config['spotify']['refresh_token'] = REFRESH_TOKEN

        with open(PATH + "/config/config.yaml", 'w') as file_config:
            yaml.dump(upload_config, file_config)
            
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /config/config/ | " + str(e))  
        return ("ERROR: " + str(e))
        

def SET_CONFIG_BACKUP_LOCATION(backup_location_path):
    global backup_location_temp_path
    
    try:
        with open(PATH + "/config/config.yaml") as file_config:
            upload_config = yaml.load(file_config)

        upload_config['config']['backup_location'] = backup_location_path

        with open(PATH + "/config/config.yaml", 'w') as file_config:
            yaml.dump(upload_config, file_config)
            
        backup_location_temp_path = backup_location_path
            
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /config/config/ | " + str(e))  
        return ("ERROR: " + str(e))
    

""" ############## """
""" network config """
""" ############## """

def SAVE_NETWORK_SETTINGS(eth0_ip_address, eth0_gateway, wlan0_ip_address, wlan0_gateway):
    
    try:
        file = "/etc/dhcpcd.conf"
        with open(file, 'w', encoding='utf-8') as conf_file:
            conf_file.write("# A sample configuration for dhcpcd.\n")
            conf_file.write("# See dhcpcd.conf(5) for details.\n")
            conf_file.write("\n")
            conf_file.write("# Inform the DHCP server of our hostname for DDNS.\n")
            conf_file.write("hostname\n")
            conf_file.write("\n")
            conf_file.write("# Use the hardware address of the interface for the Client ID.\n")
            conf_file.write("clientid\n")
            conf_file.write("\n")
            conf_file.write("# Persist interface configuration when dhcpcd exits.\n")
            conf_file.write("persistent\n")
            conf_file.write("\n")
            conf_file.write("# on the server to actually work.\n")
            conf_file.write("option rapid_commit\n")
            conf_file.write("\n")
            conf_file.write("# A list of options to request from the DHCP server.\n")
            conf_file.write("option domain_name_servers, domain_name, domain_search, host_name\n")
            conf_file.write("option classless_static_routes\n")
            conf_file.write("\n")
            conf_file.write("# Respect the network MTU. This is applied to DHCP routes.\n")
            conf_file.write("option interface_mtu\n")
            conf_file.write("\n")
            conf_file.write("# A ServerID is required by RFC2131.\n")
            conf_file.write("require dhcp_server_identifier\n")
            conf_file.write("\n")
            conf_file.write("# Generate SLAAC address using the Hardware Address of the interface\n")
            conf_file.write("#slaac hwaddr\n")
            conf_file.write("# OR generate Stable Private IPv6 Addresses based from the DUID\n")
            conf_file.write("slaac private\n")
            conf_file.write("\n")
            conf_file.write("interface wlan0\n")
            conf_file.write("inform " + str(wlan0_ip_address) + "/24\n")
            conf_file.write("static routers=" + str(wlan0_gateway) + "\n")
            conf_file.write("\n")
            conf_file.write("interface eth0\n")
            conf_file.write("static routers=" + str(eth0_gateway) + "\n")
            conf_file.write("inform " + str(eth0_ip_address) + "/24\n")
              
            conf_file.close()

    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /etc/dhcpcd.conf | " + str(e))  
        return ("ERROR: " + str(e))


""" ############### """
""" backup database """
""" ############### """

# get backup path
backup_location_path = GET_CONFIG_BACKUP_LOCATION()


def GET_BACKUP_FILES():
    file_list = []
    for files in os.walk(backup_location_path):  
        file_list.append(files)

    if file_list == []:
        return ""
    else:
        file_list = file_list[0][2]
        file_list = sorted(file_list, reverse=True)
        return file_list 


def SAVE_DATABASE():  

    try:
        # save database
        shutil.copyfile(PATH + '/app/database/smarthome.sqlite3', 
                        backup_location_path + str(datetime.datetime.now().date()) + '_smarthome.sqlite3')
                
        # if more then 10 backups saved, delete oldest backup file
        list_of_files = os.listdir(PATH + '/backup/')    
        full_path     = [backup_location_path + '{0}'.format(x) for x in list_of_files]

        if len([name for name in list_of_files]) > 10:
            oldest_file = min(full_path, key=os.path.getctime)
            os.remove(oldest_file)        
        
        WRITE_LOGFILE_SYSTEM("SUCCESS", "Database_Backup | saved")
        return ""
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Database_Backup | " + str(e)) 
        return str(e)


def RESTORE_DATABASE(filename):
    # check file
    try:
        if filename.split("_")[1] == "smarthome.sqlite3":
            shutil.copyfile(backup_location_path + filename, PATH + '/app/database/smarthome.sqlite3')
            WRITE_LOGFILE_SYSTEM("SUCCESS", "Database_Backup | " + filename + " | restored")
            
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Database_Backup | " + str(e))  
        return ("ERROR: " + str(e))
        
        
def DELETE_DATABASE_BACKUP(filename):
    try:
        os.remove (backup_location_path + filename)
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /backup/" + filename + " | deleted")
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /backup/" + filename + " | " + str(e))  
        return ("ERROR: " + str(e))


""" ########### """
""" colorpicker """
""" ########### """

# Host files for colorpicker_local
@app.route('/get_media/<path:filename>', methods=['GET'])
def get_media(filename):
    if filename is None:
        WRITE_LOGFILE_SYSTEM("ERROR", "LED | Colorpicker | File not founded")
    try:
        PATH_CSS = PATH + '/app/static/colorpicker'
        return send_from_directory(PATH_CSS, filename)
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "LED | Colorpicker | " + str(e))
        

""" ################ """
"""  file locations  """
""" ################ """

try:
    # open locations file
    with open(PATH + "/config/locations.ymal", "r") as file_locations:
        locations = yaml.load(file_locations, Loader=yaml.SafeLoader)
        file_locations.close()

except Exception as e:
    print(str(e))
    WRITE_LOGFILE_SYSTEM("ERROR", "File | config/locations.ymal | " + str(e))


def GET_ALL_LOCATIONS():
    try:
        return (locations["Locations"].keys())
        
    except Exception as e:    
        return ("ERROR: Locations Import >>> " + str(e))
        WRITE_LOGFILE_SYSTEM("ERROR", "File | config/locations.ymal | " + str(e))
        

def GET_LOCATION_COORDINATES(location):
    try:
        return (locations["Locations"][location])
        
    except Exception as e:    
        return ("ERROR: Locations Import >>> " + str(e))
        WRITE_LOGFILE_SYSTEM("ERROR", "File | config/locations.ymal | " + str(e))


""" ################################ """
"""  file zigbee device informations """
""" ################################ """

def GET_MQTT_DEVICE_INFORMATIONS(model):
    
    try:
        with open(PATH + "/config/zigbee_device_informations.json", 'r') as data_file:
            data_loaded = json.load(data_file)

        for device in data_loaded["data"]:

            if str(device["model"]) == str(model):

                try:
                    device_type  = device['device_type']
                except:
                    device_type  = ""                 
                  
                try:
                    description  = device['description']
                except:
                    description  = ""

                try:
                    input_values = device['input_values']
                    input_values = ','.join(input_values)   
                    input_values = input_values.replace("'", '"')
                except:
                    input_values = ""
                  
                try:
                    input_events = device['input_events']
                    input_events = ','.join(input_events)
                    input_events = input_events.replace("'", '"')
                    input_events = input_events.replace("},{", '} {')     
                except:
                    input_events = ""
                    
                try:
                    commands     = device['commands']   
                    commands     = ','.join(commands)
                    commands     = commands.replace("'", '"')  
                    commands     = commands.replace("},{", '} {')                               
                except:
                    commands     = ""
                
                return (device_type, description, input_values, input_events, commands)
                
        return ("", "", "", "", "")   
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | config/zigbee_device_informations.json | " + str(e))   


""" ########## """
""" sensordata """
""" ########## """

def GET_SENSORDATA_FILES():
    file_list = []
    for files in os.walk(PATH + "/csv/"):  
        file_list.append(files)   

    if file_list == []:
        return ""
    else:
        return file_list[0][2]    


def CREATE_SENSORDATA_FILE(filename):
    if os.path.isfile(PATH + "/csv/" + filename + ".csv") is False:

        try:
            # create csv file
            file = PATH + "/csv/" + filename + ".csv"
            with open(file, 'w', encoding='utf-8') as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)                       
                filewriter.writerow(['Timestamp','Device','Sensor','Sensor_Value'])
                csvfile.close()

            WRITE_LOGFILE_SYSTEM("EVENT", "File | /csv/" + filename + ".csv | created") 
            return "" 
                
        except Exception as e:
            WRITE_LOGFILE_SYSTEM("ERROR", "File | /csv/" + filename + ".csv | " + str(e))

    else:
        return ""


def WRITE_SENSORDATA_FILE(filename, device, sensor, value):
    if os.path.isfile(PATH + "/csv/" + filename + ".csv") is False:
        CREATE_SENSORDATA_FILE(filename)

    try:
        # open csv file
        file = PATH + "/csv/" + filename + ".csv"
        with open(file, 'a', newline='', encoding='utf-8') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)                                        
            filewriter.writerow( [str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), str(device), str(sensor), str(value) ])
            csvfile.close()
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /csv/" + filename + ".csv | " + str(e))


def READ_SENSORDATA_FILE(filename):
    try:
        # open csv file with pandas
        file = PATH + "/csv/" + filename
        
        df = pd.read_csv(file, sep = ",", skiprows = 1, names = ["Timestamp","Device","Sensor","Sensor_Value"])
        return df

    except Exception as e:
        if "Error tokenizing data. C error: Calling read(nbytes) on source failed. Try engine='python'." not in str(e):
            print(e)
            WRITE_LOGFILE_SYSTEM("ERROR", "File | /csv/" + filename + " | " + str(e))    


def DELETE_SENSORDATA_FILE(filename):
    try:
        os.remove (PATH + '/csv/' + filename)
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /csv/" + filename + " | deleted")
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /csv/" + filename + " | " + str(e))  


""" ####### """
""" snowboy """
""" ####### """

def GET_ALL_HOTWORD_FILES():
    file_list_temp = []
    file_list = []

    for files in os.walk(PATH + "/app/speechcontrol/snowboy/resources/"):  
        file_list_temp.append(files)

    if file_list_temp == []:
        return ""  
    else:
        file_list_temp = file_list_temp[0][2]
        for file in file_list_temp:        
            if file != "common.res":
                file_list.append(file)
                
        return file_list


def UPLOAD_HOTWORD_FILE(file):
    ALLOWED_EXTENSIONS = set(['pmdl'])

    def allowed_file(filename):
        return '.' in filename and \
                filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS    

    if file.filename == '':
        error_message_fileupload = "Keine Datei angegeben"
    elif file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        error_message_fileupload = ""
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /app/speechcontrol/snowboy/resources/" + str(file.name) + ".pmdl | uploaded")  
    else:
        error_message_fileupload = "Ungültige Dateiendung"

    return error_message_fileupload
    

def DELETE_HOTWORD_FILE(filename):
    try:
        os.remove (PATH + '/app/speechcontrol/snowboy/resources/' + filename)
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /app/speechcontrol/snowboy/resources/" + filename + " | deleted") 
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /app/speechcontrol/snowboy/resources/" + filename + " | " + str(e))  


""" ############## """
""" speech control """
""" ############## """

def GET_SPEECH_RECOGNITION_PROVIDER_HOTWORD(settings):
    hotword_file = settings
    return (PATH + "/app/speechcontrol/snowboy/resources/" + hotword_file)

