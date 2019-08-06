from flask_mail import Mail, Message
import os

from app import app
from app.database.database import *
from app.components.file_management import WRITE_LOGFILE_SYSTEM


def SEND_EMAIL(subject, body):

    def eMAIL_SETTINGS():     
        settings = GET_EMAIL_SETTINGS()

        if settings.encoding == "SSL":
            mail_settings = {
                "MAIL_SERVER"  : settings.server_address,
                "MAIL_PORT"    : settings.server_port,  
                "MAIL_USE_TLS" : False,
                "MAIL_USE_SSL" : True,
                "MAIL_USERNAME": settings.username,
                "MAIL_PASSWORD": settings.password,
            }

        else:
            mail_settings = {
                "MAIL_SERVER"  : settings.server_address,
                "MAIL_PORT"    : settings.server_port,  
                "MAIL_USE_TLS" : True,
                "MAIL_USE_SSL" : False,
                "MAIL_USERNAME": settings.username,
                "MAIL_PASSWORD": settings.password,
            }  

        return mail_settings 

    app.config.update(eMAIL_SETTINGS())
    mail = Mail(app)

    recipients = GET_EMAIL_ADDRESSES(subject)

    try:
        with app.app_context():
            msg = Message(subject    = "MIRANDA - " + subject,
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

        return "success"   
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "eMail | " + str(recipients) + " | " + subject + " | " + body + " | " + str(e))  
        return ("Fehler in eMail: " + str(e))  
