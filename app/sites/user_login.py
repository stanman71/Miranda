from flask import render_template, redirect, url_for, request
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from app import app
from app.database.database import *


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

class RegisterForm(FlaskForm):
    email    = StringField('eMail-Adresse:', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Benutzername:', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Passwort:', validators=[InputRequired(), Length(min=8, max=80)])


""" ########## """
""" user sites """
""" ########## """

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = GET_USER_BY_NAME(form.username.data)
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return render_template('login.html', form=form, login_check=False)

    return render_template('login.html', form=form)


# signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error_message = ""

    form = RegisterForm()

    if form.validate_on_submit():
        check_name  = GET_USER_BY_NAME(form.username.data)
        check_email = GET_EMAIL(form.email.data)
        if check_name is not None:     
            error_message = "Name schon vergeben"
        elif check_email is not None:     
            error_message = "eMail schon vergeben"
        else:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            ADD_USER(form.username.data, form.email.data, hashed_password)
            return redirect(url_for('index'))
      
    return render_template('signup.html', 
                            form=form,
                            error_message=error_message
                            )


# logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))