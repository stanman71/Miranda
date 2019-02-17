from app import app
from app.database.database_operations import *


""" ####### """
""" sensors """
""" ####### """

def READ_SENSOR_GPIO(sensor_name):

    try:

        import gpiozero

        adc = gpiozero.MCP3008(channel = int(sensor_name.slice(-1)))
        voltage = adc.voltage
        return voltage

    except:
        pass