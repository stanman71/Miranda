from flask_sqlalchemy  import SQLAlchemy
import re
import time

from app import app
from app.database.database_tables import *

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/smarthome.sqlite3'
db = SQLAlchemy(app)


""" ############### """
""" task management """
""" ############### """


def GET_ALL_TASKS():
    return Schedular.query.all()

def ADD_TASK(name, day, hour, minute, task, repeat):
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
                return ""
    else:
        return "Name bereits vergeben"

def DELETE_TASK(task_id):
    Schedular.query.filter_by(id=task_id).delete()
    db.session.commit()


""" ############### """
""" user management """
""" ############### """


def GET_USER_BY_ID(user_id):
    return User.query.get(int(user_id))

def GET_USER_BY_NAME(user_name):
    return User.query.filter_by(username=user_name).first()

def GET_ALL_USERS():
    return User.query.all()

def ADD_USER(user_name, email, password):
    new_user = User(username=user_name, email=email, password=password, role="user")
    db.session.add(new_user)
    db.session.commit()

def ACTIVATE_USER(user_id):
    entry = User.query.get(user_id)
    entry.role = "superuser"
    db.session.commit()

def DELETE_USER(user_id):
    User.query.filter_by(id=user_id).delete()
    db.session.commit()

def GET_EMAIL(email):
    return User.query.filter_by(email=email).first()


""" ###### """
""" bridge """
""" ###### """


def GET_BRIDGE_IP():
    entry = Bridge.query.filter_by().first()
    return (entry.ip)  


def SET_BRIDGE_IP(IP):
    entry = Bridge.query.filter_by().first()
    entry.ip = IP
    db.session.commit() 


""" ### """
""" led """
""" ### """


def GET_DROPDOWN_LIST_LED():
    entry_list = []
    # get all led entries
    entries = LED.query.all()
    for entry in entries:
        # select the led names only
        entry_list.append(entry.name)

    return entry_list


def GET_ALL_LEDS():
    return LED.query.all()


def UPDATE_LED(led_list):
    try:
        for i in range (len(led_list)):
            # check entries and replace them if nessessary
            try:
                check_entry = LED.query.filter_by(id=i+1).first()
                if check_entry.name is not led_list[i]:
                    check_entry.name = led_list[i]
            # add new entires, if they not exist
            except:
                led = LED(
                    id = i + 1,
                    name = led_list[i],
                )    
                db.session.add(led)     

            db.session.commit()  
    except:
        return False    


def ADD_LED(Scene, Name):
    # search for the selected LED entry 
    entry = LED.query.filter_by(name=Name).first() 

    if Scene == 1:
        # LED already exist ?
        check_entry = Scene_01.query.filter_by(led_id=entry.id).first()
        # add new led
        if check_entry is None:
            scene = Scene_01(
                led_id = entry.id,
            )
    if Scene == 2:
        check_entry = Scene_02.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_02(
                led_id = entry.id,
            )
    if Scene == 3:
        check_entry = Scene_03.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_03(
                led_id = entry.id,
            )
    if Scene == 4:
        check_entry = Scene_04.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_04(
                led_id = entry.id,
            )
    if Scene == 5:
        check_entry = Scene_05.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_05(
                led_id = entry.id,
            )      
    if Scene == 6:
        check_entry = Scene_06.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_06(
                led_id = entry.id,
            )
    if Scene == 7:
        check_entry = Scene_07.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_07(
                led_id = entry.id,
            )
    if Scene == 8:
        check_entry = Scene_08.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_08(
                led_id = entry.id,
            )
    if Scene == 9:
        check_entry = Scene_09.query.filter_by(led_id=entry.id).first()
        if check_entry is None:
            scene = Scene_09(
                led_id = entry.id,
            )      

    try:        
        db.session.add(scene)
        db.session.commit()        
    except:
        pass    


