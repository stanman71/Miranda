from app import app
from app.database.database import *
from app.components.file_management import GET_ALL_HOTWORD_FILES

import datetime


""" ################### """
"""     check camera    """
""" ################### """

def CHECK_CAMERA_SETTINGS(cameras):
   error_message_settings = []

   for camera in cameras:

      if camera.name == "None" or camera.name == "":
         error_message_settings.append(str(camera.id) + " >>> Keinen Name eingetragen")         
      if camera.url == "None" or camera.url == "":
         error_message_settings.append(camera.name + " >>> Keine URL eingetragen")  

   return error_message_settings


""" ################### """
"""   check dashboard   """
""" ################### """

def CHECK_DEVICE_EXCEPTION_SETTINGS(devices): 
   error_message_settings = []

   for device in devices:

      if device.exception_option != "None":

         if device.exception_setting == "None" or device.exception_setting == None:
            error_message_settings.append(device.name + " >>> Keine Aufgabe ausgewählt")         

         # exception setting ip_address
         if device.exception_option == "IP-Address":

            # search for wrong chars
            for element in device.exception_value_1:
               if not element.isdigit() and element != "." and element != "," and element != " ":
                  error_message_settings.append(device.name + " >>> Ungültige IP-Adresse")
                  break
               
         # exception setting sensor
         if device.exception_option != "IP-Address": 
            
            if device.exception_value_1 == "None" or device.exception_value_1 == None:
               error_message_settings.append(device.name + " >>> Keinen Sensor ausgewählt")

            if device.exception_value_2 == "None" or device.exception_value_2 == None:
               error_message_settings.append(device.name + " >>> Keinen Operator (<, >, =) eingetragen")

            if device.exception_value_3 == "None" or device.exception_value_3 == None:
               error_message_settings.append(device.name + " >>> Keinen Vergleichswert eingetragen")
                  
   return error_message_settings


""" ################## """
"""   check heating    """
""" ################## """

