from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from functools import wraps

from app import app
from app.components.file_management import GET_LOGFILE_SYSTEM, GET_CONFIG_VERSION

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    error_message = ""

    if GET_LOGFILE_SYSTEM(10) is not None:
        data_log_system = GET_LOGFILE_SYSTEM(10)
    else:
        data_log_system = ""
        error_message = "Keine Einträge gefunden"

    version = GET_CONFIG_VERSION()        

    return render_template('dashboard.html',
                            data_log_system=data_log_system, 
                            version=version,   
                            error_message=error_message,    
                            role=current_user.role,
                            )
