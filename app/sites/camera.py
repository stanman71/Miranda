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


""" ########### """
""" site camera """
""" ########### """

@app.route('/dashboard/camera', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard_camera():

    return render_template('dashboard_camera.html',                                                                                                                                                                                
                            role=current_user.role,                     
                            )