def DEL_LED(Scene, ID):
    if Scene == 1:
        Scene_01.query.filter_by(led_id=ID).delete()
    if Scene == 2:
        Scene_02.query.filter_by(led_id=ID).delete()
    if Scene == 3:
        Scene_03.query.filter_by(led_id=ID).delete()
    if Scene == 4:
        Scene_04.query.filter_by(led_id=ID).delete()
    if Scene == 5:
        Scene_05.query.filter_by(led_id=ID).delete()
    if Scene == 6:
        Scene_06.query.filter_by(led_id=ID).delete()
    if Scene == 7:
        Scene_07.query.filter_by(led_id=ID).delete()
    if Scene == 8:
        Scene_08.query.filter_by(led_id=ID).delete()
    if Scene == 9:
        Scene_09.query.filter_by(led_id=ID).delete()

    db.session.commit()


""" ###### """
""" scenes """
""" ###### """


def GET_SCENE(Scene):
    entries = None
    name    = None
    if Scene == 1:
        # scene exist ?
        if Scene_01.query.all():
            # get all settings
            entries = Scene_01.query.all()
            # get the scene name of an other table
            name = entries[0].scene_name.name
    if Scene == 2:
        if Scene_02.query.all():
            entries = Scene_02.query.all()
            name = entries[0].scene_name.name
    if Scene == 3:
        if Scene_03.query.all():
            entries = Scene_03.query.all()
            name = entries[0].scene_name.name
    if Scene == 4:
        if Scene_04.query.all():
            entries = Scene_04.query.all()  
            name = entries[0].scene_name.name
    if Scene == 5:
        if Scene_05.query.all():
            entries = Scene_05.query.all()
            name = entries[0].scene_name.name
    if Scene == 6:
        if Scene_06.query.all():
            entries = Scene_06.query.all()
            name = entries[0].scene_name.name
    if Scene == 7:
        if Scene_07.query.all():
            entries = Scene_07.query.all()
            name = entries[0].scene_name.name
    if Scene == 8:
        if Scene_08.query.all():
            entries = Scene_08.query.all()  
            name = entries[0].scene_name.name
    if Scene == 9:
        if Scene_09.query.all():
            entries = Scene_09.query.all()
            name = entries[0].scene_name.name

    return (entries, name)


def GET_ALL_SCENES():
    entries = Scenes.query.all()
    return (entries)    


def SET_SCENE_NAME(Scene, name):
    check_entry = Scenes.query.filter_by(name=name).first()
    if check_entry is None:
        entry = Scenes.query.filter_by(id=Scene).first()
        entry.name = name
        db.session.commit()
        return ("")
    else:
        return ("Name bereits vergeben")


def SET_SCENE_COLOR(Scene, rgb_scene):
    if Scene == 1:
        # check all array entries
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                # get scene settings
                entry = Scene_01.query.filter_by(led_id=i+1).first()
                # get the rgb values only (source: rgb(xxx, xxx, xxx))
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 2:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_02.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 3:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_03.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 4:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_04.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 5:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_05.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break 
    if Scene == 6:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_06.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 7:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_07.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 8:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_08.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break
    if Scene == 9:
        for i in range(len(rgb_scene)):
            if rgb_scene[i] is not None:
                entry = Scene_09.query.filter_by(led_id=i+1).first()
                rgb_color = re.findall(r'\d+', rgb_scene[i])
                break 

    try:
        entry.color_red   = rgb_color[0]
        entry.color_green = rgb_color[1]           
        entry.color_blue  = rgb_color[2]
        db.session.commit()
    except:
        pass
    

def SET_SCENE_BRIGHTNESS(Scene, brightness):
    if Scene == 1:
        # check all array entries
        for i in range(len(brightness)):
            if brightness[i] is not None:
                # get scene settings
                entry = Scene_01.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 2:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_02.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 3:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_03.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break            
    if Scene == 4:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_04.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 5:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_05.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 6:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_06.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 7:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_07.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break            
    if Scene == 8:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_08.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break
    if Scene == 9:
        for i in range(len(brightness)):
            if brightness[i] is not None:
                entry = Scene_09.query.filter_by(led_id=i+1).first()
                brightness = brightness[i]
                break

    try:
        entry.brightness = brightness
        db.session.commit()
    except:
        pass


