from flask import Flask
from flask_bootstrap import Bootstrap

from app.components.colorpicker_local import colorpicker

""" ###### """
""" flasks """
""" ###### """

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
Bootstrap(app)
colorpicker(app)

from app.snowboy.snowboy import SNOWBOY_START
from app.sites import index, user, dashboard, led, schedular, plants, sensors
from app.components.plants_control import *
from app.database.database import *


# stop all pumps
for plant in GET_ALL_PLANTS():
    STOP_PUMP(plant.pump_id) 


# start flask
def START_FLASK_THREAD():

    class flask_Thread(threading.Thread):
        def __init__(self, ID = 1, name = "flask_Thread"):
            threading.Thread.__init__(self)
            self.ID = ID
            self.name = name

        def run(self):
            print("###### Start FLASK ######")


            """ ############## """
            """ initialisation """
            """ ############## """

            @app.before_first_request
            def initialisation():
                pass


            app.run(host="0.0.0.0")
            #app.run(debug=True)
            #app.run()

       
    # start thread
    t1 = flask_Thread()
    t1.start()


START_FLASK_THREAD()

# start snowboy
print("###### Start SNOWBOY ######")
SNOWBOY_START()



""" 

# start flask without threading

@app.before_first_request
def initialisation():
    pass


app.run(host="0.0.0.0")
#app.run(debug=True)
#app.run()

"""




