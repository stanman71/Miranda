from flask_mail import Mail, Message
import os

from app import app
from app.database.database import *

def SEND_EMAIL(recipients, subject, body):

    def GET_MAIL_SETTINGS():     
        mail_config = GET_EMAIL_CONFIG()[0]
        if mail_config.mail_encoding == "SSL":
            mail_settings = {
                "MAIL_SERVER"  : mail_config.mail_server_address,
                "MAIL_PORT"    : mail_config.mail_server_port,  
                "MAIL_USE_TLS" : False,
                "MAIL_USE_SSL" : True,
                "MAIL_USERNAME": mail_config.mail_username,
                "MAIL_PASSWORD": mail_config.mail_password,
            }

        else:
            mail_settings = {
                "MAIL_SERVER"  : mail_config.mail_server_address,
                "MAIL_PORT"    : mail_config.mail_server_port,  
                "MAIL_USE_TLS" : True,
                "MAIL_USE_SSL" : False,
                "MAIL_USERNAME": mail_config.mail_username,
                "MAIL_PASSWORD": mail_config.mail_password,
            }  

        return mail_settings 

    app.config.update(GET_MAIL_SETTINGS())
    mail = Mail(app)

    try:
        with app.app_context():
            msg = Message(subject    = subject,
                          sender     = app.config.get("MAIL_USERNAME"),
                          recipients = recipients,
                          body       = body)
            
            # attachment

            """
            # pictures
            with app.open_resource("/home/pi/SmartHome/app/static/images/background.jpg") as fp:
                msg.attach("background.jpg","image/jpg", fp.read())
            with app.open_resource("/home/pi/SmartHome/app/static/images/background-panal.jpg") as fp:
                msg.attach("background-panal.jpg","image/jpg", fp.read())   
              
            # text
            with app.open_resource("C:/Users/mstan/Downloads/uzt.txt") as fp:
                msg.attach("uzt.txt","text/plain", fp.read())   
            """

            mail.send(msg)

        return ""   
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "eMail >>> " + str(e))  
        return ("Fehler in eMail: " + str(e))  
