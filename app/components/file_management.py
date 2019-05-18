import datetime
import os
import shutil
import csv
import yaml

import pandas as pd

from werkzeug.utils import secure_filename

from app import app
from app.database.database import *


# windows
if os.name == "nt":                 
    PATH = os.path.abspath("") 
# linux
else:                               
    PATH = os.path.abspath("") + "/SmartHome"

UPLOAD_FOLDER = PATH + "/app/speechcontrol/snowboy/resources/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def GET_PATH():
    return (PATH)


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
    if os.path.isfile(PATH + "/logs/log_" + gateway + ".csv") is False:
        CREATE_LOGFILE("log_" + gateway)

    try:
        # open csv file
        file = PATH + "/logs/log_" + gateway + ".csv"
        with open(file, 'a', newline='', encoding='utf-8') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)                                        
            filewriter.writerow( [str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), str(channel), msg ])
            csvfile.close()
      
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/log_" + gateway + ".csv | " + str(e))


def READ_LOGFILE_MQTT(gateway, channel, time):   
    
    try:
        # open csv file
        file = PATH + "/logs/log_" + gateway + ".csv"
        
        with open(file, 'r', newline='', encoding='utf-8') as csvfile:
            rowReader = csv.reader(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            data = [row for row in rowReader] 
            csvfile.close()

            headers = data.pop(0)  

            # reverse messages           
            data_reversed = data[::-1]        

            # get time value of the time setting
            date_check = datetime.datetime.now() - datetime.timedelta(seconds=time)
            date_check = date_check.strftime("%Y-%m-%d %H:%M:%S")
            
            # get all elements of the selected time
            list_temp = []
            list_result = []

            for element in data_reversed:
                
                try:
                    date_entry   = datetime.datetime.strptime(element[0],"%Y-%m-%d %H:%M:%S")   
                    date_control = datetime.datetime.strptime(date_check, "%Y-%m-%d %H:%M:%S")
                    if date_entry > date_control:
                        list_temp.append(element)
                except:
                    pass
                    
            if list_temp == []:
                return "Message nicht gefunden"                    
                
            else:
                # get the searched message
                
                for element in list_temp:
                    if element[1] == channel:
                        list_result.append(element)
                    
                if list_result != []:
                    return list_result
                if list_result == []:
                    return "Message nicht gefunden" 

    
    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/log_" + gateway + ".csv | " + str(e))   
        return ("ZigBee2MQTT >>> ERROR >>> " + str(e))
    

def WRITE_LOGFILE_SYSTEM(log_type, description):
    if os.path.isfile(PATH + "/logs/log_system.csv") is False:
        CREATE_LOGFILE("log_system")

    try:
        # open csv file
        file = PATH + "/logs/log_system.csv"

        with open(file, 'a', newline='', encoding='utf-8') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)                                        
            filewriter.writerow( [str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), str(log_type), str(description) ])
            csvfile.close()
       
    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/log_system.csv | " + str(e))
        return ("ERROR: " + str(e))
        
    
