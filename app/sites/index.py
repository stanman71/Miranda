from flask import render_template, url_for, request

from app.components.led_control import *
from app.database.database import *
from app.components.file_management import GET_CONFIG_VERSION


""" ##### """
""" index """
""" ##### """

@app.route('/', methods=['GET', 'POST'])
def index():

    version = GET_CONFIG_VERSION()

    return render_template('index.html',
                            version=version,
                            )