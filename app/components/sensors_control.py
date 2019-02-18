from app import app
from app.database.database import *


""" ####### """
""" sensors """
""" ####### """

def READ_SENSOR_GPIO(sensor_id):

    try:
        import gpiozero

        adc = gpiozero.MCP3008(channel = (int(sensor_id) - 1))
        voltage = adc.voltage
        voltage = round(voltage, 2)
        return voltage

    except:
        pass