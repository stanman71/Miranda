from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_apscheduler import APScheduler
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
import sys
import datetime
import os


""" ############## """
""" module imports """
""" ############## """

sys.path.insert(0, "./app/led")
sys.path.insert(0, "./app/components")

# Windows Home
#PATH_CSS = 'C:/Users/stanman/Desktop/Unterlagen/GIT/Python_Projects/SmartHome/app/static/CDNJS/'

# Windows Work
PATH_CSS = 'C:/Users/mstan/GIT/Python_Projects/SmartHome/app/static/CDNJS/'

# RasPi:
#PATH_CSS = '/home/pi/Python/SmartHome/app/static/CDNJS/'

from LED_database import *
from LED_control import *
from sensors_database import *
from sensors_control import *
from watering_plants import *


""" ######## """
""" database """
""" ######## """

# connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smarthome.sqlite3'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# define table structure
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id       = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(50), unique=True)
    email    = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    role     = db.Column(db.String(20), server_default=("user"))

class Schedular(db.Model):
    __tablename__ = 'schedular'
    id     = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name   = db.Column(db.String(50), unique=True)
    day    = db.Column(db.String(50))
    hour   = db.Column(db.String(50))
    minute = db.Column(db.String(50))
    task   = db.Column(db.String(100))
    repeat = db.Column(db.String(50))


""" ############################## """
""" database create default values """
""" ############################## """

# create all database tables
db.create_all()

# create default user
if User.query.filter_by(username='default').first() is None:
    user = User(
        username='default',
        email='member@example.com',
        password=generate_password_hash('qwer1234', method='sha256'),
        role='superuser'
    )
    db.session.add(user)
    db.session.commit()


""" ######### """
""" schedular """
""" ######### """

scheduler = APScheduler()
scheduler.start()   

@scheduler.task('cron', id='scheduler_job', minute='*')
def scheduler_job():
    now    = datetime.datetime.now()
    day    = now.strftime('%a')
    hour   = now.strftime('%H')
    minute = now.strftime('%M')

    #reload database
    db.session.expire_all()
    entries = Schedular.query.all()

    for entry in entries:
        if entry.day == day or entry.day == "*":
            if entry.hour == hour or entry.hour == "*":
                if entry.minute == minute or entry.minute == "*":
                    print(entry.name)
                    # start scene
                    if "start_scene" in entry.task:
                        task = entry.task.split(":")
                        LED_SET_SCENE(int(task[1]))
                    # start program
                    if "start_program" in entry.task:
                        task = entry.task.split(":")
                        START_PROGRAM(int(task[1]))
                    # turn off LEDs
                    if "led_off" in entry.task:
                        task = entry.task.split(":")
                        LED_OFF(int(task[1])) 
                    # read sensor
                    if "read_sensor" in entry.task:
                        task = entry.task.split(":")
                        READ_SENSOR(task[1])  
                    # watering plants
                    if "watering_plants" in entry.task:
                        WATERING_PLANTS()
                    # start LED automatically
                    if "start_smartphone" in entry.task:
                        task = entry.task.split(":")
                        hostname = "google.com"
                        if os.system("ping -n 1 " + hostname) == 0:
                            print("ok")
                            #if READ_SENSOR("GPIO_A07") < 600:
                            #    LED_SET_SCENE(int(task[1]))                                                                                                                        
                    # remove task without repeat
                    if entry.repeat == "":
                        Schedular.query.filter_by(id=entry.id).delete()
                        db.session.commit()


""" ############### """
""" role management """
""" ############### """

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


""" ##### """
""" logIn """
""" ##### """

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email    = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


""" ############ """
""" landing page """
""" ############ """

# landing page
@app.route('/', methods=['GET', 'POST'])
def index():

    connect_bridge  = False
    program_massage = False
    scene = 0
    brightness_global = 100

    value_list = ["", "", "", "", "", "", "", "", ""]

    # connect to the bridge and an update
    led_update = ""
    led_update = UPDATE_LED()

    if request.method == "GET":     
        # change scene   
        try:     
            scene = int(request.args.get("radio_scene"))
            brightness_global = request.args.get("brightness_global")
            LED_SET_SCENE(scene,brightness_global)
            # add radio check
            for i in range (1,10):
                if scene == i:
                    value_list[i-1] = "checked = 'on'"
        except:
            pass

        # select a program   
        try:     
            program = int(request.args.get("radio_program"))
            program_massage = START_PROGRAM(program)            
        except:
            pass

    scene_list   = GET_ALL_SCENES()
    program_list = GET_ALL_PROGRAMS()

    return render_template('index.html', 
                            led_update=led_update,
                            scene_list=scene_list,
                            value_list=value_list,                         
                            brightness_global=brightness_global,
                            program_list=program_list,
                            program_massage=program_massage
                            )