def GET_LOGFILE_SYSTEM(rows):   
    try:
        # open csv file
        file = PATH + "/logs/log_system.csv"
        
        with open(file, 'r', newline='', encoding='utf-8') as csvfile:
            rowReader = csv.reader(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            data = [row for row in rowReader] # get data
            headers = data.pop(0)             # get headers and remove from data
            data_reversed = data[::-1]        # reverse the data
            csvfile.close()

            return data_reversed[0:rows]
            
    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /logs/log_system.csv | " + str(e)) 
        return ("ERROR: " + str(e))         


""" ############### """
""" backup database """
""" ############### """

def GET_BACKUP_FILES():
    file_list = []
    for files in os.walk(PATH + "/backup/"):  
        file_list.append(files)

    if file_list == []:
        return ""
    else:
        return file_list[0][2]    


def SAVE_DATABASE():  
    # delete old backup files
    if len(GET_BACKUP_FILES()) == 10:
        file_list = GET_BACKUP_FILES()
        os.remove (PATH + '/backup/' + file_list[0])

    try:
        shutil.copyfile(PATH + '/app/database/smarthome.sqlite3', 
                        PATH + '/backup/' + str(datetime.datetime.now().date()) + '_smarthome.sqlite3')
        WRITE_LOGFILE_SYSTEM("EVENT", "Database_Backup | saved")
        return ""
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Database_Backup | " + str(e)) 
        return str(e)
        return ("ERROR: " + str(e))


def RESTORE_DATABASE(filename):
    # check file
    try:
        if filename.split("_")[1] == "smarthome.sqlite3":
            shutil.copyfile(PATH + '/backup/' + filename, PATH + '/app/database/smarthome.sqlite3')
            WRITE_LOGFILE_SYSTEM("EVENT", "Database_Backup | " + filename + " | restored")
            
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Database_Backup | " + str(e))  
        return ("ERROR: " + str(e))
        
        
def DELETE_DATABASE_BACKUP(filename):
    try:
        os.remove (PATH + '/backup/' + filename)
        WRITE_LOGFILE_SYSTEM("EVENT", "File | /backup/" + filename + " | deleted")
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File | /backup/" + filename + " | " + str(e))  
        return ("ERROR: " + str(e))


""" ############# """
"""  file config  """
""" ############# """

try:
    # open config file
    with open(PATH + "/app/config/config.yaml", "r") as file_config:
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


""" ################################ """
"""  file zigbee device informations """
""" ################################ """

try:
    # open mqtt file
    with open(PATH + "/app/config/zigbee_device_informations.yaml", 'r') as file_zigbee:
        zigbee_devices = yaml.load(file_zigbee, Loader=yaml.SafeLoader)
        file_zigbee.close()
        
except Exception as e:
    WRITE_LOGFILE_SYSTEM("ERROR", "File | config/zigbee_device_informations.ymal | " + str(e))


def GET_MQTT_DEVICE_INFORMATIONS(model):
    
    if model.isdigit():
        model = int(model)
    
    try:
        device_type = str(zigbee_devices[model]['device_type'])
    except:
        device_type = ""
        
    try:
        description = str(zigbee_devices[model]['description'])
    except:
        description = ""
        
    try:        
        inputs      = str(zigbee_devices[model]['inputs'])
        inputs      = inputs.replace("[","")
        inputs      = inputs.replace("]","")
        inputs      = inputs.replace("'","")        
    except:
        inputs      = ""
        
    try:        
        outputs     = str(zigbee_devices[model]['outputs'])
        outputs     = outputs.replace("[","")
        outputs     = outputs.replace("]","")
        outputs     = outputs.replace("'","")    
    except:
        outputs     = ""
        
    try:        
        commands    = str(zigbee_devices[model]['commands'])
        commands    = commands.replace("[","")
        commands    = commands.replace("]","")
        commands    = commands.replace("'","")         
    except:
        commands    = ""
      
        
    return (device_type, description, inputs, outputs, commands)


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
        
        df = pd.read_csv(file, sep=",", skiprows = 1, names=["Timestamp","Device","Sensor","Sensor_Value"])
        return df

    except Exception as e:
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


def GET_HOTWORD_FILES_FROM_TASKS(snowboy_tasks):
    file_list = []
    exist_file_list = GET_ALL_HOTWORD_FILES()
    
    for element in snowboy_tasks:
        if (element.name + ".pmdl") in exist_file_list:
            file_list.append(PATH + "/app/speechcontrol/snowboy/resources/" + element.name + ".pmdl")
        
    return file_list


def CHECK_HOTWORD_FILE_EXIST(snowboy_tasks):
    list_files = []
    exist_file_list = GET_ALL_HOTWORD_FILES()
    
    for element in snowboy_tasks:

        try:
            if (element.name + ".pmdl") not in exist_file_list:
                list_files.append(element.name + ".pmdl")
        except:
            list_files.append("Keine Datei angegeben")
            
    if list_files != []:
        return list_files
    else:
        return ""
        

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
