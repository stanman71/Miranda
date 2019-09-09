from flask import render_template, redirect, url_for, request
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from app import app
from app.database.database import *
from app.components.file_management import GET_CONFIG_VERSION
from flask_mobility.decorators import mobile_template


""" ############ """
""" user control """
""" ############ """

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return GET_USER_BY_ID(user_id)


class LoginForm(FlaskForm):
    username = StringField('Benutzername:', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Passwort:', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


""" ##### """
""" login """
""" ##### """

@app.route('/login')
def login():
    logout_user()
    return redirect(url_for('index'))


""" ##### """
""" index """
""" ##### """

@app.route('/', methods=['GET', 'POST'])
@mobile_template('{mobile/}index.html')
def index(template):
    error_message = ""
    form = LoginForm()
    
    version = GET_CONFIG_VERSION()

    if form.validate_on_submit():
        user = GET_USER_BY_NAME(form.username.data)
        
        if user:
            
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                
                if user.permission_dashboard == "checked":
                    return redirect(url_for('dashboard'))
                    
                elif user.permission_scheduler == "checked":
                    return redirect(url_for('scheduler')) 
                                       
                elif user.permission_programs == "checked":
                    return redirect(url_for('programs')) 
                           
                elif user.permission_watering == "checked":
                    return redirect(url_for('watering')) 
 
                elif user.permission_heating == "checked":
                    return redirect(url_for('heating')) 
 
                elif user.permission_camera == "checked":
                    return redirect(url_for('camera'))
                    
                elif user.permission_led == "checked":
                    return redirect(url_for('led_scenes'))   
                                     
                elif user.permission_sensordata == "checked":
                    return redirect(url_for('sensordata_jobs'))  
                          
                elif user.permission_spotify == "checked":
                    return redirect(url_for('spotify'))  
                    
                elif user.permission_system == "checked":
                    return redirect(url_for('system_host'))
                    
                else:
                    error_message = "Keine Zugriffberechtigungen erteilt"
                    return render_template(template, 
                                           form=form,
                                           version=version, 
                                           error_message=error_message)   
                

        return render_template(template, 
                               form=form, 
                               login_check=False, 
                               version=version, 
                               error_message=error_message)


    return render_template(template, 
                           form=form, 
                           version=version, 
                           error_message=error_message)    
                           
      
                           
""" ###### """
""" logout """
""" ###### """

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