""" ########## """
""" sites user """
""" ########## """

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return render_template('login.html', form=form, login_check=False)

    return render_template('login.html', form=form)


# signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error_massage = ""

    form = RegisterForm()

    if form.validate_on_submit():
        check_entry = User.query.filter_by(username=form.username.data).first()
        if check_entry is None:           
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, role="user")
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            error_massage = "Name schon vergeben"
        
    return render_template('signup.html', 
                            form=form,
                            error_massage=error_massage
                            )


# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)


# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


""" ######### """
""" sites LED """
""" ######### """

# LED scene 01
@app.route('/dashboard/LED/scene_01', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_01():
    scene = 1
    error_massage = ""

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene  = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 
    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html', 
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active01="active",
                            error_massage=error_massage
                            )


# LED scene 02
@app.route('/dashboard/LED/scene_02', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_02():
    scene = 2
    error_massage = ""

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))  
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 
    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html',
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active02="active",
                            error_massage=error_massage
                            )


# LED scene 03
@app.route('/dashboard/LED/scene_03', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_03():
    scene = 3
    error_massage = ""

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i))) 
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 
    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html', 
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active03="active",
                            error_massage=error_massage
                            )


# LED scene 04
@app.route('/dashboard/LED/scene_04', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_04():
    scene = 4
    error_massage = ""

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))      
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 
    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html', 
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active04="active",
                            error_massage=error_massage
                            )


# LED scene 05
@app.route('/dashboard/LED/scene_05', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_05():
    scene = 5
    error_massage = ""

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))     
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 

    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html',
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active05="active",
                            error_massage=error_massage
                            )


# LED scene 06
@app.route('/dashboard/LED/scene_06', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_06():
    scene = 6
    error_massage = ""

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))  
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 
    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html',
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active06="active",
                            error_massage=error_massage
                            )


# LED scene 07
@app.route('/dashboard/LED/scene_07', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_07():
    scene = 7
    error_massage = ""

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i))) 
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 
    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html', 
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active07="active",
                            error_massage=error_massage
                            )


# LED scene 08
@app.route('/dashboard/LED/scene_08', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_08():
    scene = 8
    error_massage = ""

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))      
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 
    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html', 
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active08="active",
                            error_massage=error_massage
                            )


