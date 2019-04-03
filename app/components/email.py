from flask_mail import Mail, Message
import os

from app import app
from app.database.database import *

def SEND_EMAIL(recipients):

    mail_settings = GET_EMAIL_SETTINGS()[0]

    mail_settings = {
        "MAIL_SERVER": mail_settings.mail_server_address,
        "MAIL_PORT": mail_settings.mail_server_port,  
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME": mail_settings.mail_username,
        "MAIL_PASSWORD": mail_settings.mail_password,
    }

    app.config.update(mail_settings)
    mail = Mail(app)

    try:
        with app.app_context():
                msg = Message(subject="Hello",
                            sender=app.config.get("MAIL_USERNAME"),
                            recipients=[recipients], 
                            body="This is a test email I sent with Gmail and Python!")
                mail.send(msg)
        return ""   
        
    except Exception as e:
        WRITE_LOGFILE_SYSTEM("ERROR", "eMail >>> " + str(e))  
        return ("Fehler in eMail: " + str(e))  