def DEL_SCENE(Scene):
    if Scene == 1:
        # delete scene settings
        Scene_01.query.delete()
    if Scene == 2:
        Scene_02.query.delete()
    if Scene == 3:
        Scene_03.query.delete()
    if Scene == 4:
        Scene_04.query.delete()
    if Scene == 5:
        Scene_05.query.delete()
    if Scene == 6:
        Scene_06.query.delete()
    if Scene == 7:
        Scene_07.query.delete()
    if Scene == 8:
        Scene_08.query.delete()
    if Scene == 9:
        Scene_09.query.delete()

    # delete scene name
    entry = Scenes.query.get(Scene)
    entry.name = ""
    db.session.commit()


""" ######## """
""" programs """
""" ######## """


def NEW_PROGRAM(name):
    # name exist ?
    check_entry = Programs.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,25):
            if Programs.query.filter_by(id=i).first():
                pass
            else:
                # add the new program
                program = Programs(
                        id = i,
                        name = name,
                        content = "",
                    )
                db.session.add(program)
                db.session.commit()
                return ("")
    else:
        return ("Name bereits vergeben")


def GET_DROPDOWN_LIST_PROGRAMS():
    entry_list = []
    # get all Programs
    entries = Programs.query.all()
    for entry in entries:
        # select the Programs names only
        entry_list.append(entry.name)

    return entry_list


def GET_ALL_PROGRAMS():
    return Programs.query.all()   


def GET_PROGRAM_NAME(name):
    return Programs.query.filter_by(name=name).first()


def GET_PROGRAM_ID(id):
    return Programs.query.filter_by(id=id).first()


def SET_PROGRAM_NAME(id, name):
    check_entry = Programs.query.filter_by(name=name).first()
    if check_entry is None:
        entry = Programs.query.filter_by(id=id).first()
        entry.name = name
        db.session.commit()    


def UPDATE_PROGRAM(id, content):
    entry = Programs.query.filter_by(id=id).update(dict(content=content))
    db.session.commit()


def DELETE_PROGRAM(name):
    Programs.query.filter_by(name=name).delete()
    db.session.commit()


""" ####### """
""" plants  """
""" ####### """


def GET_ALL_PLANTS():
    return Plants.query.all()


def ADD_PLANT(name, sensor_id, pump_id, water_volume):

    # name exist ?
    check_entry = Plants.query.filter_by(name=name).first()
    if check_entry is None:
        # find a unused id
        for i in range(1,25):
            if Plants.query.filter_by(id=i).first():
                pass
            else:
                # add the new plant
                plant = Plants(
                        id           = i,
                        name         = name,
                        sensor_id    = sensor_id,
                        pump_id      = pump_id,
                        moisture     = 0,
                        water_volume = water_volume,
                    )
                db.session.add(plant)
                db.session.commit()
                return ""
    else:
        return "Name bereits vergeben"


def CHANGE_MOISTURE(plant_id, moisture):    
    entry = Plants.query.filter_by(id=plant_id).first()
    entry.moisture = moisture
    # calculate voltage value
    voltage_value = round((float(moisture) * 1.6) / 100, 2) 
    moisture_voltage = round(2.84 - voltage_value, 2)   
    entry.moisture_voltage = moisture_voltage
    db.session.commit()  


def CHANGE_WATER_VOLUME(plant_id, water_volume):        
    entry = Plants.query.filter_by(id=plant_id).first()
    entry.water_volume = water_volume
    db.session.commit()    


def DELETE_PLANT(plant_id):
    Plants.query.filter_by(id=plant_id).delete()
    db.session.commit()


""" ###### """
""" sensor """
""" ###### """


def GET_ALL_SENSORS():
    return Sensor.query.all()


def GET_SENSOR_NAME(sensor_id):
    sensor_name = Sensor.query.filter_by(id=sensor_id).first()
    return sensor_name.name  


