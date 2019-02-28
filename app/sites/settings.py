from flask import render_template, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
import os

from app import app
from app.components.led_control import *
from app.database.database import *

# create role "superuser"
def superuser_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role == "superuser":
            return f(*args, **kwargs)
        else:
            form = LoginForm()
            return render_template('login.html', form=form, role_check=False)
    return wrap

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


""" ############# """
""" mqtt settings """
""" ############# """

@app.route('/dashboard/settings/mqtt', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_mqtt():
      
    error_message_mqtt = ""
    check_value_mqtt       = ["", ""]

    if request.method == "GET":     
        # change mqtt settings   
        if request.args.get("radio_mqtt") is not None:
            setting_mqtt = str(request.args.get("radio_mqtt"))
            SET_SETTING_VALUE("mqtt", setting_mqtt)

    # change radio check  
    mqtt_setting = GET_SETTING_VALUE("mqtt")    
    if mqtt_setting == "True":
        check_value_mqtt[0] = "checked = 'on'"
        check_value_mqtt[1] = ""
    else:
        check_value_mqtt[0] = ""
        check_value_mqtt[1] = "checked = 'on'"


    return render_template('dashboard_settings_mqtt.html',
                            error_message_mqtt=error_message_mqtt,
                            mqtt_setting=mqtt_setting,
                            check_value_mqtt=check_value_mqtt
                            )
     

""" ################ """
""" snowboy settings """
""" ################ """

@app.route('/dashboard/settings/snowboy', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_snowboy():
      
    error_message_snowboy = ""
    error_message_fileupload = ""
    error_message_table = ""
    sensitivity = ""
    check_value_snowboy    = ["", ""]
    set_name = ""
    set_task = ""

    if request.method == "GET":     
        # change snowboy settings   
        if request.args.get("radio_snowboy") is not None:
            setting_snowboy = str(request.args.get("radio_snowboy"))
            SET_SETTING_VALUE("snowboy", setting_snowboy) 


    if GET_SETTING_VALUE("snowboy") == "True":

        def START_SNOWBOY():
            from app.snowboy.snowboy import SNOWBOY_START
            SNOWBOY_START()
            
        try:
            START_SNOWBOY()
        except Exception as e:
            if "signal only works in main thread" not in str(e):
                error_message_snowboy = "Fehler in SnowBoy: " + str(e)

        # change sensitivity
        if request.method == "GET":
            sensitivity = request.args.get("sensitivity") 
            if sensitivity is not None:
                SET_SENSITIVITY(sensitivity)    

        # add new task
        if request.args.get("set_name") is not None:

            # controll name and task input
            if request.args.get("set_name") == "":
                error_message_table = "Kein Name angegeben"
                set_task = request.args.get("set_task")

            elif request.args.get("set_task") == "":
                error_message_table = "Keine Aufgabe angegeben"  
                set_name = request.args.get("set_name")  
                          
            else:         
                # get database informations
                name   = request.args.get("set_name")
                task   = request.args.get("set_task")

                error_message_table = ADD_SNOWBOY_TASK(name, task)

        # file upload
        if request.method == 'POST':
            if 'file' not in request.files:
                error_message_fileupload = False
            else:
                file = request.files['file']
                if file.filename == '':
                    error_message_fileupload = False
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    error_message_fileupload = True


    # change radio check    
    if GET_SETTING_VALUE("snowboy") == "True":
        check_value_snowboy[0] = "checked = 'on'"
        check_value_snowboy[1] = ""
    else:
        check_value_snowboy[0] = ""
        check_value_snowboy[1] = "checked = 'on'"

    snowboy_setting = GET_SETTING_VALUE("snowboy")
    sensitivity = GET_SENSITIVITY()
    snowboy_list = GET_ALL_SNOWBOY_TASKS()

    # get hotword files
    file_list_temp = []
    file_list = []

    for files in os.walk("./app/snowboy/resources/"):  
        file_list_temp.append(files)
            
    file_list_temp = file_list_temp[0][2]
    for file in file_list_temp:        
        if file != "common.res":
            file_list.append(file)
         
    return render_template('dashboard_settings_snowboy.html',
                            sensitivity=sensitivity,
                            error_message_snowboy=error_message_snowboy,  
                            error_message_table=error_message_table,                  
                            error_message_fileupload=error_message_fileupload,
                            snowboy_setting=snowboy_setting,
                            check_value_snowboy=check_value_snowboy,
                            snowboy_list=snowboy_list,
                            file_list=file_list,
                            set_name=set_name,
                            set_task=set_task         
                            )


# delete snowboy tasks
@app.route('/dashboard/settings/snowboy/delete/task/<int:id>')
@login_required
@superuser_required
def delete_snowboy_task(id):
    DELETE_SNOWBOY_TASK(id)
    return redirect(url_for('dashboard_settings_snowboy'))


# delete snowboy hotwords
@app.route('/dashboard/settings/snowboy/delete/hotword/<string:filename>')
@login_required
@superuser_required
def delete_snowboy_hotword(filename):
    os.remove ('./app/snowboy/resources/' + filename)
    return redirect(url_for('dashboard_settings_snowboy'))


""" ################### """
""" hue bridge settings """
""" ################### """

@app.route('/dashboard/settings/hue_bridge/', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_hue_bridge():
      
    led_update = "" 
    error_message_hue_bridge = ""
    hue_bridge_ip = ""
    led_list = ""
    check_value_hue_bridge = ["", ""]

    if request.method == "GET":     
        # change hue settings   
        if request.args.get("radio_hue_bridge") is not None:
            setting_hue_bridge = str(request.args.get("radio_hue_bridge"))
            SET_SETTING_VALUE("hue_bridge", setting_hue_bridge)

    # change radio check  
    hue_bridge_setting = GET_SETTING_VALUE("hue_bridge")     
    if hue_bridge_setting == "True":
        check_value_hue_bridge[0] = "checked = 'on'"
        check_value_hue_bridge[1] = ""
    else:
        check_value_hue_bridge[0] = ""
        check_value_hue_bridge[1] = "checked = 'on'"


    if hue_bridge_setting == "True":
        if request.method == "GET": 
            # change HUE ip
            hue_bridge_ip = request.args.get("hue_bridge_ip") 
            if hue_bridge_ip is not None:
                SET_HUE_BRIDGE_IP(hue_bridge_ip)
            # update_led_entries
            update_led_entries = request.args.get("update_led_entries") 
            if update_led_entries is not None:           
                UPDATE_LED(GET_LED_NAMES_HUE())    

        led_list = GET_ALL_LEDS()
        hue_bridge_ip = GET_HUE_BRIDGE_IP()  
        error_message_hue_bridge = TEST_HUE_BRIDGE()

    return render_template('dashboard_settings_hue_bridge.html',
                            hue_bridge_ip=hue_bridge_ip,
                            led_list=led_list,
                            error_message_hue_bridge=error_message_hue_bridge,
                            hue_bridge_setting=hue_bridge_setting,
                            check_value_hue_bridge=check_value_hue_bridge,
                            )
    

# remove led
@app.route('/dashboard/settings/hue_bridge/delete/<int:id>')
@login_required
@superuser_required
def remove_hue_bridge_led(id):
    remove_message_led = REMOVE_LED(id)
    return redirect(url_for('dashboard_settings_hue_bridge'))
    

""" ############# """
""" user settings """
""" ############# """

# dashboard user management
@app.route('/dashboard/settings/user/', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_settings_user():
    user_list = GET_ALL_USERS()
    return render_template('dashboard_settings_user.html',
                            name=current_user.username,
                            user_list=user_list,
                            )


# activate user
@app.route('/dashboard/settings/user/role/<int:id>')
@login_required
@superuser_required
def activate_user(id):
    ACTIVATE_USER(id)
    return redirect(url_for('dashboard_settings_user'))


# delete user
@app.route('/dashboard/settings/user/delete/<int:id>')
@login_required
@superuser_required
def delete_user(id):
    DELETE_USER(id)
    return redirect(url_for('dashboard_settings_user'))
