import datetime
import os
import shutil
import csv

from werkzeug.utils import secure_filename

from app import app
from app.database.database import *

PATH = "/home/pi/SmartHome"

UPLOAD_FOLDER = PATH + "/app/snowboy/resources/"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def GET_PATH():
    return (PATH)


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

    shutil.copyfile(PATH + '/app/database/smarthome.sqlite3', 
                    PATH + '/backup/' + str(datetime.datetime.now().date()) + '_smarthome.sqlite3')


def RESTORE_DATABASE(filename):
    # check file
    try:
        if filename.split("_")[1] == "smarthome.sqlite3":
            shutil.copyfile(PATH + '/backup/' + filename, PATH + '/app/database/smarthome.sqlite3')
    except:
        pass 
        
        
def DELETE_DATABASE_BACKUP(filename):
    os.remove (PATH + '/backup/' + filename)


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
    try:
        # create csv file
        file = PATH + "/csv/" + filename + ".csv"
        with open(file, 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)                       
            filewriter.writerow(['Sensorwert', 'Datum'])
            csvfile.close()
        return ""
            
    except:
        return "Datei konnte nicht angelegt werden"


def WRITE_SENSORDATA_FILE(filename, data):
    try:
        # open csv file
        file = PATH + "/csv/" + filename + ".csv"
        with open(file, 'a', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)                                        
            filewriter.writerow([str(data), str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))])
            csvfile.close()
        return ""          
    except:
        return "Auf die Datei konnte nicht zugegriffen werden"


def DELETE_SENSORDATA_FILE(filename):
    os.remove (PATH + '/csv/' + filename)


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


def GET_USED_HOTWORD_FILES():
    file_list = []
    for element in GET_ALL_SNOWBOY_TASKS():
        file_list.append(PATH + "/app/snowboy/resources/" + element.name + ".pmdl")
        
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
    else:
        error_message_fileupload = "Ungültige Dateiendung"

    return error_message_fileupload
    

def DELETE_HOTWORD_FILE(filename):
    os.remove (PATH + '/app/snowboy/resources/' + filename)