def GET_SENSOR_VALUES(id):

    sensor_name = Sensor.query.filter_by(id=id).first()
    sensor_name = sensor_name.name

    if sensor_name == "GPIO_A00":
        sensor_values = Sensor_GPIO_A00.query.all()
    if sensor_name == "GPIO_A01":
        sensor_values = Sensor_GPIO_A01.query.all()
    if sensor_name == "GPIO_A02":
        sensor_values = Sensor_GPIO_A02.query.all()
    if sensor_name == "GPIO_A03":
        sensor_values = Sensor_GPIO_A03.query.all()
    if sensor_name == "GPIO_A04":
        sensor_values = Sensor_GPIO_A04.query.all()
    if sensor_name == "GPIO_A05":
        sensor_values = Sensor_GPIO_A05.query.all()
    if sensor_name == "GPIO_A06":
        sensor_values = Sensor_GPIO_A06.query.all()
    if sensor_name == "GPIO_A07":
        sensor_values = Sensor_GPIO_A07.query.all()        
    if sensor_name == "MQTT_00":
        sensor_values = Sensor_MQTT_00.query.all()
    if sensor_name == "MQTT_01":
        sensor_values = Sensor_MQTT_01.query.all()
    if sensor_name == "MQTT_02":
        sensor_values = Sensor_MQTT_02.query.all()
    
    if sensor_values == []:
        return None
    else:
        return sensor_values


def SAVE_SENSOR_GPIO(sensor_name):

    try:

        import gpiozero

        if sensor_name == "GPIO_A00":
            adc = gpiozero.MCP3008(channel = 0)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A00(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A01":
            adc = gpiozero.MCP3008(channel = 1)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A01(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A02":
            adc = gpiozero.MCP3008(channel = 2)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A02(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A03":
            adc = gpiozero.MCP3008(channel = 3)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A03(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A04":
            adc = gpiozero.MCP3008(channel = 4)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A04(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A05":
            adc = gpiozero.MCP3008(channel = 5)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A05(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A06":
            adc = gpiozero.MCP3008(channel = 6)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A06(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   
        if sensor_name == "GPIO_A07":
            adc = gpiozero.MCP3008(channel = 7)
            voltage = adc.voltage
            result = "%.2f V" % voltage
            entry = Sensor_GPIO_A07(
                value = result,
                date  = time.strftime("%Y-%m-%d %H:%M"),
            )   

        db.session.add(entry)
        db.session.commit()   

    except:
        pass


def SAVE_SENSOR_MQTT(mqtt, result):
    
    if mqtt == 0:
        entry = Sensor_MQTT_00(
            value = result,
            date  = time.strftime("%Y-%m-%d %H:%M"),
        ) 
    if mqtt == 1:
        entry = Sensor_MQTT_01(
            value = result,
            date  = time.strftime("%Y-%m-%d %H:%M"),
        ) 
    if mqtt == 2:
        entry = Sensor_MQTT_02(
            value = result,
            date  = time.strftime("%Y-%m-%d %H:%M"),
        ) 

    db.session.add(entry)
    db.session.commit()   


def DELETE_SENSOR_VALUES(id):

    sensor_name = Sensor.query.filter_by(id=id).first()
    sensor_name = sensor_name.name

    if sensor_name == "GPIO_A00":
        Sensor_GPIO_A00.query.delete()
    if sensor_name == "GPIO_A01":
        Sensor_GPIO_A01.query.delete()
    if sensor_name == "GPIO_A02":
        Sensor_GPIO_A02.query.delete()
    if sensor_name == "GPIO_A03":
        Sensor_GPIO_A03.query.delete()
    if sensor_name == "GPIO_A04":
        Sensor_GPIO_A04.query.delete()
    if sensor_name == "GPIO_A05":
        Sensor_GPIO_A05.query.delete()
    if sensor_name == "GPIO_A06":
        Sensor_GPIO_A06.query.delete()
    if sensor_name == "GPIO_A07":
        Sensor_GPIO_A07.query.delete()
    if sensor_name == "MQTT_00":
        Sensor_MQTT_00.query.delete()
    if sensor_name == "MQTT_01":
        Sensor_MQTT_01.query.delete()
    if sensor_name == "MQTT_02":
        Sensor_MQTT_02.query.delete()

    db.session.commit() 
    return "Werte gelöscht"