def CHECK_HEATING_SETTINGS(heaters):
   list_errors = []
   
   for heater in heaters:
       
      # check mqtt_device multiple times ?
      list_heaters = GET_ALL_HEATERS()

      for control_heater in list_heaters:
           
         if control_heater.id != heater.id:
            if control_heater.mqtt_device_ieeeAddr == heater.mqtt_device_ieeeAddr:
               list_errors.append(heater.name + " >>> Gerät mehrmals zugeordnet >>> " + heater.mqtt_device.name)
      
      
      # ######################  
      # search for wrong chars
      # ######################
      
      # ######
      # monday
      # ######
      
      if heater.monday_time_1 != "None" and heater.monday_time_1 != None and heater.monday_time_1 != "":
          
         try:
            datetime.datetime.strptime(heater.monday_time_1, "%H:%M")
         except:
            list_errors.append(heater.name + " >>> Montag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 1 >>> " + heater.monday_time_1)
            
         if heater.monday_temperature_1 == "None" or heater.monday_temperature_1 == None or heater.monday_temperature_1 == "":       
            list_errors.append(heater.name + " >>> Montag >>> Keine Temperatur angegeben >>> Eintrag 1")
            
      if heater.monday_temperature_1 != "None" and heater.monday_temperature_1 != None and heater.monday_temperature_1 != "":
          
         try:
            error_founded = False
            
            for element in heater.monday_temperature_1:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Montag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 1 >>> " + heater.monday_temperature_1)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.monday_temperature_1) <= 25:
                  list_errors.append(heater.name + " >>> Montag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 1 >>> " + heater.monday_temperature_1)
         
         except:
            list_errors.append(heater.name + " >>> Montag >>> Ungültige Temperatur >>> Eintrag 1 >>> " + heater.monday_temperature_1)

         if heater.monday_time_1 == "None" or heater.monday_time_1 == None or heater.monday_time_1 == "":       
            list_errors.append(heater.name + " >>> Montag >>> Keine Uhrzeit angegeben >>> Eintrag 1")         
      
      
      if heater.monday_time_2 != "None" and heater.monday_time_2 != None and heater.monday_time_2 != "":
          
         try:
            if datetime.datetime.strptime(heater.monday_time_1, "%H:%M") > datetime.datetime.strptime(heater.monday_time_2, "%H:%M"):
               list_errors.append(heater.name + " >>> Montag >>> Ungültige Uhrzeit >>> Eintrag 2 >>> muss nach Uhrzeit Eintrag 1 sein >>> " + heater.monday_time_2)
         except:
            list_errors.append(heater.name + " >>> Montag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 2 >>> " + heater.monday_time_2)
            
         if heater.monday_temperature_2 == "None" or heater.monday_temperature_2 == None or heater.monday_temperature_2 == "":       
            list_errors.append(heater.name + " >>> Montag >>> Keine Temperatur angegeben >>> Eintrag 2")
          
      if heater.monday_temperature_2 != "None" and heater.monday_temperature_2 != None and heater.monday_temperature_2 != "":
          
         try:
            error_founded = False
            
            for element in heater.monday_temperature_2:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Montag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 2 >>> " + heater.monday_temperature_2)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.monday_temperature_2) <= 25:
                  list_errors.append(heater.name + " >>> Montag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 2 >>> " + heater.monday_temperature_2)
         
         except:
            list_errors.append(heater.name + " >>> Montag >>> Ungültige Temperatur >>> Eintrag 2 >>> " + heater.monday_temperature_2)

         if heater.monday_time_2 == "None" or heater.monday_time_2 == None or heater.monday_time_2 == "":       
            list_errors.append(heater.name + " >>> Montag >>> Keine Uhrzeit angegeben >>> Eintrag 2")     
 
 
      if heater.monday_time_3 != "None" and heater.monday_time_3 != None and heater.monday_time_3 != "":
          
         try:
            if datetime.datetime.strptime(heater.monday_time_2, "%H:%M") > datetime.datetime.strptime(heater.monday_time_3, "%H:%M"):
               list_errors.append(heater.name + " >>> Montag >>> Ungültige Uhrzeit >>> Eintrag 3 >>> muss nach Uhrzeit Eintrag 2 sein >>> " + heater.monday_time_3)
         except:
            list_errors.append(heater.name + " >>> Montag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 3 >>> " + heater.monday_time_3)
            
         if heater.monday_temperature_3 == "None" or heater.monday_temperature_3 == None or heater.monday_temperature_3 == "":       
            list_errors.append(heater.name + " >>> Montag >>> Keine Temperatur angegeben >>> Eintrag 3")
            
      if heater.monday_temperature_3 != "None" and heater.monday_temperature_3 != None and heater.monday_temperature_3 != "":
          
         try:
            error_founded = False
            
            for element in heater.monday_temperature_3:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Montag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 3 >>> " + heater.monday_temperature_3)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.monday_temperature_3) <= 25:
                  list_errors.append(heater.name + " >>> Montag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 3 >>> " + heater.monday_temperature_3)
         
         except:
            list_errors.append(heater.name + " >>> Montag >>> Ungültige Temperatur >>> Eintrag 3 >>> " + heater.monday_temperature_3)

         if heater.monday_time_3 == "None" or heater.monday_time_3 == None or heater.monday_time_3 == "":       
            list_errors.append(heater.name + " >>> Montag >>> Keine Uhrzeit angegeben >>> Eintrag 3")       


      if heater.monday_time_4 != "None" and heater.monday_time_4 != None and heater.monday_time_4 != "":
          
         try:
            if datetime.datetime.strptime(heater.monday_time_3, "%H:%M") > datetime.datetime.strptime(heater.monday_time_4, "%H:%M"):
               list_errors.append(heater.name + " >>> Montag >>> Ungültige Uhrzeit >>> Eintrag 4 >>> muss nach Uhrzeit Eintrag 3 sein >>> " + heater.monday_time_4)
         except:
            list_errors.append(heater.name + " >>> Montag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 4 >>> " + heater.monday_time_4)
            
         if heater.monday_temperature_4 == "None" or heater.monday_temperature_4 == None or heater.monday_temperature_4 == "":       
            list_errors.append(heater.name + " >>> Montag >>> Keine Temperatur angegeben >>> Eintrag 4")
               
      if heater.monday_temperature_4 != "None" and heater.monday_temperature_4 != None and heater.monday_temperature_4 != "":
          
         try:
            error_founded = False
            
            for element in heater.monday_temperature_4:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Montag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 4 >>> " + heater.monday_temperature_4)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.monday_temperature_4) <= 25:
                  list_errors.append(heater.name + " >>> Montag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 4 >>> " + heater.monday_temperature_4)
         
         except:
            list_errors.append(heater.name + " >>> Montag >>> Ungültige Temperatur >>> Eintrag 4 >>> " + heater.monday_temperature_4)

         if heater.monday_time_4 == "None" or heater.monday_time_4 == None or heater.monday_time_4 == "":       
            list_errors.append(heater.name + " >>> Montag >>> Keine Uhrzeit angegeben >>> Eintrag 4")     
 
      # #######
      # tuesday
      # #######
      
      if heater.tuesday_time_1 != "None" and heater.tuesday_time_1 != None and heater.tuesday_time_1 != "":
          
         try:
            datetime.datetime.strptime(heater.tuesday_time_1, "%H:%M")
         except:
            list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 1 >>> " + heater.tuesday_time_1)
            
         if heater.tuesday_temperature_1 == "None" or heater.tuesday_temperature_1 == None or heater.tuesday_temperature_1 == "":       
            list_errors.append(heater.name + " >>> Dienstag >>> Keine Temperatur angegeben >>> Eintrag 1")
            
      if heater.tuesday_temperature_1 != "None" and heater.tuesday_temperature_1 != None and heater.tuesday_temperature_1 != "":
          
         try:
            error_founded = False
            
            for element in heater.tuesday_temperature_1:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 1 >>> " + heater.tuesday_temperature_1)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.tuesday_temperature_1) <= 25:
                  list_errors.append(heater.name + " >>> Dienstag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 1 >>> " + heater.tuesday_temperature_1)
         
         except:
            list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Temperatur >>> Eintrag 1 >>> " + heater.tuesday_temperature_1)

         if heater.tuesday_time_1 == "None" or heater.tuesday_time_1 == None or heater.tuesday_time_1 == "":       
            list_errors.append(heater.name + " >>> Dienstag >>> Keine Uhrzeit angegeben >>> Eintrag 1")         
      
      
      if heater.tuesday_time_2 != "None" and heater.tuesday_time_2 != None and heater.tuesday_time_2 != "":
          
         try:
            if datetime.datetime.strptime(heater.tuesday_time_1, "%H:%M") > datetime.datetime.strptime(heater.tuesday_time_2, "%H:%M"):
               list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Uhrzeit >>> Eintrag 2 >>> muss nach Uhrzeit Eintrag 1 sein >>> " + heater.tuesday_time_2)
         except:
            list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 2 >>> " + heater.tuesday_time_2)
            
         if heater.tuesday_temperature_2 == "None" or heater.tuesday_temperature_2 == None or heater.tuesday_temperature_2 == "":       
            list_errors.append(heater.name + " >>> Dienstag >>> Keine Temperatur angegeben >>> Eintrag 2")
          
      if heater.tuesday_temperature_2 != "None" and heater.tuesday_temperature_2 != None and heater.tuesday_temperature_2 != "":
          
         try:
            error_founded = False
            
            for element in heater.tuesday_temperature_2:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 2 >>> " + heater.tuesday_temperature_2)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.tuesday_temperature_2) <= 25:
                  list_errors.append(heater.name + " >>> Dienstag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 2 >>> " + heater.tuesday_temperature_2)
         
         except:
            list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Temperatur >>> Eintrag 2 >>> " + heater.tuesday_temperature_2)

         if heater.tuesday_time_2 == "None" or heater.tuesday_time_2 == None or heater.tuesday_time_2 == "":       
            list_errors.append(heater.name + " >>> Dienstag >>> Keine Uhrzeit angegeben >>> Eintrag 2")     
 
 
      if heater.tuesday_time_3 != "None" and heater.tuesday_time_3 != None and heater.tuesday_time_3 != "":
          
         try:
            if datetime.datetime.strptime(heater.tuesday_time_2, "%H:%M") > datetime.datetime.strptime(heater.tuesday_time_3, "%H:%M"):
               list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Uhrzeit >>> Eintrag 3 >>> muss nach Uhrzeit Eintrag 2 sein >>> " + heater.tuesday_time_3)
         except:
            list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 3 >>> " + heater.tuesday_time_3)
            
         if heater.tuesday_temperature_3 == "None" or heater.tuesday_temperature_3 == None or heater.tuesday_temperature_3 == "":       
            list_errors.append(heater.name + " >>> Dienstag >>> Keine Temperatur angegeben >>> Eintrag 3")
            
      if heater.tuesday_temperature_3 != "None" and heater.tuesday_temperature_3 != None and heater.tuesday_temperature_3 != "":
          
         try:
            error_founded = False
            
            for element in heater.tuesday_temperature_3:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 3 >>> " + heater.tuesday_temperature_3)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.tuesday_temperature_3) <= 25:
                  list_errors.append(heater.name + " >>> Dienstag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 3 >>> " + heater.tuesday_temperature_3)
         
         except:
            list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Temperatur >>> Eintrag 3 >>> " + heater.tuesday_temperature_3)

         if heater.tuesday_time_3 == "None" or heater.tuesday_time_3 == None or heater.tuesday_time_3 == "":       
            list_errors.append(heater.name + " >>> Dienstag >>> Keine Uhrzeit angegeben >>> Eintrag 3")       


      if heater.tuesday_time_4 != "None" and heater.tuesday_time_4 != None and heater.tuesday_time_4 != "":
          
         try:
            if datetime.datetime.strptime(heater.tuesday_time_3, "%H:%M") > datetime.datetime.strptime(heater.tuesday_time_4, "%H:%M"):
               list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Uhrzeit >>> Eintrag 4 >>> muss nach Uhrzeit Eintrag 3 sein >>> " + heater.tuesday_time_4)
         except:
            list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 4 >>> " + heater.tuesday_time_4)
            
         if heater.tuesday_temperature_4 == "None" or heater.tuesday_temperature_4 == None or heater.tuesday_temperature_4 == "":       
            list_errors.append(heater.name + " >>> Dienstag >>> Keine Temperatur angegeben >>> Eintrag 4")
               
      if heater.tuesday_temperature_4 != "None" and heater.tuesday_temperature_4 != None and heater.tuesday_temperature_4 != "":
          
         try:
            error_founded = False
            
            for element in heater.tuesday_temperature_4:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 4 >>> " + heater.tuesday_temperature_4)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.tuesday_temperature_4) <= 25:
                  list_errors.append(heater.name + " >>> Dienstag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 4 >>> " + heater.tuesday_temperature_4)
         
         except:
            list_errors.append(heater.name + " >>> Dienstag >>> Ungültige Temperatur >>> Eintrag 4 >>> " + heater.tuesday_temperature_4)

         if heater.tuesday_time_4 == "None" or heater.tuesday_time_4 == None or heater.tuesday_time_4 == "":       
            list_errors.append(heater.name + " >>> Dienstag >>> Keine Uhrzeit angegeben >>> Eintrag 4")      
 
      # #########
      # wednesday
      # #########
      
      if heater.wednesday_time_1 != "None" and heater.wednesday_time_1 != None and heater.wednesday_time_1 != "":
          
         try:
            datetime.datetime.strptime(heater.wednesday_time_1, "%H:%M")
         except:
            list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 1 >>> " + heater.wednesday_time_1)
            
         if heater.wednesday_temperature_1 == "None" or heater.wednesday_temperature_1 == None or heater.wednesday_temperature_1 == "":       
            list_errors.append(heater.name + " >>> Mittwoch >>> Keine Temperatur angegeben >>> Eintrag 1")
            
      if heater.wednesday_temperature_1 != "None" and heater.wednesday_temperature_1 != None and heater.wednesday_temperature_1 != "":
          
         try:
            error_founded = False
            
            for element in heater.wednesday_temperature_1:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 1 >>> " + heater.wednesday_temperature_1)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.wednesday_temperature_1) <= 25:
                  list_errors.append(heater.name + " >>> Mittwoch >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 1 >>> " + heater.wednesday_temperature_1)
         
         except:
            list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Temperatur >>> Eintrag 1 >>> " + heater.wednesday_temperature_1)

         if heater.wednesday_time_1 == "None" or heater.wednesday_time_1 == None or heater.wednesday_time_1 == "":       
            list_errors.append(heater.name + " >>> Mittwoch >>> Keine Uhrzeit angegeben >>> Eintrag 1")         
      
      
      if heater.wednesday_time_2 != "None" and heater.wednesday_time_2 != None and heater.wednesday_time_2 != "":
          
         try:
            if datetime.datetime.strptime(heater.wednesday_time_1, "%H:%M") > datetime.datetime.strptime(heater.wednesday_time_2, "%H:%M"):
               list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Uhrzeit >>> Eintrag 2 >>> muss nach Uhrzeit Eintrag 1 sein >>> " + heater.wednesday_time_2)
         except:
            list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 2 >>> " + heater.wednesday_time_2)
            
         if heater.wednesday_temperature_2 == "None" or heater.wednesday_temperature_2 == None or heater.wednesday_temperature_2 == "":       
            list_errors.append(heater.name + " >>> Mittwoch >>> Keine Temperatur angegeben >>> Eintrag 2")
          
      if heater.wednesday_temperature_2 != "None" and heater.wednesday_temperature_2 != None and heater.wednesday_temperature_2 != "":
          
         try:
            error_founded = False
            
            for element in heater.wednesday_temperature_2:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 2 >>> " + heater.wednesday_temperature_2)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.wednesday_temperature_2) <= 25:
                  list_errors.append(heater.name + " >>> Mittwoch >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 2 >>> " + heater.wednesday_temperature_2)
         
         except:
            list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Temperatur >>> Eintrag 2 >>> " + heater.wednesday_temperature_2)

         if heater.wednesday_time_2 == "None" or heater.wednesday_time_2 == None or heater.wednesday_time_2 == "":       
            list_errors.append(heater.name + " >>> Mittwoch >>> Keine Uhrzeit angegeben >>> Eintrag 2")     
 
 
      if heater.wednesday_time_3 != "None" and heater.wednesday_time_3 != None and heater.wednesday_time_3 != "":
          
         try:
            if datetime.datetime.strptime(heater.wednesday_time_2, "%H:%M") > datetime.datetime.strptime(heater.wednesday_time_3, "%H:%M"):
               list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Uhrzeit >>> Eintrag 3 >>> muss nach Uhrzeit Eintrag 2 sein >>> " + heater.wednesday_time_3)
         except:
            list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 3 >>> " + heater.wednesday_time_3)
            
         if heater.wednesday_temperature_3 == "None" or heater.wednesday_temperature_3 == None or heater.wednesday_temperature_3 == "":       
            list_errors.append(heater.name + " >>> Mittwoch >>> Keine Temperatur angegeben >>> Eintrag 3")
            
      if heater.wednesday_temperature_3 != "None" and heater.wednesday_temperature_3 != None and heater.wednesday_temperature_3 != "":
          
         try:
            error_founded = False
            
            for element in heater.wednesday_temperature_3:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 3 >>> " + heater.wednesday_temperature_3)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.wednesday_temperature_3) <= 25:
                  list_errors.append(heater.name + " >>> Mittwoch >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 3 >>> " + heater.wednesday_temperature_3)
         
         except:
            list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Temperatur >>> Eintrag 3 >>> " + heater.wednesday_temperature_3)

         if heater.wednesday_time_3 == "None" or heater.wednesday_time_3 == None or heater.wednesday_time_3 == "":       
            list_errors.append(heater.name + " >>> Mittwoch >>> Keine Uhrzeit angegeben >>> Eintrag 3")       


      if heater.wednesday_time_4 != "None" and heater.wednesday_time_4 != None and heater.wednesday_time_4 != "":
          
         try:
            if datetime.datetime.strptime(heater.wednesday_time_3, "%H:%M") > datetime.datetime.strptime(heater.wednesday_time_4, "%H:%M"):
               list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Uhrzeit >>> Eintrag 4 >>> muss nach Uhrzeit Eintrag 3 sein >>> " + heater.wednesday_time_4)
         except:
            list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 4 >>> " + heater.wednesday_time_4)
            
         if heater.wednesday_temperature_4 == "None" or heater.wednesday_temperature_4 == None or heater.wednesday_temperature_4 == "":       
            list_errors.append(heater.name + " >>> Mittwoch >>> Keine Temperatur angegeben >>> Eintrag 4")
               
      if heater.wednesday_temperature_4 != "None" and heater.wednesday_temperature_4 != None and heater.wednesday_temperature_4 != "":
          
         try:
            error_founded = False
            
            for element in heater.wednesday_temperature_4:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 4 >>> " + heater.wednesday_temperature_4)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.wednesday_temperature_4) <= 25:
                  list_errors.append(heater.name + " >>> Mittwoch >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 4 >>> " + heater.wednesday_temperature_4)
         
         except:
            list_errors.append(heater.name + " >>> Mittwoch >>> Ungültige Temperatur >>> Eintrag 4 >>> " + heater.wednesday_temperature_4)

         if heater.wednesday_time_4 == "None" or heater.wednesday_time_4 == None or heater.wednesday_time_4 == "":       
            list_errors.append(heater.name + " >>> Mittwoch >>> Keine Uhrzeit angegeben >>> Eintrag 4")      
 
      # ########
      # thursday
      # ########
      
      if heater.thursday_time_1 != "None" and heater.thursday_time_1 != None and heater.thursday_time_1 != "":
          
         try:
            datetime.datetime.strptime(heater.thursday_time_1, "%H:%M")
         except:
            list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 1 >>> " + heater.thursday_time_1)
            
         if heater.thursday_temperature_1 == "None" or heater.thursday_temperature_1 == None or heater.thursday_temperature_1 == "":       
            list_errors.append(heater.name + " >>> Donnerstag >>> Keine Temperatur angegeben >>> Eintrag 1")
            
      if heater.thursday_temperature_1 != "None" and heater.thursday_temperature_1 != None and heater.thursday_temperature_1 != "":
          
         try:
            error_founded = False
            
            for element in heater.thursday_temperature_1:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 1 >>> " + heater.thursday_temperature_1)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.thursday_temperature_1) <= 25:
                  list_errors.append(heater.name + " >>> Donnerstag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 1 >>> " + heater.thursday_temperature_1)
         
         except:
            list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Temperatur >>> Eintrag 1 >>> " + heater.thursday_temperature_1)

         if heater.thursday_time_1 == "None" or heater.thursday_time_1 == None or heater.thursday_time_1 == "":       
            list_errors.append(heater.name + " >>> Donnerstag >>> Keine Uhrzeit angegeben >>> Eintrag 1")         
      
      
      if heater.thursday_time_2 != "None" and heater.thursday_time_2 != None and heater.thursday_time_2 != "":
          
         try:
            if datetime.datetime.strptime(heater.thursday_time_1, "%H:%M") > datetime.datetime.strptime(heater.thursday_time_2, "%H:%M"):
               list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Uhrzeit >>> Eintrag 2 >>> muss nach Uhrzeit Eintrag 1 sein >>> " + heater.thursday_time_2)
         except:
            list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 2 >>> " + heater.thursday_time_2)
            
         if heater.thursday_temperature_2 == "None" or heater.thursday_temperature_2 == None or heater.thursday_temperature_2 == "":       
            list_errors.append(heater.name + " >>> Donnerstag >>> Keine Temperatur angegeben >>> Eintrag 2")
          
      if heater.thursday_temperature_2 != "None" and heater.thursday_temperature_2 != None and heater.thursday_temperature_2 != "":
          
         try:
            error_founded = False
            
            for element in heater.thursday_temperature_2:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 2 >>> " + heater.thursday_temperature_2)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.thursday_temperature_2) <= 25:
                  list_errors.append(heater.name + " >>> Donnerstag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 2 >>> " + heater.thursday_temperature_2)
         
         except:
            list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Temperatur >>> Eintrag 2 >>> " + heater.thursday_temperature_2)

         if heater.thursday_time_2 == "None" or heater.thursday_time_2 == None or heater.thursday_time_2 == "":       
            list_errors.append(heater.name + " >>> Donnerstag >>> Keine Uhrzeit angegeben >>> Eintrag 2")     
 
 
      if heater.thursday_time_3 != "None" and heater.thursday_time_3 != None and heater.thursday_time_3 != "":
          
         try:
            if datetime.datetime.strptime(heater.thursday_time_2, "%H:%M") > datetime.datetime.strptime(heater.thursday_time_3, "%H:%M"):
               list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Uhrzeit >>> Eintrag 3 >>> muss nach Uhrzeit Eintrag 2 sein >>> " + heater.thursday_time_3)
         except:
            list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 3 >>> " + heater.thursday_time_3)
            
         if heater.thursday_temperature_3 == "None" or heater.thursday_temperature_3 == None or heater.thursday_temperature_3 == "":       
            list_errors.append(heater.name + " >>> Donnerstag >>> Keine Temperatur angegeben >>> Eintrag 3")
            
      if heater.thursday_temperature_3 != "None" and heater.thursday_temperature_3 != None and heater.thursday_temperature_3 != "":
          
         try:
            error_founded = False
            
            for element in heater.thursday_temperature_3:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 3 >>> " + heater.thursday_temperature_3)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.thursday_temperature_3) <= 25:
                  list_errors.append(heater.name + " >>> Donnerstag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 3 >>> " + heater.thursday_temperature_3)
         
         except:
            list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Temperatur >>> Eintrag 3 >>> " + heater.thursday_temperature_3)

         if heater.thursday_time_3 == "None" or heater.thursday_time_3 == None or heater.thursday_time_3 == "":       
            list_errors.append(heater.name + " >>> Donnerstag >>> Keine Uhrzeit angegeben >>> Eintrag 3")       


      if heater.thursday_time_4 != "None" and heater.thursday_time_4 != None and heater.thursday_time_4 != "":
          
         try:
            if datetime.datetime.strptime(heater.thursday_time_3, "%H:%M") > datetime.datetime.strptime(heater.thursday_time_4, "%H:%M"):
               list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Uhrzeit >>> Eintrag 4 >>> muss nach Uhrzeit Eintrag 3 sein >>> " + heater.thursday_time_4)
         except:
            list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 4 >>> " + heater.thursday_time_4)
            
         if heater.thursday_temperature_4 == "None" or heater.thursday_temperature_4 == None or heater.thursday_temperature_4 == "":       
            list_errors.append(heater.name + " >>> Donnerstag >>> Keine Temperatur angegeben >>> Eintrag 4")
               
      if heater.thursday_temperature_4 != "None" and heater.thursday_temperature_4 != None and heater.thursday_temperature_4 != "":
          
         try:
            error_founded = False
            
            for element in heater.thursday_temperature_4:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 4 >>> " + heater.thursday_temperature_4)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.thursday_temperature_4) <= 25:
                  list_errors.append(heater.name + " >>> Donnerstag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 4 >>> " + heater.thursday_temperature_4)
         
         except:
            list_errors.append(heater.name + " >>> Donnerstag >>> Ungültige Temperatur >>> Eintrag 4 >>> " + heater.thursday_temperature_4)

         if heater.thursday_time_4 == "None" or heater.thursday_time_4 == None or heater.thursday_time_4 == "":       
            list_errors.append(heater.name + " >>> Donnerstag >>> Keine Uhrzeit angegeben >>> Eintrag 4")      
 
      # ######
      # friday
      # ######
      
      if heater.friday_time_1 != "None" and heater.friday_time_1 != None and heater.friday_time_1 != "":
          
         try:
            datetime.datetime.strptime(heater.friday_time_1, "%H:%M")
         except:
            list_errors.append(heater.name + " >>> Freitag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 1 >>> " + heater.friday_time_1)
            
         if heater.friday_temperature_1 == "None" or heater.friday_temperature_1 == None or heater.friday_temperature_1 == "":       
            list_errors.append(heater.name + " >>> Freitag >>> Keine Temperatur angegeben >>> Eintrag 1")
            
      if heater.friday_temperature_1 != "None" and heater.friday_temperature_1 != None and heater.friday_temperature_1 != "":
          
         try:
            error_founded = False
            
            for element in heater.friday_temperature_1:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Freitag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 1 >>> " + heater.friday_temperature_1)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.friday_temperature_1) <= 25:
                  list_errors.append(heater.name + " >>> Freitag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 1 >>> " + heater.friday_temperature_1)
         
         except:
            list_errors.append(heater.name + " >>> Freitag >>> Ungültige Temperatur >>> Eintrag 1 >>> " + heater.friday_temperature_1)

         if heater.friday_time_1 == "None" or heater.friday_time_1 == None or heater.friday_time_1 == "":       
            list_errors.append(heater.name + " >>> Freitag >>> Keine Uhrzeit angegeben >>> Eintrag 1")         
      
      
      if heater.friday_time_2 != "None" and heater.friday_time_2 != None and heater.friday_time_2 != "":
          
         try:
            if datetime.datetime.strptime(heater.friday_time_1, "%H:%M") > datetime.datetime.strptime(heater.friday_time_2, "%H:%M"):
               list_errors.append(heater.name + " >>> Freitag >>> Ungültige Uhrzeit >>> Eintrag 2 >>> muss nach Uhrzeit Eintrag 1 sein >>> " + heater.friday_time_2)
         except:
            list_errors.append(heater.name + " >>> Freitag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 2 >>> " + heater.friday_time_2)
            
         if heater.friday_temperature_2 == "None" or heater.friday_temperature_2 == None or heater.friday_temperature_2 == "":       
            list_errors.append(heater.name + " >>> Freitag >>> Keine Temperatur angegeben >>> Eintrag 2")
          
      if heater.friday_temperature_2 != "None" and heater.friday_temperature_2 != None and heater.friday_temperature_2 != "":
          
         try:
            error_founded = False
            
            for element in heater.friday_temperature_2:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Freitag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 2 >>> " + heater.friday_temperature_2)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.friday_temperature_2) <= 25:
                  list_errors.append(heater.name + " >>> Freitag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 2 >>> " + heater.friday_temperature_2)
         
         except:
            list_errors.append(heater.name + " >>> Freitag >>> Ungültige Temperatur >>> Eintrag 2 >>> " + heater.friday_temperature_2)

         if heater.friday_time_2 == "None" or heater.friday_time_2 == None or heater.friday_time_2 == "":       
            list_errors.append(heater.name + " >>> Freitag >>> Keine Uhrzeit angegeben >>> Eintrag 2")     
 
 
      if heater.friday_time_3 != "None" and heater.friday_time_3 != None and heater.friday_time_3 != "":
          
         try:
            if datetime.datetime.strptime(heater.friday_time_2, "%H:%M") > datetime.datetime.strptime(heater.friday_time_3, "%H:%M"):
               list_errors.append(heater.name + " >>> Freitag >>> Ungültige Uhrzeit >>> Eintrag 3 >>> muss nach Uhrzeit Eintrag 2 sein >>> " + heater.friday_time_3)
         except:
            list_errors.append(heater.name + " >>> Freitag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 3 >>> " + heater.friday_time_3)
            
         if heater.friday_temperature_3 == "None" or heater.friday_temperature_3 == None or heater.friday_temperature_3 == "":       
            list_errors.append(heater.name + " >>> Freitag >>> Keine Temperatur angegeben >>> Eintrag 3")
            
      if heater.friday_temperature_3 != "None" and heater.friday_temperature_3 != None and heater.friday_temperature_3 != "":
          
         try:
            error_founded = False
            
            for element in heater.friday_temperature_3:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Freitag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 3 >>> " + heater.friday_temperature_3)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.friday_temperature_3) <= 25:
                  list_errors.append(heater.name + " >>> Freitag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 3 >>> " + heater.friday_temperature_3)
         
         except:
            list_errors.append(heater.name + " >>> Freitag >>> Ungültige Temperatur >>> Eintrag 3 >>> " + heater.friday_temperature_3)

         if heater.friday_time_3 == "None" or heater.friday_time_3 == None or heater.friday_time_3 == "":       
            list_errors.append(heater.name + " >>> Freitag >>> Keine Uhrzeit angegeben >>> Eintrag 3")       


      if heater.friday_time_4 != "None" and heater.friday_time_4 != None and heater.friday_time_4 != "":
          
         try:
            if datetime.datetime.strptime(heater.friday_time_3, "%H:%M") > datetime.datetime.strptime(heater.friday_time_4, "%H:%M"):
               list_errors.append(heater.name + " >>> Freitag >>> Ungültige Uhrzeit >>> Eintrag 4 >>> muss nach Uhrzeit Eintrag 3 sein >>> " + heater.friday_time_4)
         except:
            list_errors.append(heater.name + " >>> Freitag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 4 >>> " + heater.friday_time_4)
            
         if heater.friday_temperature_4 == "None" or heater.friday_temperature_4 == None or heater.friday_temperature_4 == "":       
            list_errors.append(heater.name + " >>> Freitag >>> Keine Temperatur angegeben >>> Eintrag 4")
               
      if heater.friday_temperature_4 != "None" and heater.friday_temperature_4 != None and heater.friday_temperature_4 != "":
          
         try:
            error_founded = False
            
            for element in heater.friday_temperature_4:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Freitag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 4 >>> " + heater.friday_temperature_4)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.friday_temperature_4) <= 25:
                  list_errors.append(heater.name + " >>> Freitag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 4 >>> " + heater.friday_temperature_4)
         
         except:
            list_errors.append(heater.name + " >>> Freitag >>> Ungültige Temperatur >>> Eintrag 4 >>> " + heater.friday_temperature_4)

         if heater.friday_time_4 == "None" or heater.friday_time_4 == None or heater.friday_time_4 == "":       
            list_errors.append(heater.name + " >>> Freitag >>> Keine Uhrzeit angegeben >>> Eintrag 4")      
 
      # ########
      # saturday
      # ########
      
      if heater.saturday_time_1 != "None" and heater.saturday_time_1 != None and heater.saturday_time_1 != "":
          
         try:
            datetime.datetime.strptime(heater.saturday_time_1, "%H:%M")
         except:
            list_errors.append(heater.name + " >>> Samstag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 1 >>> " + heater.saturday_time_1)
            
         if heater.saturday_temperature_1 == "None" or heater.saturday_temperature_1 == None or heater.saturday_temperature_1 == "":       
            list_errors.append(heater.name + " >>> Samstag >>> Keine Temperatur angegeben >>> Eintrag 1")
            
      if heater.saturday_temperature_1 != "None" and heater.saturday_temperature_1 != None and heater.saturday_temperature_1 != "":
          
         try:
            error_founded = False
            
            for element in heater.saturday_temperature_1:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Samstag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 1 >>> " + heater.saturday_temperature_1)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.saturday_temperature_1) <= 25:
                  list_errors.append(heater.name + " >>> Samstag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 1 >>> " + heater.saturday_temperature_1)
         
         except:
            list_errors.append(heater.name + " >>> Samstag >>> Ungültige Temperatur >>> Eintrag 1 >>> " + heater.saturday_temperature_1)

         if heater.saturday_time_1 == "None" or heater.saturday_time_1 == None or heater.saturday_time_1 == "":       
            list_errors.append(heater.name + " >>> Samstag >>> Keine Uhrzeit angegeben >>> Eintrag 1")         
      
      
      if heater.saturday_time_2 != "None" and heater.saturday_time_2 != None and heater.saturday_time_2 != "":
          
         try:
            if datetime.datetime.strptime(heater.saturday_time_1, "%H:%M") > datetime.datetime.strptime(heater.saturday_time_2, "%H:%M"):
               list_errors.append(heater.name + " >>> Samstag >>> Ungültige Uhrzeit >>> Eintrag 2 >>> muss nach Uhrzeit Eintrag 1 sein >>> " + heater.saturday_time_2)
         except:
            list_errors.append(heater.name + " >>> Samstag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 2 >>> " + heater.saturday_time_2)
            
         if heater.saturday_temperature_2 == "None" or heater.saturday_temperature_2 == None or heater.saturday_temperature_2 == "":       
            list_errors.append(heater.name + " >>> Samstag >>> Keine Temperatur angegeben >>> Eintrag 2")
          
      if heater.saturday_temperature_2 != "None" and heater.saturday_temperature_2 != None and heater.saturday_temperature_2 != "":
          
         try:
            error_founded = False
            
            for element in heater.saturday_temperature_2:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Samstag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 2 >>> " + heater.saturday_temperature_2)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.saturday_temperature_2) <= 25:
                  list_errors.append(heater.name + " >>> Samstag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 2 >>> " + heater.saturday_temperature_2)
         
         except:
            list_errors.append(heater.name + " >>> Samstag >>> Ungültige Temperatur >>> Eintrag 2 >>> " + heater.saturday_temperature_2)

         if heater.saturday_time_2 == "None" or heater.saturday_time_2 == None or heater.saturday_time_2 == "":       
            list_errors.append(heater.name + " >>> Samstag >>> Keine Uhrzeit angegeben >>> Eintrag 2")     
 
 
      if heater.saturday_time_3 != "None" and heater.saturday_time_3 != None and heater.saturday_time_3 != "":
          
         try:
            if datetime.datetime.strptime(heater.saturday_time_2, "%H:%M") > datetime.datetime.strptime(heater.saturday_time_3, "%H:%M"):
               list_errors.append(heater.name + " >>> Samstag >>> Ungültige Uhrzeit >>> Eintrag 3 >>> muss nach Uhrzeit Eintrag 2 sein >>> " + heater.saturday_time_3)
         except:
            list_errors.append(heater.name + " >>> Samstag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 3 >>> " + heater.saturday_time_3)
            
         if heater.saturday_temperature_3 == "None" or heater.saturday_temperature_3 == None or heater.saturday_temperature_3 == "":       
            list_errors.append(heater.name + " >>> Samstag >>> Keine Temperatur angegeben >>> Eintrag 3")
            
      if heater.saturday_temperature_3 != "None" and heater.saturday_temperature_3 != None and heater.saturday_temperature_3 != "":
          
         try:
            error_founded = False
            
            for element in heater.saturday_temperature_3:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Samstag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 3 >>> " + heater.saturday_temperature_3)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.saturday_temperature_3) <= 25:
                  list_errors.append(heater.name + " >>> Samstag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 3 >>> " + heater.saturday_temperature_3)
         
         except:
            list_errors.append(heater.name + " >>> Samstag >>> Ungültige Temperatur >>> Eintrag 3 >>> " + heater.saturday_temperature_3)

         if heater.saturday_time_3 == "None" or heater.saturday_time_3 == None or heater.saturday_time_3 == "":       
            list_errors.append(heater.name + " >>> Samstag >>> Keine Uhrzeit angegeben >>> Eintrag 3")       


      if heater.saturday_time_4 != "None" and heater.saturday_time_4 != None and heater.saturday_time_4 != "":
          
         try:
            if datetime.datetime.strptime(heater.saturday_time_3, "%H:%M") > datetime.datetime.strptime(heater.saturday_time_4, "%H:%M"):
               list_errors.append(heater.name + " >>> Samstag >>> Ungültige Uhrzeit >>> Eintrag 4 >>> muss nach Uhrzeit Eintrag 3 sein >>> " + heater.saturday_time_4)
         except:
            list_errors.append(heater.name + " >>> Samstag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 4 >>> " + heater.saturday_time_4)
            
         if heater.saturday_temperature_4 == "None" or heater.saturday_temperature_4 == None or heater.saturday_temperature_4 == "":       
            list_errors.append(heater.name + " >>> Samstag >>> Keine Temperatur angegeben >>> Eintrag 4")
               
      if heater.saturday_temperature_4 != "None" and heater.saturday_temperature_4 != None and heater.saturday_temperature_4 != "":
          
         try:
            error_founded = False
            
            for element in heater.saturday_temperature_4:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Samstag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 4 >>> " + heater.saturday_temperature_4)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.saturday_temperature_4) <= 25:
                  list_errors.append(heater.name + " >>> Samstag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 4 >>> " + heater.saturday_temperature_4)
         
         except:
            list_errors.append(heater.name + " >>> Samstag >>> Ungültige Temperatur >>> Eintrag 4 >>> " + heater.saturday_temperature_4)

         if heater.saturday_time_4 == "None" or heater.saturday_time_4 == None or heater.saturday_time_4 == "":       
            list_errors.append(heater.name + " >>> Samstag >>> Keine Uhrzeit angegeben >>> Eintrag 4")      
 
      # ######
      # sunday
      # ######
      
      if heater.sunday_time_1 != "None" and heater.sunday_time_1 != None and heater.sunday_time_1 != "":
          
         try:
            datetime.datetime.strptime(heater.sunday_time_1, "%H:%M")
         except:
            list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 1 >>> " + heater.sunday_time_1)
            
         if heater.sunday_temperature_1 == "None" or heater.sunday_temperature_1 == None or heater.sunday_temperature_1 == "":       
            list_errors.append(heater.name + " >>> Sonntag >>> Keine Temperatur angegeben >>> Eintrag 1")
            
      if heater.sunday_temperature_1 != "None" and heater.sunday_temperature_1 != None and heater.sunday_temperature_1 != "":
          
         try:
            error_founded = False
            
            for element in heater.sunday_temperature_1:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 1 >>> " + heater.sunday_temperature_1)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.sunday_temperature_1) <= 25:
                  list_errors.append(heater.name + " >>> Sonntag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 1 >>> " + heater.sunday_temperature_1)
         
         except:
            list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Temperatur >>> Eintrag 1 >>> " + heater.sunday_temperature_1)

         if heater.sunday_time_1 == "None" or heater.sunday_time_1 == None or heater.sunday_time_1 == "":       
            list_errors.append(heater.name + " >>> Sonntag >>> Keine Uhrzeit angegeben >>> Eintrag 1")         
      
      
      if heater.sunday_time_2 != "None" and heater.sunday_time_2 != None and heater.sunday_time_2 != "":
          
         try:
            if datetime.datetime.strptime(heater.sunday_time_1, "%H:%M") > datetime.datetime.strptime(heater.sunday_time_2, "%H:%M"):
               list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Uhrzeit >>> Eintrag 2 >>> muss nach Uhrzeit Eintrag 1 sein >>> " + heater.sunday_time_2)
         except:
            list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 2 >>> " + heater.sunday_time_2)
            
         if heater.sunday_temperature_2 == "None" or heater.sunday_temperature_2 == None or heater.sunday_temperature_2 == "":       
            list_errors.append(heater.name + " >>> Sonntag >>> Keine Temperatur angegeben >>> Eintrag 2")
          
      if heater.sunday_temperature_2 != "None" and heater.sunday_temperature_2 != None and heater.sunday_temperature_2 != "":
          
         try:
            error_founded = False
            
            for element in heater.sunday_temperature_2:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 2 >>> " + heater.sunday_temperature_2)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.sunday_temperature_2) <= 25:
                  list_errors.append(heater.name + " >>> Sonntag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 2 >>> " + heater.sunday_temperature_2)
         
         except:
            list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Temperatur >>> Eintrag 2 >>> " + heater.sunday_temperature_2)

         if heater.sunday_time_2 == "None" or heater.sunday_time_2 == None or heater.sunday_time_2 == "":       
            list_errors.append(heater.name + " >>> Sonntag >>> Keine Uhrzeit angegeben >>> Eintrag 2")     
 
 
      if heater.sunday_time_3 != "None" and heater.sunday_time_3 != None and heater.sunday_time_3 != "":
          
         try:
            if datetime.datetime.strptime(heater.sunday_time_2, "%H:%M") > datetime.datetime.strptime(heater.sunday_time_3, "%H:%M"):
               list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Uhrzeit >>> Eintrag 3 >>> muss nach Uhrzeit Eintrag 2 sein >>> " + heater.sunday_time_3)
         except:
            list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 3 >>> " + heater.sunday_time_3)
            
         if heater.sunday_temperature_3 == "None" or heater.sunday_temperature_3 == None or heater.sunday_temperature_3 == "":       
            list_errors.append(heater.name + " >>> Sonntag >>> Keine Temperatur angegeben >>> Eintrag 3")
            
      if heater.sunday_temperature_3 != "None" and heater.sunday_temperature_3 != None and heater.sunday_temperature_3 != "":
          
         try:
            error_founded = False
            
            for element in heater.sunday_temperature_3:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 3 >>> " + heater.sunday_temperature_3)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.sunday_temperature_3) <= 25:
                  list_errors.append(heater.name + " >>> Sonntag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 3 >>> " + heater.sunday_temperature_3)
         
         except:
            list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Temperatur >>> Eintrag 3 >>> " + heater.sunday_temperature_3)

         if heater.sunday_time_3 == "None" or heater.sunday_time_3 == None or heater.sunday_time_3 == "":       
            list_errors.append(heater.name + " >>> Sonntag >>> Keine Uhrzeit angegeben >>> Eintrag 3")       


      if heater.sunday_time_4 != "None" and heater.sunday_time_4 != None and heater.sunday_time_4 != "":
          
         try:
            if datetime.datetime.strptime(heater.sunday_time_3, "%H:%M") > datetime.datetime.strptime(heater.sunday_time_4, "%H:%M"):
               list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Uhrzeit >>> Eintrag 4 >>> muss nach Uhrzeit Eintrag 3 sein >>> " + heater.sunday_time_4)
         except:
            list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Uhrzeit (Stunden : Minuten) >>> Eintrag 4 >>> " + heater.sunday_time_4)
            
         if heater.sunday_temperature_4 == "None" or heater.sunday_temperature_4 == None or heater.sunday_temperature_4 == "":       
            list_errors.append(heater.name + " >>> Sonntag >>> Keine Temperatur angegeben >>> Eintrag 4")
               
      if heater.sunday_temperature_4 != "None" and heater.sunday_temperature_4 != None and heater.sunday_temperature_4 != "":
          
         try:
            error_founded = False
            
            for element in heater.sunday_temperature_4:
               if not element.isdigit():
                  list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Temperatur (nur ganze Zahlen) >>> Eintrag 4 >>> " + heater.sunday_temperature_4)
                  error_founded = True
                  break
                
            if error_founded == False:
               if not 16 <= int(heater.sunday_temperature_4) <= 25:
                  list_errors.append(heater.name + " >>> Sonntag >>> Ungültiger Temperaturbereich (16 - 25 C°) >>> Eintrag 4 >>> " + heater.sunday_temperature_4)
         
         except:
            list_errors.append(heater.name + " >>> Sonntag >>> Ungültige Temperatur >>> Eintrag 4 >>> " + heater.sunday_temperature_4)

         if heater.sunday_time_4 == "None" or heater.sunday_time_4 == None or heater.sunday_time_4 == "":       
            list_errors.append(heater.name + " >>> Sonntag >>> Keine Uhrzeit angegeben >>> Eintrag 4")      
  
 
   return list_errors


