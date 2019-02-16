from flask import Flask
from flask_bootstrap import Bootstrap
import sys


""" ############## """
""" module imports """
""" ############## """

sys.path.insert(0, "./app/")

from components.colorpicker_local import colorpicker


""" ###### """
""" flasks """
""" ###### """

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
Bootstrap(app)
colorpicker(app)

from app.sites import index, user, dashboard, led, schedular, plants, sensors

#app.run(host="0.0.0.0")
app.run(debug=True)