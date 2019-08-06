from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from functools import wraps

from app import app
from app.database.database import *
from app.components.checks import CHECK_CAMERA_SETTINGS

# access rights
def permission_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.permission_camera == "checked":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('logout'))
    return wrap


global_collapse_camera_table = ""


""" ########### """
""" site camera """
""" ########### """

@app.route('/dashboard/camera', methods=['GET', 'POST'])
@login_required
@permission_required
def dashboard_camera():
    global global_collapse_camera_table

    collapse_camera_table        = global_collapse_camera_table
    global_collapse_camera_table = ""

    error_message_add_camera = []

    name     = ""
    url      = ""
    user     = ""
    password = ""

    if request.method == "POST":     

        # add device task
        if request.form.get("add_camera") != None:

            collapse_camera_table = "in"

            # check name
            if request.form.get("set_name") != "":
                name = request.form.get("set_name")
            else:
                error_message_add_camera.append("Keinen Namen angegeben")

            # check url
            if request.form.get("set_url") != "":
                url = request.form.get("set_url")
            else:
                error_message_add_camera.append("Keine URL angegeben")

            user     = request.form.get("set_user")
            password = request.form.get("set_password")   

            if name != "" and url != "":
                error = ADD_CAMERA(name, url, user, password)   

                if error != "":
                    error_message_add_camera.append(error)
                else:
                    name     = ""
                    url      = ""
                    user     = ""
                    password = ""                     
            
        # change camera settings
        if request.form.get("change_camera_settings") != None: 

            collapse_camera_table = "in"

            for i in range (1,10):
                
                if request.form.get("set_name_" + str(i)) != None:

                    if request.form.get("set_name_" + str(i)) != None:  
                        name = request.form.get("set_name_" + str(i))
                    else:
                        name = ""     

                    if request.form.get("set_url_" + str(i)) != None:  
                        url = request.form.get("set_url_" + str(i))
                    else:
                        url = ""

                    if request.form.get("set_user_" + str(i)) != None:  
                        user = request.form.get("set_user_" + str(i))
                    else:
                        user = ""

                    if request.form.get("set_password_" + str(i)) != None:  
                        password = request.form.get("set_password_" + str(i))
                    else:
                        password = ""

                    SET_CAMERA_SETTINGS(i, name, url, user, password)  


    if error_message_add_camera == []:
        error_message_add_camera = ""

    error_message_camera_settings = CHECK_CAMERA_SETTINGS(GET_ALL_CAMERAS())

    camera_list = GET_ALL_CAMERAS()

    try:
        video_feed_01 = GET_CAMERA_BY_ID(1)
    except:
        video_feed_01 = None
    try:
        video_feed_02 = GET_CAMERA_BY_ID(2)
    except:
        video_feed_02 = None
    try:
        video_feed_03 = GET_CAMERA_BY_ID(3)
    except:
        video_feed_03 = None
    try:
        video_feed_04 = GET_CAMERA_BY_ID(4)
    except:
        video_feed_04 = None
    try:
        video_feed_05 = GET_CAMERA_BY_ID(5)
    except:
        video_feed_05 = None
    try:
        video_feed_06 = GET_CAMERA_BY_ID(6)
    except:
        video_feed_06 = None
    try:
        video_feed_07 = GET_CAMERA_BY_ID(7)
    except:
        video_feed_07 = None
    try:
        video_feed_08 = GET_CAMERA_BY_ID(8)
    except:
        video_feed_08 = None
    try:
        video_feed_09 = GET_CAMERA_BY_ID(9)
    except:
        video_feed_09 = None

    return render_template('dashboard_camera.html',        
                            video_feed_01=video_feed_01,    
                            video_feed_02=video_feed_02, 
                            video_feed_03=video_feed_03,       
                            video_feed_04=video_feed_04,    
                            video_feed_05=video_feed_05, 
                            video_feed_06=video_feed_06,   
                            video_feed_07=video_feed_07,    
                            video_feed_08=video_feed_08, 
                            video_feed_09=video_feed_09,   
                            error_message_add_camera=error_message_add_camera,
                            error_message_camera_settings=error_message_camera_settings,
                            collapse_camera_table=collapse_camera_table,
                            camera_list=camera_list,
                            name=name,
                            url=url,
                            user=user,
                            password=password,                                                                                                                                                             
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,  
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system,                      
                            )


# change cameras position 
@app.route('/dashboard/camera/position/<string:direction>/<int:id>')
@login_required
@permission_required
def change_cameras_position(id, direction):
    global global_collapse_camera_table

    global_collapse_camera_table = "in"

    CHANGE_CAMERAS_POSITION(id, direction)
    return redirect(url_for('dashboard_camera'))


# Delete camera
@app.route('/dashboard/camera/delete/<int:id>')
@login_required
@permission_required
def delete_camera(id):
    global global_collapse_camera_table

    global_collapse_camera_table = "in"

    DELETE_CAMERA(id)
    return redirect(url_for('dashboard_camera'))