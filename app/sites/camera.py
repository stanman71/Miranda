from flask import render_template, redirect, url_for, request, Response
from flask_login import login_required, current_user
from functools import wraps

from app import app
from app.database.database import *
from app.components.checks import CHECK_CAMERA_SETTINGS

import cv2


# access rights
def permission_required(f):
    @wraps(f)
    def wrap(*args, **kwargs): 
        try:
            if current_user.permission_camera == "checked":
                return f(*args, **kwargs)
            else:
                return redirect(url_for('logout'))
        except Exception as e:
            print(e)
            return redirect(url_for('logout'))
        
    return wrap


global_collapse_camera_table = ""


try:
    camera_1_url = "rtsp://" + GET_CAMERA_BY_ID(1).user + ":" + GET_CAMERA_BY_ID(1).password + "@" + GET_CAMERA_BY_ID(1).url 
except:
    camera_1_url = None
 
try:
    camera_2_url = "rtsp://" + GET_CAMERA_BY_ID(2).user + ":" + GET_CAMERA_BY_ID(2).password + "@" + GET_CAMERA_BY_ID(2).url
except:
    camera_2_url = None
    
try:
    camera_3_url = "rtsp://" + GET_CAMERA_BY_ID(3).user + ":" + GET_CAMERA_BY_ID(3).password + "@" + GET_CAMERA_BY_ID(3).url            
except:
    camera_3_url = None

try:
    camera_4_url = "rtsp://" + GET_CAMERA_BY_ID(4).user + ":" + GET_CAMERA_BY_ID(4).password + "@" + GET_CAMERA_BY_ID(4).url              
except:
    camera_4_url = None

try:
    camera_5_url = "rtsp://" + GET_CAMERA_BY_ID(5).user + ":" + GET_CAMERA_BY_ID(5).password + "@" + GET_CAMERA_BY_ID(5).url             
except:
    camera_5_url = None
    
try:
    camera_6_url = "rtsp://" + GET_CAMERA_BY_ID(6).user + ":" + GET_CAMERA_BY_ID(6).password + "@" + GET_CAMERA_BY_ID(6).url               
except:
    camera_6_url = None
    

# generate frame by frame from camera
def GENERATE_FRAME(camera_url):
    
    try:
        # Capture frame-by-frame
        success, frame = cv2.VideoCapture(camera_url).read()  

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

    except:
        pass
    

""" ########### """
""" site camera """
""" ########### """

@app.route('/camera', methods=['GET', 'POST'])
@login_required
@permission_required
def camera():
    global global_collapse_camera_table

    # get current collapse setting and reset global collapse setting
    collapse_camera_table        = global_collapse_camera_table
    global_collapse_camera_table = ""

    error_message_add_camera = []
    
    message_camera_config_change = False

    name     = ""
    url      = ""
    user     = ""
    password = ""
    
    # ##########
    # add camera
    # ########## 

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
                    
                    message_camera_config_change = True
                    
                    name     = ""
                    url      = ""
                    user     = ""
                    password = ""                        


    error_message_camera_settings = CHECK_CAMERA_SETTINGS(GET_ALL_CAMERAS())

    camera_list = GET_ALL_CAMERAS()
    
    
    # ############
    # read cameras
    # ############
    
    try:
        camera_1 = GET_CAMERA_BY_ID(1)
    except:
        camera_1 = None      
    try:
        camera_2 = GET_CAMERA_BY_ID(2)
    except:
        camera_2 = None       
    try:
        camera_3 = GET_CAMERA_BY_ID(3)
    except:
        camera_3 = None
    try:
        camera_4 = GET_CAMERA_BY_ID(4)
    except:
        camera_4 = None
    try:
        camera_5 = GET_CAMERA_BY_ID(5)
    except:
        camera_5 = None
    try:
        camera_6 = GET_CAMERA_BY_ID(6)
    except:
        camera_6 = None        


    return render_template('camera.html',        
                            error_message_add_camera=error_message_add_camera,
                            error_message_camera_settings=error_message_camera_settings,
                            message_camera_config_change=message_camera_config_change,
                            collapse_camera_table=collapse_camera_table,
                            camera_list=camera_list,
                            camera_1=camera_1,    
                            camera_2=camera_2, 
                            camera_3=camera_3,
                            camera_4=camera_4,    
                            camera_5=camera_5, 
                            camera_6=camera_6,                             
                            name=name,
                            url=url,
                            user=user,
                            password=password,                                                                                                                                                             
                            permission_dashboard=current_user.permission_dashboard,
                            permission_scheduler=current_user.permission_scheduler,   
                            permission_programs=current_user.permission_programs,
                            permission_watering=current_user.permission_watering,
                            permission_heating=current_user.permission_heating,                           
                            permission_camera=current_user.permission_camera,  
                            permission_led=current_user.permission_led,
                            permission_sensordata=current_user.permission_sensordata,
                            permission_spotify=current_user.permission_spotify, 
                            permission_system=current_user.permission_system,                      
                            )


# change cameras position 
@app.route('/camera/position/<string:direction>/<int:id>')
@login_required
@permission_required
def change_cameras_position(id, direction):
    global global_collapse_camera_table

    global_collapse_camera_table = "in"

    CHANGE_CAMERAS_POSITION(id, direction)
    return redirect(url_for('dashboard_camera'))


# Delete camera
@app.route('/camera/delete/<int:id>')
@login_required
@permission_required
def delete_camera(id):
    global global_collapse_camera_table

    global_collapse_camera_table = "in"

    DELETE_CAMERA(id)
    return redirect(url_for('camera'))


@app.route('/camera/video_feed_1')
def video_feed_1():
    return Response(GENERATE_FRAME(camera_1_url),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera/video_feed_2')
def video_feed_2():
    return Response(GENERATE_FRAME(camera_2_url),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera/video_feed_3')
def video_feed_3():
    return Response(GENERATE_FRAME(camera_3_url),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
                    
@app.route('/camera/video_feed_4')
def video_feed_4():
    return Response(GENERATE_FRAME(camera_4_url),
                    mimetype='multipart/x-mixed-replace; boundary=frame') 
 
@app.route('/camera/video_feed_5')
def video_feed_5():
    return Response(GENERATE_FRAME(camera_5_url),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera/video_feed_6')
def video_feed_6():
    return Response(GENERATE_FRAME(camera_6_url),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
                   