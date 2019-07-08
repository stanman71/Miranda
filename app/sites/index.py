from flask import render_template, url_for, request

from app import app
from app.components.file_management import GET_CONFIG_VERSION
from flask_mobility.decorators import mobile_template


""" ##### """
""" index """
""" ##### """

                            
@app.route('/')
@mobile_template('{mobile/}index.html')
def index(template):
    version = GET_CONFIG_VERSION()
    
    return render_template(template, version=version)
