from flask_sqlalchemy  import SQLAlchemy

from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smarthome.sqlite3'
db = SQLAlchemy(app)

from database_tables import *


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
        return "Name schon vergeben"

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