""" ################## """
"""  check led groups  """
""" ################## """

def CHECK_LED_GROUP_SETTINGS(settings):
   list_errors = []

   # check setting open led_slots in groups
   for element in settings:
      
      if element.led_ieeeAddr_1 == None or element.led_ieeeAddr_1 == "None":
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 1")        
      if element.active_led_2 == "True" and (element.led_ieeeAddr_2 == None or element.led_ieeeAddr_2 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 2") 
      if element.active_led_3 == "True" and (element.led_ieeeAddr_3 == None or element.led_ieeeAddr_3 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 3") 
      if element.active_led_4 == "True" and (element.led_ieeeAddr_4 == None or element.led_ieeeAddr_4 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 4") 
      if element.active_led_5 == "True" and (element.led_ieeeAddr_5 == None or element.led_ieeeAddr_5 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 5") 
      if element.active_led_6 == "True" and (element.led_ieeeAddr_6 == None or element.led_ieeeAddr_6 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 6") 
      if element.active_led_7 == "True" and (element.led_ieeeAddr_7 == None or element.led_ieeeAddr_7 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 7") 
      if element.active_led_8 == "True" and (element.led_ieeeAddr_8 == None or element.led_ieeeAddr_8 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 8") 
      if element.active_led_9 == "True" and (element.led_ieeeAddr_9 == None or element.led_ieeeAddr_9 == "None"):
          list_errors.append(element.name + " >>> fehlende Einstellung >>> LED 9")   
          
   return list_errors


""" ############## """
"""  check program """
""" ############## """

def CHECK_PROGRAM(program_id):
   list_errors = []
   
   lines = [[GET_PROGRAM_BY_ID(program_id).line_active_1,  GET_PROGRAM_BY_ID(program_id).line_content_1],
            [GET_PROGRAM_BY_ID(program_id).line_active_2,  GET_PROGRAM_BY_ID(program_id).line_content_2],
            [GET_PROGRAM_BY_ID(program_id).line_active_3,  GET_PROGRAM_BY_ID(program_id).line_content_3],
            [GET_PROGRAM_BY_ID(program_id).line_active_4,  GET_PROGRAM_BY_ID(program_id).line_content_4],
            [GET_PROGRAM_BY_ID(program_id).line_active_5,  GET_PROGRAM_BY_ID(program_id).line_content_5],
            [GET_PROGRAM_BY_ID(program_id).line_active_6,  GET_PROGRAM_BY_ID(program_id).line_content_6],                 
            [GET_PROGRAM_BY_ID(program_id).line_active_7,  GET_PROGRAM_BY_ID(program_id).line_content_7],                 
            [GET_PROGRAM_BY_ID(program_id).line_active_8,  GET_PROGRAM_BY_ID(program_id).line_content_8],                 
            [GET_PROGRAM_BY_ID(program_id).line_active_9,  GET_PROGRAM_BY_ID(program_id).line_content_9],                 
            [GET_PROGRAM_BY_ID(program_id).line_active_10, GET_PROGRAM_BY_ID(program_id).line_content_10],   
            [GET_PROGRAM_BY_ID(program_id).line_active_11, GET_PROGRAM_BY_ID(program_id).line_content_11],   
            [GET_PROGRAM_BY_ID(program_id).line_active_12, GET_PROGRAM_BY_ID(program_id).line_content_12],   
            [GET_PROGRAM_BY_ID(program_id).line_active_13, GET_PROGRAM_BY_ID(program_id).line_content_13],
            [GET_PROGRAM_BY_ID(program_id).line_active_14, GET_PROGRAM_BY_ID(program_id).line_content_14],   
            [GET_PROGRAM_BY_ID(program_id).line_active_15, GET_PROGRAM_BY_ID(program_id).line_content_15],
            [GET_PROGRAM_BY_ID(program_id).line_active_16, GET_PROGRAM_BY_ID(program_id).line_content_16],   
            [GET_PROGRAM_BY_ID(program_id).line_active_17, GET_PROGRAM_BY_ID(program_id).line_content_17],
            [GET_PROGRAM_BY_ID(program_id).line_active_18, GET_PROGRAM_BY_ID(program_id).line_content_18],   
            [GET_PROGRAM_BY_ID(program_id).line_active_19, GET_PROGRAM_BY_ID(program_id).line_content_19],            
            [GET_PROGRAM_BY_ID(program_id).line_active_20, GET_PROGRAM_BY_ID(program_id).line_content_20]]   

   line_number = 0
            
   
   try:
   
      for line in lines:
             
         line_number = line_number + 1

         # line active ?
         if line[0] == "True":
             
             
             # ##################
             #  content function
             # ##################
             
             # break
                     
             if "pause" in line[1]:   
                
                try: 
                   line_content = line[1].split(" /// ")
                    
                   # check delay value            
                   if line_content[1].isdigit():
                       continue
                   else:
                      list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> fehlende Einstellung >>> Sekunden")
                      
                except:
                   list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige Formatierung")

             #  device

             elif "device" in line[1]:
                
                try:
                   line_content = line[1].split(" /// ")

                   device_name = line_content[1]    
                   device      = ""
                   device      = GET_MQTT_DEVICE_BY_NAME(device_name)
                         
                   # check device
                   if device != None:
                      
                      if not "led" in device.device_type:
           
                         program_setting_formated = line_content[2]
                         program_setting_formated = program_setting_formated.replace(" ", "")

                         # convert string to json-format
                         program_setting = program_setting_formated.replace(':', '":"')
                         program_setting = program_setting.replace(',', '","')
                         program_setting = '{"' + str(program_setting) + '"}'    

                         setting_valid = False

                         # check device command 
                         for command in device.commands.split(" "):   
                            if command == program_setting:
                               setting_valid = True

                         if setting_valid == False:
                            list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> falsche Einstellung >>> Befehl ungültig >>> " + program_setting)

                      else:        
                         list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Gerät ist eine LED")

                   else:
                      list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> falsche Einstellung >>> Gerät nicht gefunden >>> " + device_name)
                      
                except:
                   list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige Formatierung")

               
             #  led       
               
             elif "led" in line[1] and "led_group" not in line[1]:
                
                try:        
                   line_content = line[1].split(" /// ")

                   try:
                      # check led name
                      led_name = line_content[1]    
                      led_type = GET_MQTT_DEVICE_BY_NAME(led_name).device_type
                      
                      if "led" in led_type:

                         # check setting led_rgb             
                         if led_type == "led_rgb" and (line_content[2] != "off" and line_content[2] != "OFF"): 
                               
                            try:
                               
                               try:
                               
                                  rgb_values = re.findall(r'\d+', line_content[2])
                               
                                  if not rgb_values[0].isdigit() or not (0 <= int(rgb_values[0]) <= 255):
                                     list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger RGB Wert >>> ROT") 
                                  if not rgb_values[1].isdigit() or not (0 <= int(rgb_values[1]) <= 255):
                                     list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger RGB Wert >>> GRÜN")                   
                                  if not rgb_values[2].isdigit() or not (0 <= int(rgb_values[2]) <= 255):
                                     list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger RGB Wert >>> BLAU")
                                     
                               except:
                                  list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige RGB Einstellungen")
                                                   
                            
                               if not line_content[3].isdigit() or not (0 <= int(line_content[3]) <= 254):
                                  list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Helligkeitswert")
                               
                            except:
                               list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige Formatierung")

           
                         # check setting led_white             
                         elif led_type == "led_white" and (line_content[2] != "off" and line_content[2] != "OFF"): 
                            
                            try:
                            
                               if not line_content[2].isdigit() or not (0 <= int(line_content[2]) <= 7000):
                                  list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige Farbtemperatur")
                                
                               if not line_content[3].isdigit() or not (0 <= int(line_content[3]) <= 254):
                                  list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Helligkeitswert")
                               
                            except:
                               list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige Formatierung")
                               


                         # check setting led_simple             
                         elif led_type == "led_simple" and (line_content[2] != "off" and line_content[2] != "OFF"): 
                            
                            try: 
                            
                               if not line_content[2].isdigit() or not (0 <= int(line_content[2]) <= 254):
                                  list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Helligkeitswert")
                               
                            except:
                               list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige Formatierung")

                          
                         # check setting turn_off             
                         elif line_content[2] == "off" or line_content[2] == "OFF": 
                            pass
                     
                          
                         # nothing founded
                         else:
                            list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige Formatierung")
                                
                      else:        
                         list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Gerät ist keine LED")

                   except:
                      list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> LED nicht gefunden >>> " + led_name)

                except:
                   list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige Formatierung")
                   

             #  led group        
               
             elif "led_group" in line[1]:
                
                try:        
                   line_content = line[1].split(" /// ")

                   try:
                      # check led name
                      led_group_name = line_content[1]    
                      
                      if GET_LED_GROUP_BY_NAME(led_group_name) != None:
                         
                         try:
                         
                             if line_content[2] != "off" and line_content[2] != "OFF":
                                
                                 if GET_LED_SCENE_BY_NAME(line_content[2]) == None: 
                                    list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Szene nicht gefunden >>> " + line_content[2])

                                 if not line_content[3].isdigit() or not (0 <= int(line_content[3]) <= 254):
                                    list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Helligkeitswert")
                                    
                             elif line_content[2] == "off" or line_content[2] == "OFF":
                                 pass
                                
                             else:
                                 list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige Formatierung")                            
        
                         except:
                            list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige Formatierung")
                          
                      else:        
                         list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> LED Gruppe nicht gefunden >>> " + led_group_name)

                   except:
                      list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> LED Gruppe nicht gefunden >>> " + led_group_name)
                      
                except:
                   list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige Formatierung")


             #  spotify 
             
             elif "spotify" in line[1]:
                
                try:        
                   line_content = line[1].split(" /// ")       
                   
                   if (line_content[1].lower() != "play" and
                       line_content[1].lower() != "previous" and
                       line_content[1].lower() != "next" and
                       line_content[1].lower() != "stop" and
                       line_content[1].lower() != "volume" and
                       line_content[1].lower() != "playlist" and
                       line_content[1].lower() != "track" and
                       line_content[1].lower() != "album"):

                       list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Befehl")

                   # volume

                   if line_content[1].lower() == "volume":
                      
                      try:
                         if not line_content[2].isdigit():
                            list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Lautstärkewert")
                        
                         else:
                            if not 0 <= int(line_content[2]) <= 100:
                               list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Zulässige Lautstärke liegt zwischen 0 % und 100 %")
                               
                      except:
                         list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Lautstärkewert")

                   # playlist
       
                   if line_content[1].lower() == "playlist": 
                      
                      try:
                         device_name   = line_content[2]                                    
                         playlist_name = line_content[3]
                         
                         try:
                            if not line_content[4].isdigit():
                               list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Lautstärkewert")
                            
                            else:
                               if not 0 <= int(line_content[4]) <= 100:
                                  list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Zulässige Lautstärke liegt zwischen 0 % und 100 %")

                         except:
                            list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Lautstärkewert")

                      except:
                         list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Unvollständige Angaben")

                   # track
                         
                   if line_content[1].lower() == "track": 
                      
                      try:
                         device_name  = line_content[2]                                    
                         track_title  = line_content[3]
                         track_artist = line_content[4]
                         
                         try:
                            if not line_content[5].isdigit():
                               list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Lautstärkewert")

                            else:
                               if not 0 <= int(line_content[5]) <= 100:
                                  list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Zulässige Lautstärke liegt zwischen 0 % und 100 %")

                         except:
                            list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Lautstärkewert")

                      except:
                         list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Unvollständige Angaben")

                   # album

                   if line_content[1].lower() == "album": 
                      
                      try:
                         device_name  = line_content[2]                                    
                         album_title  = line_content[3]
                         album_artist = line_content[4]
                         
                         try:
                            if not line_content[5].isdigit():
                               list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Lautstärkewert")

                            else:
                               if not 0 <= int(line_content[5]) <= 100:
                                  list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Zulässige Lautstärke liegt zwischen 0 % und 100 %")

                         except:
                            list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültiger Lautstärkewert")

                      except:
                         list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Unvollständige Angaben")

                except:
                   list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> Ungültige Formatierung")


            # None

             elif line[1] == "None":
                 pass


             #  other

             elif line[1] != "":
                list_errors.append("Zeile " + str(line_number) + " >>> " + line[1] + " >>> falsche Einstellung >>> Eingabetyp nicht gefunden")
             
             
   except:
      pass


   return list_errors


""" ####################### """
"""  check sensordata jobs  """
""" ####################### """

def CHECK_SENSORDATA_JOBS_SETTINGS():
   list_errors = []

   entries = GET_ALL_SENSORDATA_JOBS()

   # sensor missing ?
   for entry in entries:
        if entry.mqtt_device_ieeeAddr == "None" or entry.mqtt_device_ieeeAddr == None or entry.mqtt_device_ieeeAddr == "":
            list_errors.append(entry.name + " >>> kein Gerät zugeordnet")       
        if entry.sensor_key == "None" or entry.sensor_key == None or entry.sensor_key == "":
            list_errors.append(entry.name + " >>> kein Sensor zugeordnet")

   return list_errors


""" ######################### """
"""  check scheduler settings """
""" ######################### """

def CHECK_SCHEDULER_GENERAL_SETTINGS(scheduler_tasks): 
   list_general_errors = []  

   for task in scheduler_tasks:

      if task.option_time != "checked" and task.option_sun != "checked" and task.option_sensors != "checked" and task.option_position != "checked":    
         list_general_errors.append(task.name + " >>> Keine Bedingungsoption ausgewählt")          

   return list_general_errors


def CHECK_SCHEDULER_TIME_SETTINGS(scheduler_tasks): 
   list_time_errors = []  

   for task in scheduler_tasks:

      if task.option_time == "checked":

         # check settings sunrise / sunset option
         if task.option_sun == "checked":
            list_time_errors.append(task.name + " >>> Ungültige Kombination >>> Zeit und Sonne nur getrennt verwenden")         

         ### check day

         try:
            if "," in task.day:
                  days = task.day.replace(" ", "")
                  days = days.split(",")
                  for element in days:
                     if element.lower() not in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
                        list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Tag >>> Gültig: Mon, Tue, Wed, Thu, Fri, Sat, Sun, *")
                        break                                 
            else:
                  if task.day.lower() not in ["mon", "tue", "wed", "thu", "fri", "sat", "sun", "*"] and task.day != "*":
                     list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Tag >>> Gültig: Mon, Tue, Wed, Thu, Fri, Sat, Sun, *") 
         except:
            list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Tag >>> Gültig: Mon, Tue, Wed, Thu, Fri, Sat, Sun, *")

         ### check hour
            
         try:
            if "," in task.hour:
                  hours = task.hour.replace(" ", "")                
                  hours = hours.split(",")
                  
                  for element in hours:
 
                     if len(element) == 1 and element != "*":
                        list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Stunde >>> Gültig: 00 - 23, *")
                        break
                    
                     try:
                        if not (0 <= int(element) <= 24):
                           list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Stunde >>> Gültig: 00 - 23, *")
                           break
                        
                     except:
                        list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Stunde >>> Gültig: 00 - 23, *")
                        break   
            else:
                  
               if len(task.hour) == 1 and task.hour != "*":
                  list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Stunde >>> Gültig: 00 - 23, *")
                  break
                
               try:
                  if not (0 <= int(task.hour) <= 24) and task.hour != "*":
                     list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Stunde >>> Gültig: 00 - 23, *") 
               except:
                  if task.hour != "*":
                     list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Stunde >>> Gültig: 00 - 23, *")    

         except:
            list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Stunde >>> Gültig: 00 - 23, *")

         ### check minute

         try:
            if "," in task.minute:
                  minutes = task.minute.replace(" ", "")                 
                  minutes = minutes.split(",")
                  
                  for element in minutes:
                      
                     if len(element) == 1 and element != "*":
                        list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Minute >>> Gültig: 00 - 59, *")
                        break                      
                      
                     try:
                        if not (0 <= int(element) <= 60):
                           list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Minute >>> Gültig: 00 - 59, *") 
                           break
                        
                     except:
                        list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Minute >>> Gültig: 00 - 59, *") 
                        break   
            else:
                
               if len(task.minute) == 1 and task.minute != "*":
                  list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Minute >>> Gültig: 00 - 59, *")
                  break
                
               try:
                  if not (0 <= int(task.minute) <= 60) and task.minute != "*":
                     list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Minute >>> Gültig: 00 - 59, *") 
               except:
                  if task.minute != "*":
                     list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Minute >>> Gültig: 00 - 59, *") 
      
         except:
            list_time_errors.append(task.name + " >>> falsche Zeitangabe >>> Minute >>> Gültig: 00 - 59, *") 

   return list_time_errors


def CHECK_SCHEDULER_SUN_SETTINGS(scheduler_tasks):
   list_sun_errors = []  

   for task in scheduler_tasks:

      if task.option_sun == "checked":

         # check setting location
         if task.option_sunrise == "checked" or task.option_sunset == "checked":
            if task.location == "None":
               list_sun_errors.append(task.name + " >>> Zone wurde noch nicht eingestellt")

   return list_sun_errors


def CHECK_SCHEDULER_SENSOR_SETTINGS(scheduler_tasks): 
   list_sensor_errors = []  

   for task in scheduler_tasks:

      if task.option_sensors == "checked":

         # check mqtt devices
         if task.mqtt_device_ieeeAddr_1 == "None" or task.mqtt_device_ieeeAddr_1 == "" or task.mqtt_device_ieeeAddr_1 == None:
            list_sensor_errors.append(task.name + " >>> fehlende Einstellung >>> MQTT-Gerät 1") 

         if task.mqtt_device_ieeeAddr_2 == "None" or task.mqtt_device_ieeeAddr_2 == "" or task.mqtt_device_ieeeAddr_2 == None:
            if task.operator_main_1 != "None" and task.operator_main_1 != None:
               list_sensor_errors.append(task.name + " >>> fehlende Einstellung >>> MQTT-Gerät 2") 

         if task.mqtt_device_ieeeAddr_3 == "None" or task.mqtt_device_ieeeAddr_3 == "" or task.mqtt_device_ieeeAddr_3 == None:
            if task.operator_main_1 != "None" and task.operator_main_1 != None:
               if task.operator_main_2 != "None" and task.operator_main_2 != None:
                  list_sensor_errors.append(task.name + " >>> fehlende Einstellung >>> MQTT-Gerät 3")  
                  
         # check sensors
         if task.sensor_key_1 == "None" or task.sensor_key_1 == None:
            list_sensor_errors.append(task.name + " >>> fehlende Einstellung >>> Sensor 1") 
            
         if task.operator_main_1 != "None" and task.operator_main_1 != None:
            if task.sensor_key_2 == "None" or task.sensor_key_2 == None:
               list_sensor_errors.append(task.name + " >>> fehlende Einstellung >>> Sensor 2")  
               
         if task.operator_main_2 != "None" and task.operator_main_2 != None:
            if task.sensor_key_3 == "None" or task.sensor_key_3 == None:
               list_sensor_errors.append(task.name + " >>> fehlende Einstellung >>> Sensor 3")

         # check operators
         if task.operator_main_1 != "<" and task.operator_main_1 != ">" and task.operator_main_1 != "=":
            if task.operator_1 == "" or task.operator_1 == "None" or task.operator_1 == None: 
               list_sensor_errors.append(task.name + " >>> fehlende Einstellung >>> Operator 1")
         
         if task.operator_main_1 == "and" or task.operator_main_1 == "or":
            if task.operator_2 == "None" or task.operator_2 == "" or task.operator_2 == None: 
               list_sensor_errors.append(task.name + " >>> fehlende Einstellung >>> Operator 2")  

         if task.operator_main_2 == "and" or task.operator_main_2 == "or":
            if task.operator_3 == "None" or task.operator_3 == "" or task.operator_3 == None: 
               list_sensor_errors.append(task.name + " >>> fehlende Einstellung >>> Operator 3")

         # check values
         if task.operator_main_1 != "<" and task.operator_main_1 != ">" and task.operator_main_1 != "=":   
            if task.value_1 == "" or task.value_1 == "None" or task.value_1 == None: 
               list_sensor_errors.append(task.name + " >>> fehlende Einstellung >>> Vergleichswert 1")   
                  
            elif (task.operator_1 == "<" or task.operator_1 == ">") and not task.value_1.isdigit():
               list_sensor_errors.append(task.name + 
               " >>> ungültiger Eintrag >>> Vergleichswert 1 >>> nur Zahlen können mit dem gewählten Operator verwendet werden") 

         if task.operator_main_1 == "and" or task.operator_main_1 == "or":
            if task.value_2 == "" or task.value_2 == "None" or task.value_2 == None:
               list_sensor_errors.append(task.name + " >>> fehlende Einstellung >>> Vergleichswert 2")  
            elif (task.operator_2 == "<" or task.operator_2 == ">") and not task.value_2.isdigit():
               list_sensor_errors.append(task.name + 
               " >>> ungültiger Eintrag >>> Vergleichswert 2 >>> nur Zahlen können mit dem gewählten Operator verwendet werden")                 

         if task.operator_main_2 == "and" or task.operator_main_2 == "or":
            if task.value_3 == "" or task.value_3 == "None" or task.value_3 == None:
               list_sensor_errors.append(task.name + " >>> fehlende Einstellung >>> Vergleichswert 3")  
            elif (task.operator_3 == "<" or task.operator_3 == ">") and not task.value_3.isdigit():
               list_sensor_errors.append(task.name + 
               " >>> ungültiger Eintrag >>> Vergleichswert 3 >>> nur Zahlen können mit dem gewählten Operator verwendet werden")        
               
   return list_sensor_errors


def CHECK_SCHEDULER_POSITION_SETTINGS(scheduler_tasks):
   list_position_errors = []  

   for task in scheduler_tasks:

      if task.option_position == "checked":

         # check setting choosed
         if task.option_home != "checked" and task.option_away != "checked":
            list_position_errors.append(task.name + " >>> fehlende Einstellung >>> HOME oder AWAY")

         # check setting home / away
         if task.option_home == "checked" and task.option_away == "checked":
            list_position_errors.append(task.name + " >>> Es kann nur HOME oder AWAY separat gewählt werden")

         # check setting ip-addresses
         if task.option_home == "checked" or task.option_away == "checked":

            if task.ip_addresses != "None":
               
               # search for wrong chars
               for element in task.ip_addresses:
                  if not element.isdigit() and element != "." and element != "," and element != " ":
                     list_position_errors.append(task.name + " >>> Ungültige IP-Adressen")
                     break

   return list_position_errors


""" ########################## """
"""  check speech recognition  """
""" ########################## """

def CHECK_SPEECH_RECOGNITION_PROVIDER_SETTINGS(settings):
   list_errors = []

   if settings.snowboy_hotword == "":
      list_errors.append("Kein Snowboy Hotword angegeben") 
   if settings.speech_recognition_provider == "":
      list_errors.append("Keinen Provider angegeben")     
   if settings.speech_recognition_provider_key == "":
      list_errors.append("Keinen Key angegeben")
      
   # check hotword files exist
   hotword_file = GET_SPEECH_RECOGNITION_PROVIDER_SETTINGS().snowboy_hotword
   
   if hotword_file not in GET_ALL_HOTWORD_FILES() and hotword_file != "None":
      list_errors.append("Snowboy Hotword " + str(hotword_file) + " nicht vorhanden")

   return list_errors   


def CHECK_SPEECHCONTROL_LED_TASKS(tasks):
   list_errors = []


   # get list with all keywords
   list_all_keywords = []
   
   for task in tasks:
      
      if task.keywords != None and task.keywords != "None":
      
         list_keywords = task.keywords.split(",")
         
         for keyword in list_keywords:
            keyword = keyword.replace(" ", "")
            list_all_keywords.append(keyword)
   
   
   # search for double keywords
   for task in tasks:
      
      if task.keywords != "":
         
         if task.keywords != None and task.keywords != "None":
         
            keywords = task.keywords.split(",")
            
            for keyword in keywords:
               keyword = keyword.replace(" ", "")
               num = list_all_keywords.count(keyword)
            
               if num > 1:
                  list_errors.append(task.task + " >>> Schlüsselwort doppelt verwendet >>> " + keyword)
                  break
         
   return list_errors


def CHECK_SPEECHCONTROL_TASKS(tasks, task_typ):
   list_errors = []

   # search for missing commands 
   for task in tasks:
      
      if task_typ == "devices":
         if task.setting == None or task.setting == "None":
            list_errors.append(task.task + " >>> Keinen Befehl ausgewählt") 
            
      if task_typ == "programs":
         if task.command == None or task.command == "None":
            list_errors.append(task.task + " >>> Keinen Befehl ausgewählt") 
                        
            
   # search for missing keywords 
   for task in tasks:
      if task.keywords == None or task.keywords == "None":
         list_errors.append(task.task + " >>> Keine Schlüsselwörter eingetragen")             
         
         
   # get list with all keywords
   list_all_keywords = []
   
   for task in tasks:
      
      if task.keywords != None and task.keywords != "None":
      
         list_keywords = task.keywords.split(",")
         
         for keyword in list_keywords:
            keyword = keyword.replace(" ", "")
            list_all_keywords.append(keyword)
   
   
   # search for double keywords
   for task in tasks:
      
      if task.keywords != "":
         
         if task.keywords != None and task.keywords != "None":
         
            keywords = task.keywords.split(",")
            
            for keyword in keywords:
               keyword = keyword.replace(" ", "")
               num = list_all_keywords.count(keyword)
            
               if num > 1:
                  list_errors.append(task.task + " >>> Schlüsselwort doppelt verwendet >>> " + keyword)
                  break
         
   return list_errors


def CHECK_SPEECHCONTROL_SPOTIFY_TASKS(tasks):
   list_errors = []


   # get list with all keywords
   list_all_keywords = []
   
   for task in tasks:
      
      if task.keywords != None and task.keywords != "None":
      
         list_keywords = task.keywords.split(",")
         
         for keyword in list_keywords:
            keyword = keyword.replace(" ", "")
            list_all_keywords.append(keyword)
   
   
   # search for double keywords
   for task in tasks:
      
      if task.keywords != "":
         
         if task.keywords != None and task.keywords != "None":
         
            keywords = task.keywords.split(",")
            
            for keyword in keywords:
               keyword = keyword.replace(" ", "")
               num = list_all_keywords.count(keyword)
            
               if num > 1:
                  list_errors.append(task.task + " >>> Schlüsselwörter doppelt verwendet >>> " + task.keywords)
                  break                   
       
   return list_errors


""" ################### """
"""     check tasks     """
""" ################### """

def CHECK_TASKS(tasks, task_type):
   list_task_errors = []


   if task_type == "scheduler": 

      for element in tasks:

         result = CHECK_TASK_OPERATION(element.task, element.name, task_type)
         
         if result != []:
            
            for error in result:   
               list_task_errors.append(error)
               

   if task_type == "controller": 

      for controller in tasks:

         name = GET_MQTT_DEVICE_BY_IEEEADDR(controller.mqtt_device_ieeeAddr).name

         if controller.command_1 != None and controller.command_1 != "None": 
            result = CHECK_TASK_OPERATION(controller.task_1, name, task_type, controller.command_1)
            
            if result != []:
               
               for error in result:   
                  list_task_errors.append(error)    
               
         if controller.command_2 != None and controller.command_2 != "None": 
            result = CHECK_TASK_OPERATION(controller.task_2, name, task_type, controller.command_2)
            
            if result != []:
               
               for error in result:   
                  list_task_errors.append(error)        
                         
         if controller.command_3 != None and controller.command_3 != "None": 
            result = CHECK_TASK_OPERATION(controller.task_3, name, task_type, controller.command_3)
            
            if result != []:
               
               for error in result:   
                  list_task_errors.append(error)                 
               
         if controller.command_4 != None and controller.command_4 != "None": 
            result = CHECK_TASK_OPERATION(controller.task_4, name, task_type, controller.command_4)
            
            if result != []:
               
               for error in result:   
                  list_task_errors.append(error)       
               
         if controller.command_5 != None and controller.command_5 != "None": 
            result = CHECK_TASK_OPERATION(controller.task_5, name, task_type, controller.command_5)
            
            if result != []:
               
               for error in result:   
                  list_task_errors.append(error)                     
               
         if controller.command_6 != None and controller.command_6 != "None": 
            result = CHECK_TASK_OPERATION(controller.task_6, name, task_type, controller.command_6)
            
            if result != []:
               
               for error in result:   
                  list_task_errors.append(error)       
               
         if controller.command_7 != None and controller.command_7 != "None": 
            result = CHECK_TASK_OPERATION(controller.task_7, name, task_type, controller.command_7)
            
            if result != []:
               
               for error in result:   
                  list_task_errors.append(error)                   
               
         if controller.command_8 != None and controller.command_8 != "None": 
            result = CHECK_TASK_OPERATION(controller.task_8, name, task_type, controller.command_8)
            
            if result != []:
               
               for error in result:   
                  list_task_errors.append(error)                   
                                             
         if controller.command_9 != None and controller.command_9 != "None": 
            result = CHECK_TASK_OPERATION(controller.task_9, name, task_type, controller.command_9)
            
            if result != []:
               
               for error in result:   
                  list_task_errors.append(error)             
    
   return list_task_errors


def CHECK_TASK_OPERATION(task, name, task_type, controller_command = ""):
   
   list_task_errors   = []
   controller_command = controller_command[1:-1].replace('"','')

   try:
      
      # #############
      #  start_scene
      # #############
      
      if "scene" in task:
         if " /// " in task:
            task = task.split(" /// ") 

            # check group setting 
            try:
               group_exist = False

               input_group_name = task[1]
               input_group_name = input_group_name.lower()

               # get exist group names and lower the letters
               all_exist_groups = GET_ALL_LED_GROUPS()
               
               for exist_group in all_exist_groups:
                  
                  exist_group_name       = exist_group.name
                  exist_group_name_lower = exist_group_name.lower()
                  
                  # compare the formated names
                  if input_group_name == exist_group_name_lower: 
                     group_exist = True
                     
               if group_exist == True:
                  pass
                  
               else:
                  if task_type == "controller":
                     list_task_errors.append(name + " >>> " + controller_command + " >>> LED Gruppe nicht vorhanden >>> " + task[1])
                  else:
                     list_task_errors.append(name + " >>> LED Gruppe nicht vorhanden >>> " + task[1])

            except:
               if task_type == "controller":
                  list_task_errors.append(name + " >>> " + controller_command + " >>> fehlende Einstellung >>> LED Gruppe")
               else:
                  list_task_errors.append(name + " >>> fehlende Einstellung >>> LED Gruppe")

            # check scene setting    
            try:
               scene_exist = False

               input_scene_name = task[2]
               input_scene_name = input_scene_name.lower()

               # get exist scene names and lower the letters
               all_exist_scenes = GET_ALL_LED_SCENES()
               
               for exist_scene in all_exist_scenes:
                  
                  exist_scene_name       = exist_scene.name
                  exist_scene_name_lower = exist_scene_name.lower()
                  
                  # compare the formated names
                  if input_scene_name == exist_scene_name_lower: 
                     scene_exist = True
                     
               if scene_exist == True:
                  pass
                  
               else:
                  if task_type == "controller":
                     list_task_errors.append(name + " >>> " + controller_command + " >>> LED Szene nicht vorhanden >>> " + task[2])
                  else:                  
                     list_task_errors.append(name + " >>> LED Szene nicht vorhanden >>> " + task[2])

            except:
               if task_type == "controller":
                  list_task_errors.append(name + " >>> " + controller_command + " >>> fehlende Einstellung >>> LED Szene")
               else:               
                  list_task_errors.append(name + " >>> fehlende Einstellung >>> LED Szene")

            # check global brightness    
            try:
               if task[3].isdigit():
                  if 1 <= int(task[3]) <= 100:
                     return list_task_errors

                  else:
                     if task_type == "controller":
                        list_task_errors.append(name + " >>> " + controller_command + " >>> ungültiger Wertebereich >>> Globale Helligkeit")
                     else:                        
                        list_task_errors.append(name + " >>> ungültiger Wertebereich >>> Globale Helligkeit") 
                     return list_task_errors    

               else:
                  if task_type == "controller":
                     list_task_errors.append(name + " >>> " + controller_command + " >>> ungültige Einstellung >>> Globale Helligkeit")
                  else:                     
                     list_task_errors.append(name + " >>> ungültige Einstellung >>> Globale Helligkeit")
                  return list_task_errors

            except:
               return list_task_errors

         else:
            if task_type == "controller":
               list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültige Formatierung")
            else:                
               list_task_errors.append(name + " >>> Ungültige Formatierung")
            return list_task_errors
     
     
      # ###################
      #  brightness dimmer
      # ###################
      
      
      if "brightness" in task and task_type == "controller":
         if " /// " in task:
            task = task.split(" /// ") 

            # check group setting
            try:
               if GET_LED_GROUP_BY_NAME(task[1]):
                  pass
                  
               else:
                  list_task_errors.append(name + " >>> " + controller_command + " >>> LED Gruppe nicht vorhanden >>> " + task[1])   
                                    
            except:
               list_task_errors.append(name + " >>> " + controller_command + " >>> fehlende Einstellung >>> LED Gruppe")      

            # check brightness setting    
            try:
               if task[2] == "turn_up" or task[2] == "TURN_UP" or task[2] == "turn_down" or task[2] == "TURN_DOWN":
                  return list_task_errors
                  
               else:
                  list_task_errors.append(name + " >>> " + controller_command + " >>> TURN_UP oder TURN_DOWN ?")
                  return list_task_errors
                  
            except:
               list_task_errors.append(name + " >>> " + controller_command + " >>> fehlende Einstellung >>> TURN_UP oder TURN_DOWN")    
               return list_task_errors

         else:
            list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültige Formatierung")
            return list_task_errors


      # #########
      #  led_off
      # #########
      
      
      if "led_off" in task:
         if " /// " in task:
            task = task.split(" /// ")
            
            # check group setting
            if "group" in task[1]:

               try:
                  
                  # get input group names and lower the letters
                  try:
                        list_groups = task[2].split(",")
                  except:
                        list_groups = [task[2]]

                  for input_group_name in list_groups:
                        
                     input_group_name = input_group_name.replace(" ", "")
                     input_group_name = input_group_name.lower()

                     # get exist group names and lower the letters
                     try:
                        all_exist_group = GET_ALL_LED_GROUPS()
                        
                        group_exist = False
                        
                        for exist_group in all_exist_group:
                           
                           exist_group_name = exist_group.name
                           exist_group_name = exist_group_name.lower()
                           
                           # compare the formated names
                           if input_group_name == exist_group_name: 
                              group_exist = True
                           
                        if group_exist == True:
                           pass
                           
                        else:
                           if task_type == "controller":
                              list_task_errors.append(name + " >>> " + controller_command + " >>> LED Gruppe nicht vorhanden >>> " + input_group_name)  
                           else:                               
                              list_task_errors.append(name + " >>> LED Gruppe nicht vorhanden >>> " + input_group_name)  
                        
                        return list_task_errors
                        
                     except:
                        if task_type == "controller":
                           list_task_errors.append(name + " >>> " + controller_command + " >>> fehlende Einstellung >>> LED Gruppe")
                        else:                            
                           list_task_errors.append(name + " >>> fehlende Einstellung >>> LED Gruppe")
                        
                        return list_task_errors
                        
               except:
                  if task_type == "controller":
                     list_task_errors.append(name + " >>> " + controller_command + " >>> fehlende Einstellung >>> LED Gruppe")
                  else:                            
                     list_task_errors.append(name + " >>> fehlende Einstellung >>> LED Gruppe")
                  
                  return list_task_errors 

               
            # check turn off all leds
            elif task[1] == "all" or task[1] == "ALL": 
               return list_task_errors


            else:
               if task_type == "controller":
                  list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültige Eingabe >>> 'all' oder 'group'")
               else:                   
                  list_task_errors.append(name + " >>> Ungültige Eingabe >>> 'all' oder 'group' ?")
               return list_task_errors  


         else:
            if task_type == "controller":
               list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültige Formatierung") 
            else:                   
               list_task_errors.append(name + " >>> Ungültige Formatierung")     
            return list_task_errors


      # ########
      #  device
      # ########
      
      
      if "device" in task and "mqtt_update" not in task:
         if " /// " in task:
            task = task.split(" /// ") 

            try:
               device  = GET_MQTT_DEVICE_BY_NAME(task[1].lower())
               
               setting_formated = task[2]
               setting_formated = setting_formated.replace(" ", "")

               # convert string to json-format
               setting = setting_formated.replace(':', '":"')
               setting = setting.replace(',', '","')
               setting = '{"' + str(setting) + '"}'    

               setting_valid = False

               # check device command 
               for command in device.commands.split(" "):   
                  if command == setting:
                     setting_valid = True
                     break

               if setting_valid == False:

                  if task_type == "controller":
                     list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültiger Befehl >>> " + task[2])
                  else:
                     list_task_errors.append(name + " >>> Ungültiger Befehl >>> " + task[2])
                             
               return list_task_errors                  
              
            except:
               
               if task_type == "controller":
                  list_task_errors.append(name + " >>> " + controller_command + " >>> Gerät nicht gefunden >>> " + task[1])
               else:
                  list_task_errors.append(name + " >>> Gerät nicht gefunden >>> " + task[1])
                  
               return list_task_errors

         else:
            if task_type == "controller":
               list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültige Formatierung")
            else:                
               list_task_errors.append(name + " >>> Ungültige Formatierung")       
            return list_task_errors
            

      # #########
      #  program
      # #########
      
      
      if "program" in task:
         if " /// " in task:
            task = task.split(" /// ") 

            try:
               program = GET_PROGRAM_BY_NAME(task[1].lower())
               setting = task[2].lower()
                  
               if program == None:
               
                  if task_type == "controller":
                     list_task_errors.append(name + " >>> " + controller_command + " >>> Programm nicht gefunden >>> " + task[1])
                  else:
                     list_task_errors.append(name + " >>> " + task[1] + " Programm nicht gefunden")                  
                  
               if setting != "start" and setting != "stop":
                  
                  if task_type == "controller":
                     list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültiger Befehl >>> " + task[2])
                  else:
                     list_task_errors.append(name + " >>> Ungültiger Befehl >>> " + task[2])
               
               return list_task_errors
      
      
            except:
               if task_type == "controller":
                  list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültige Formatierung")
               else:
                  list_task_errors.append(name + " >>> Ungültige Formatierung")
               return list_task_errors
         
         
         else:
            if task_type == "controller":
               list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültige Formatierung")
            else:                
               list_task_errors.append(name + " >>> Ungültige Formatierung")
            return list_task_errors
         

      # #################
      #  watering_plants
      # #################
      
      
      if "watering_plants" in task and task_type == "scheduler":
         if " /// " in task:
            task = task.split(" /// ") 
            
            try:
               if task[1] not in ["1", "2", "3", "4", "5"] and task[1] != "all" and task[1] != "ALL":
                  list_task_errors.append(name + " >>> keine gültige Gruppe angegeben")
            except:
               list_task_errors.append(name + " >>> keine gültige Gruppe angegeben")
            
         else:                
            list_task_errors.append(name + " >>> Ungültige Formatierung")
         return list_task_errors
         

      # ###############
      #  save_database  
      # ###############  
      
           
      if task == "save_database" and task_type == "scheduler":
         return list_task_errors


      # #####################
      #  mqtt_update_devices
      # #####################
      
      
      if task == "mqtt_update_devices" and task_type == "scheduler":
         return list_task_errors


      # ####################
      #  request_sensordata
      # ####################
      
      
      if "request_sensordata" in task and task_type == "scheduler":
         if " /// " in task:
            task = task.split(" /// ")

            # check job name setting
            try:          
               if GET_SENSORDATA_JOB_BY_NAME(task[1]):
                  return list_task_errors

               else:
                  list_task_errors.append(name + " >>> Job nicht vorhanden >>> " + task[1])
                  return list_task_errors   

            except:
               list_task_errors.append(name + " >>> fehlende Einstellung >>> Job-Name") 
               return list_task_errors

         else:
            list_task_errors.append(name + " >>> Ungültige Formatierung")
            return list_task_errors


      # #########
      #  spotify     
      # #########
      
         
      if "spotify" in task:
         if " /// " in task:
            task = task.split(" /// ")

            # check settings
            try:   
                   
               if task[1].lower() == "play":
                  return list_task_errors

               elif task[1].lower() == "previous":
                  return list_task_errors
             
               elif task[1].lower() == "next":
                  return list_task_errors   
                  
               elif task[1].lower() == "stop":
                  return list_task_errors
             
               elif task[1].lower() == "turn_up":
                  return list_task_errors                     
                                 
               elif task[1].lower() == "turn_down":
                  return list_task_errors
             
               elif task[1].lower() == "volume":             
             
                  try:
                     if not task[2].isdigit():
                        list_task_errors.append(name + " >>> """ + task[2] + " >>> Ungültiger Lautstärkewert") 
                     else:
                        if not 0 <= int(task[2]) <= 100:
                           list_task_errors.append(name + " >>> """ + task[2] + " >>> Zulässige Lautstärke liegt zwischen 0 % und 100 %")
                           
                     return list_task_errors
                           
                  except:
                     list_task_errors.append(name + " >>> """ + task[2] + " >>> Ungültiger Lautstärkewert") 
                     return list_task_errors
                  
               elif task[1].lower() == "playlist": 
                  
                  try:
                     device_name   = task[2]                                    
                     playlist_name = task[3]
                     
                     try:
                        if not task[4].isdigit():
                           list_task_errors.append(name + " >>> """ + task[4] + " >>> Ungültiger Lautstärkewert") 
                        else:
                           if not 0 <= int(task[4]) <= 100:
                              list_task_errors.append(name + " >>> """ + task[4] + " >>> Zulässige Lautstärke liegt zwischen 0 % und 100 %")
                              
                        return list_task_errors
                                 
                     except:
                        list_task_errors.append(name + " >>> """ + task[4] + " >>> Ungültiger Lautstärkewert") 
                        return list_task_errors
                        
                  except:
                     list_task_errors.append(name + " >>> """ + str(task) + " >>> Unvollständige Angaben")  
                     return list_task_errors                
                     
               elif task[1].lower() == "track": 
                  
                  try:
                     device_name  = task[2]                                    
                     track_title  = task[3]
                     track_artist = task[4]
                     
                     try:
                        if not task[5].isdigit():
                           list_task_errors.append(name + " >>> """ + task[5] + " >>> Ungültiger Lautstärkewert") 
                        else:
                           if not 0 <= int(task[5]) <= 100:
                              list_task_errors.append(name + " >>> """ + task[5] + " >>> Zulässige Lautstärke liegt zwischen 0 % und 100 %")
                              
                        return list_task_errors
                                 
                     except:
                        list_task_errors.append(name + " >>> """ + task[5] + " >>> Ungültiger Lautstärkewert") 
                        return list_task_errors
                        
                  except:
                     list_task_errors.append(name + " >>> """ + str(task) + " >>> Unvollständige Angaben") 
                     return list_task_errors  

               elif task[1].lower() == "album": 
                  
                  try:
                     device_name  = task[2]                                    
                     album_title  = task[3]
                     album_artist = task[4]
                     
                     try:
                        if not task[5].isdigit():
                           list_task_errors.append(name + " >>> """ + task[5] + " >>> Ungültiger Lautstärkewert") 
                        else:
                           if not 0 <= int(task[5]) <= 100:
                              list_task_errors.append(name + " >>> """ + task[5] + " >>> Zulässige Lautstärke liegt zwischen 0 % und 100 %")
                        
                        return list_task_errors
                                 
                     except:
                        list_task_errors.append(name + " >>> """ + task[5] + " >>> Ungültiger Lautstärkewert") 
                        return list_task_errors
                        
                  except:
                     list_task_errors.append(name + " >>> """ + str(task) + " >>> Unvollständige Angaben") 
                     return list_task_errors                   

               else:
                  if task_type == "controller":
                     list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültiger Befehl >>> " + task[1])
                  else:
                     list_task_errors.append(name + " >>> """ + task[1] + " >>> Ungültiger Befehl")
                  return list_task_errors


            except:
               if task_type == "controller":
                  list_task_errors.append(name + " >>> " + controller_command + " >>> fehlende Einstellung >>> Befehl") 
               else:
                  list_task_errors.append(name + " >>> Befehl >>> fehlende Einstellung") 
               return list_task_errors

                               
         else:
            if task_type == "controller":
               list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültige Formatierung")
            else:
               list_task_errors.append(name + " >>> Ungültige Formatierung")   
            return list_task_errors
            

      # ########################
      #  task "None" controller
      # ########################
      
      if "None" in task and task_type == "controller": 
         return list_task_errors


      # ###############
      #  nothing found
      # ###############
      
      
      if task_type == "controller":
         list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültige Aufgabe") 
      else:
         list_task_errors.append(name + " >>> Ungültige Aufgabe")
         
      return list_task_errors
   
   
   except Exception as e:
      
      if task_type == "controller":
         list_task_errors.append(name + " >>> " + controller_command + " >>> Ungültige Aufgabe")   
      else:
         list_task_errors.append("MISSING NAME >>> Ungültige Aufgabe") 
         
      return list_task_errors


""" ################ """
"""  check watering  """
""" ################ """

def CHECK_WATERING_SETTINGS():
   list_errors = []

   plants  = GET_ALL_PLANTS()
   entries = GET_ALL_PLANTS()

   # check mqtt_device multiple times ?
   for plant in plants:
      for entry in entries:

         if entry.id != plant.id:
            if entry.mqtt_device_ieeeAddr == plant.mqtt_device_ieeeAddr:
               list_errors.append(entry.name + " >>> Gerät mehrmals zugeordnet >>> " + entry.mqtt_device.name)

   # group missing ?
   for entry in entries:
        if entry.group == "None" or entry.group == None:
            list_errors.append(entry.name + " >>> keiner Gruppe zugeteilt")

   # pumptime missing ?
   for entry in entries:
        if entry.pumptime == "None" or entry.pumptime == None:
            list_errors.append(entry.name + " >>> keine Pumpdauer eingestellt")
            
   # moisture missing ?
   for entry in entries:
        if entry.control_sensor_moisture == "checked" and (entry.moisture_level == "None" or entry.moisture_level == None or entry.moisture_level == ""):
            list_errors.append(entry.name + " >>> keine Feuchtigkeit eingestellt")
   
   return list_errors

