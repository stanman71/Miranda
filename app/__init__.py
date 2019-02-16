from flask import Flask
from flask_bootstrap import Bootstrap
import sys


""" ############## """
""" module imports """
""" ############## """

sys.path.insert(0, "./app/")

from components.colorpicker_local import colorpicker
from app.sites import index, dashboard, user, led, schedular, plants, sensors


""" ###### """
""" flasks """
""" ###### """

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
Bootstrap(app)
colorpicker(app)


#app.run(host="0.0.0.0")
app.run(debug=True)