from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps

from app import app
from app.database.database import *


# access rights
def user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "user" or current_user.role == "superuser":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


""" ############ """
""" site spotify """
""" ############ """

@app.route('/dashboard/spotify', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_spotify():

    return render_template('dashboard_spotify.html',                                                                                                                                                                                
                            role=current_user.role,                     
                            )