# LED scene 09
@app.route('/dashboard/LED/scene_09', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_scene_09():
    scene = 9
    error_massage = ""

    if request.method == "GET":  
            
        # Change scene name
        name = request.args.get("name") 
        if name is not None:
            error_massage = SET_SCENE_NAME(scene, name)
    
        # Set RGB color
        rgb_scene = []
        for i in range(1,10):
            rgb_scene.append(request.args.get(str(scene) + " " + str(i)))     
        SET_SCENE_COLOR(scene, rgb_scene)

        # Set brightness
        brightness = []
        for i in range(1,10):
            brightness.append(request.args.get(str(i)))
        SET_SCENE_BRIGHTNESS(scene, brightness)  

        # Add LED
        add_LED = request.args.get("LED_scene") 
        if add_LED is not None:
            ADD_LED(scene, add_LED)
 

    if request.method == "POST": 
        # Delete scene
        if 'delete' in request.form:
            DEL_SCENE(scene)

    led_update = ""
    led_update = LED_SET_SCENE(scene)

    entries_scene = GET_SCENE(scene)[0]
    scene_name    = GET_SCENE(scene)[1]
    dropdown_list = GET_DROPDOWN_LIST_LED()

    return render_template('dashboard_LED_scenes.html',
                            led_update=led_update,
                            entries_scene=entries_scene,
                            scene_name=scene_name,
                            dropdown_list=dropdown_list,
                            number=scene,
                            active09="active",
                            error_massage=error_massage
                            )


# Delete LED 
@app.route('/dashboard/LED/scene/delete/<int:scene>/<int:id>')
@login_required
@superuser_required
def delete_LED(scene, id): 
    DEL_LED(scene, id)
    if scene == 1:
        return redirect(url_for('dashboard_LED_scene_01'))
    if scene == 2:
        return redirect(url_for('dashboard_LED_scene_02'))
    if scene == 3:
        return redirect(url_for('dashboard_LED_scene_03'))
    if scene == 4:
        return redirect(url_for('dashboard_LED_scene_04'))
    if scene == 5:
        return redirect(url_for('dashboard_LED_scene_05'))
    if scene == 6:
        return redirect(url_for('dashboard_LED_scene_06'))
    if scene == 7:
        return redirect(url_for('dashboard_LED_scene_07'))
    if scene == 8:
        return redirect(url_for('dashboard_LED_scene_08'))
    if scene == 9:
        return redirect(url_for('dashboard_LED_scene_09'))


# LED programs
@app.route('/dashboard/LED/programs', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_LED_programs():
    program = ""
    rgb = "rgb(0, 0, 0)"
    led_update = ""
    error_massage = ""

    if request.method == "GET": 
        # create a new program
        new_program = request.args.get("new_program") 
        if new_program is not None and new_program is not "":
            error_massage = NEW_PROGRAM(new_program)

        # get the selected program
        get_Program = request.args.get("get_program") 
        if get_Program is not None:
            program = GET_PROGRAM_NAME(get_Program)

        # update programs, i = program ID
        for i in range(1,25):
            update_Program = request.args.get("update_" + str(i))
            if update_Program is not None:
                UPDATE_PROGRAM(i, update_Program)

        # start program
        for i in range(1,25):
            start_Program = request.args.get("start_" + str(i))
            if start_Program is not None:
                led_update = START_PROGRAM(i)

        # get rgb values
        for i in range(1,25):
            get_rgb = request.args.get("get_rgb_" + str(i)) 
            if get_rgb is not None:
                rgb = get_rgb               
                program = GET_PROGRAM_ID(i)  

        # rename program
        for i in range(1,25):
            program_name = request.args.get("program_name_" + str(i)) 
            if program_name is not None:
                SET_PROGRAM_NAME(i, program_name)              
                program = GET_PROGRAM_ID(i)  
            
        # delete the selected program
        delete_Program = request.args.get("delete_program") 
        if delete_Program is not None:
            DELETE_PROGRAM(delete_Program)              

    dropdown_list = GET_DROPDOWN_LIST_PROGRAMS()

    return render_template('dashboard_LED_programs.html',
                            led_update=led_update,
                            dropdown_list=dropdown_list,
                            program=program,
                            rgb=rgb,
                            error_massage=error_massage
                            )


# LED settings
@app.route('/dashboard/LED/settings')
@login_required
@superuser_required
def dashboard_LED_settings():
    led_update = "" 

    if request.method == "GET": 
        # change bridge ip
        bridge_ip = request.args.get("bridge_ip") 
        if bridge_ip is not None:
            SET_BRIDGE_IP(bridge_ip)
            led_update = UPDATE_LED()

    ip = GET_BRIDGE_IP()            
    LED_list = GET_ALL_LEDS()

    return render_template('dashboard_LED_settings.html',
                            led_update=led_update,
                            ip=ip,
                            LED_list=LED_list
                            )


""" ############## """
""" site schedular """
""" ############## """

# Dashboard tasks
@app.route('/dashboard/schedular/', methods=['GET'])
@login_required
@superuser_required
def dashboard_schedular():
    error_massage = ""
    set_name = ""
    set_task = ""

    if request.method == "GET": 
        # add new task
        if request.args.get("set_name") is not None:
            # controll name and task input
            if request.args.get("set_name") == "":
                error_massage = "Kein Name angegeben"
                set_task = request.args.get("set_task")
            elif request.args.get("set_task") == "":
                error_massage = "Keine Aufgabe angegeben"  
                set_name = request.args.get("set_name")             
            else:         
                # get database informations
                name   = request.args.get("set_name")
                day    = request.args.get("set_day") 
                hour   = request.args.get("set_hour") 
                minute = request.args.get("set_minute")
                task   = request.args.get("set_task")
                if request.args.get("checkbox"):
                    repeat = "*"
                else:
                    repeat = ""

                # name exist ?
                check_entry = Schedular.query.filter_by(name=name).first()
                if check_entry is None:
                    # find a unused id
                    for i in range(1,25):
                        if Schedular.query.filter_by(id=i).first():
                            pass
                        else:
                            # add the new task
                            task = Schedular(
                                    id     = i,
                                    name   = name,
                                    day    = day,
                                    hour   = hour,
                                    minute = minute,
                                    task   = task,
                                    repeat = repeat,
                                )
                            db.session.add(task)
                            db.session.commit()
                            break
                else:
                    error_massage = "Name schon vergeben"
 
    schedular_list = Schedular.query.all()

    # dropdown values
    dropdown_list_days    = ["*", "Mon", "Thu", "Wed", "Thu", "Fri", "Sat", "Sun"]
    dropdown_list_hours   = ["*", "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", 
                             "12","13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]
    dropdown_list_minutes = ["*", "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", 
                             "12","13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", 
                             "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36","37",
                             "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48","49", "50",
                             "51", "52", "53", "54", "55", "56", "57", "58", "59"]

    return render_template('dashboard_schedular.html',
                            dropdown_list_days=dropdown_list_days,
                            dropdown_list_hours=dropdown_list_hours,
                            dropdown_list_minutes=dropdown_list_minutes,
                            schedular_list=schedular_list,
                            error_massage=error_massage,
                            set_name=set_name,
                            set_task=set_task
                            )


# Delete tasks
@app.route('/dashboard/schedular/delete/<int:id>')
@login_required
@superuser_required
def delete_schedular(id):
    Schedular.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('dashboard_schedular'))


""" ##################### """
""" sites user management """
""" ##################### """

# Dashboard user
@app.route('/dashboard/user/', methods=['GET', 'POST'])
@login_required
@superuser_required
def dashboard_user():
    user_list = User.query.all()
    return render_template('dashboard_user.html',
                            name=current_user.username,
                            user_list=user_list,
                            )


# Change user role
@app.route('/dashboard/user/role/<int:id>')
@login_required
@superuser_required
def promote_user(id):
    entry = User.query.get(id)
    entry.role = "superuser"
    db.session.commit()
    user_list = User.query.all()
    return redirect(url_for('dashboard_user'))


# Delete user
@app.route('/dashboard/user/delete/<int:id>')
@login_required
@superuser_required
def delete_user(id):
    User.query.filter_by(id=id).delete()
    db.session.commit()
    user_list = User.query.all()
    return redirect(url_for('dashboard_user'))


""" ############ """
""" sites plants """
""" ############ """

@app.route('/dashboard/plants', methods=['GET', 'POST'])
@login_required
def dashboard_plants():
    error_massage = ""
    water_volume = ""
    moisture = ""

    if request.method == "GET": 
        if request.args.get("name") is not None:
            # controll name 
            if request.args.get("name") == "":
                error_massage = "Kein Name angegeben"     
            else:         
                # get informations
                name      = request.args.get("name")
                sensor_id = request.args.get("set_sensor")
                pump_id   = request.args.get("set_pump")
                error_massage = ADD_PLANT(name, sensor_id, pump_id)

        for i in range (1,25):
            # change moisture
            if request.args.get("moisture_" + str(i)):
                moisture = request.args.get("moisture_" + str(i))    
                CHANGE_MOISTURE(i, moisture)

            # change water_volume
            if request.args.get("water_" + str(i)):
                water_volume = request.args.get("water_" + str(i))           
                CHANGE_WATER_VOLUME(i, water_volume)

    dropdown_list_sensor = GET_ALL_SENSORS()
    dropdown_list_pump = [0, 1, 2, 3]
    plants_list = GET_ALL_PLANTS()

    return render_template('dashboard_plants.html',
                            dropdown_list_sensor=dropdown_list_sensor,
                            dropdown_list_pump=dropdown_list_pump,
                            plants_list=plants_list,
                            moisture=moisture,
                            water_volume=water_volume,
                            error_massage=error_massage)


# Delete plant
@app.route('/dashboard/plants/delete/<int:id>')
@login_required
@superuser_required
def delete_plant(id):
    DELETE_PLANT(id)
    return redirect(url_for('dashboard_plants'))


""" ############# """
""" sites sensors """
""" ############# """

@app.route('/dashboard/sensors', methods=['GET', 'POST'])
@login_required
def dashboard_sensors():
    sensor_values = None
    sensor_name = ""
    sensor_id = ""
    error_massage = ""

    if request.method == "GET": 

        # get sensor values
        if request.args.get("get_sensor") is not None:               
            sensor_id = request.args.get("get_sensor")
            sensor_values = GET_SENSOR_VALUES(sensor_id)
            sensor_name = GET_SENSOR_NAME(sensor_id)

            if sensor_values == None:
                error_massage = "Keine Daten vorhanden"    

        # delete the values of a selected sensor
        if request.args.get("delete_values") is not None:
            delete_values = request.args.get("delete_values") 
            error_massage = DELETE_SENSOR_VALUES(delete_values)

    dropdown_list_sensor = GET_ALL_SENSORS()

    return render_template('dashboard_sensors.html',
                            dropdown_list_sensor=dropdown_list_sensor,
                            sensor_values=sensor_values,
                            sensor_name=sensor_name,
                            sensor_id=sensor_id,
                            error_massage=error_massage)


""" ########### """
""" sites MQTT """
""" ########### """

# URL for MQTT sensor values
@app.route('/mqtt/<int:id>/sensor/<string:value>', methods=['GET'])
def mqtt_sensor(id, value):
    
    from sensors_database import SAVE_SENSOR_MQTT
    
    SAVE_SENSOR_MQTT(id, value)
    
    return ("Daten empfangen")


# URL for MQTT control
@app.route('/mqtt/<int:id>/button/<int:button_id>/<int:value>', methods=['GET'])
def mqtt_button(id, button_id, value):
    pass


""" ############### """
""" sites file host """
""" ############### """

# Host files for colorpicker_local
@app.route('/get_media/<path:filename>', methods=['GET'])
def get_media(filename):
    return send_from_directory(PATH_CSS, filename)


