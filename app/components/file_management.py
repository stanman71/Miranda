import datetime
import os
import shutil
import csv
import yaml

import pandas as pd

from werkzeug.utils import secure_filename

from app import app
from app.database.database import *


""" ########### """
""" global path """
""" ########### """

# windows
if os.name == "nt":                 
    PATH = os.path.abspath("") 
# linux
else:                               
    PATH = os.path.abspath("") + "/SmartHome"

UPLOAD_FOLDER = PATH + "/app/snowboy/resources/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def GET_PATH():
    return (PATH)


""" ########### """
""" config file """
""" ########### """

with open(PATH + "/app/config.yaml", 'r') as cfg:
    yamlcfg=yaml.load(cfg)

# print check
print("Version: " + str((yamlcfg['config']['version'])))

def GET_CONFIG_VERSION():
    return (str((yamlcfg['config']['version'])))

def GET_CONFIG_MQTT_BROKER():
    return str((yamlcfg['config']['mqtt_broker']))

def GET_CONFIG_DATABASE():
    return str((yamlcfg['config']['database']))


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
        os.remove (PATH + '/backup/' + file_list[0])

    try:
        shutil.copyfile(PATH + '/app/database/smarthome.sqlite3', 
                        PATH + '/backup/' + str(datetime.datetime.now().date()) + '_smarthome.sqlite3')
        WRITE_LOGFILE_SYSTEM("EVENT", "Database_Backup >>> saved")
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Database_Backup >>> " + str(e)) 


def RESTORE_DATABASE(filename):
    # check file
    try:
        if filename.split("_")[1] == "smarthome.sqlite3":
            shutil.copyfile(PATH + '/backup/' + filename, PATH + '/app/database/smarthome.sqlite3')
            WRITE_LOGFILE_SYSTEM("EVENT", "Database_Backup >>> " + filename + " >>> restored")
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "Database_Backup >>> " + str(e))  
        
        
def DELETE_DATABASE_BACKUP(filename):
    try:
        os.remove (PATH + '/backup/' + filename)
        WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /backup/" + filename + " >>> deleted")
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /backup/" + filename + " >>> " + str(e))  


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

            WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /csv/" + filename + ".csv >>> created") 
            return "" 
                
        except Exception as e:
            WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /csv/" + filename + ".csv >>> " + str(e))

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
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /csv/" + filename + ".csv >>> " + str(e))


def READ_SENSORDATA_FILE(filename):
    try:
        # open csv file with pandas
        file = PATH + "/csv/" + filename
        
        df = pd.read_csv(file, sep=",", skiprows = 1, names=["Timestamp","Device","Sensor","Sensor_Value"])
        return df

    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /csv/" + filename + " >>> " + str(e))    


def DELETE_SENSORDATA_FILE(filename):
    try:
        os.remove (PATH + '/csv/' + filename)
        WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /csv/" + filename + " >>> deleted")
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /csv/" + filename + " >>> " + str(e))  


""" ####### """
""" snowboy """
""" ####### """

def GET_ALL_HOTWORD_FILES():
    file_list_temp = []
    file_list = []

    for files in os.walk(PATH + "/app/snowboy/resources/"):  
        file_list_temp.append(files)

    if file_list_temp == []:
        return ""  
    else:
        file_list_temp = file_list_temp[0][2]
        for file in file_list_temp:        
            if file != "common.res":
                file_list.append(file)
                
        return file_list


def GET_USED_HOTWORD_FILES(snowboy_tasks):
    file_list = []
    exist_file_list = GET_ALL_HOTWORD_FILES()
    
    for element in snowboy_tasks:
        if (element.name + ".pmdl") in exist_file_list:
            file_list.append(PATH + "/app/snowboy/resources/" + element.name + ".pmdl")
        
    return file_list


def CHECK_HOTWORD_FILE_EXIST(snowboy_tasks):
    list_files = []
    exist_file_list = GET_ALL_HOTWORD_FILES()
    
    for element in snowboy_tasks:
        if (element.name + ".pmdl") not in exist_file_list:
            list_files.append(element.name + ".pmdl")
            
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
        WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /app/snowboy/resources/" + str(file.name) + ".pmdl >>> uploaded")  
    else:
        error_message_fileupload = "Ungültige Dateiendung"

    return error_message_fileupload
    

def DELETE_HOTWORD_FILE(filename):
    try:
        os.remove (PATH + '/app/snowboy/resources/' + filename)
        WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /app/snowboy/resources/" + filename + " >>> deleted") 
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /app/snowboy/resources/" + filename + " >>> " + str(e))  


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
            if filename == "log_zigbee":                   
                filewriter.writerow(['Timestamp','Channel','Message'])                
            if filename == "log_system":                   
                filewriter.writerow(['Timestamp','Type','Description'])                
            
            csvfile.close()

        WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /logs/" + filename + ".csv >>> created")      

    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /logs/" + filename + ".csv >>> " + str(e))  

        
def RESET_LOGFILE(filename):
    if os.path.isfile(PATH + "/logs/" + filename + ".csv"):
        os.remove (PATH + "/logs/" + filename + ".csv")

        WRITE_LOGFILE_SYSTEM("EVENT", "File >>> /logs/" + filename + ".csv >>> deleted")
        
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
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /logs/log_" + gateway + ".csv >>> " + str(e))


def READ_LOGFILE_MQTT(gateway, channel):   
    
    try:
        # open csv file
        file = PATH + "/logs/log_" + gateway + ".csv"
        
        with open(file, 'r', newline='', encoding='utf-8') as csvfile:
            rowReader = csv.reader(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            
            # reverse messages
            data = [row for row in rowReader] 
            headers = data.pop(0)             
            data_reversed = data[::-1]        

            # get time value 5 seconds ago
            date_check = datetime.datetime.now() - datetime.timedelta(seconds=5)
            date_check = date_check.strftime("%Y-%m-%d %H:%M:%S")
            
            # get all elements of the last 5 seconds
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
                return "Keine Verbindung zu MQTT"                    
                
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
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /logs/log_" + gateway + ".csv >>> " + str(e))         


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
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /logs/log_system.csv >>> " + str(e))
        
    
def GET_LOGFILE_SYSTEM(rows):   
    try:
        # open csv file
        file = PATH + "/logs/log_system.csv"
        
        with open(file, 'r', newline='', encoding='utf-8') as csvfile:
            rowReader = csv.reader(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            data = [row for row in rowReader] # get data
            headers = data.pop(0)             # get headers and remove from data
            data_reversed = data[::-1]        # reverse the data

            return data_reversed[0:rows]
            
    except Exception as e:
        print(e)
        WRITE_LOGFILE_SYSTEM("ERROR", "File >>> /logs/log_system.csv >>> " + str(e))          
