import datetime
from astral import *


"""

city_name = 'Berlin'

a = Astral()
a.solar_depression = 'civil'

city = a[city_name]
sun = city.sun(date=datetime.date(2009, 4, 22), local=True)

print(sun['sunrise'])


a = Astral()
a.solar_depression = 'civil'

a = Location(("Heidelberg", "Germany", 49.412, -8.71, "Europe/Berlin"))

#a = Location(("Aachen", "Germany", 50.46, -6.5, "Europe/Berlin"))

print(a.sun()['sunrise'])

"""

from Sun import Sun

coords = {'longitude' : 145, 'latitude' : -38 }

sun = Sun()

# Sunrise time UTC (decimal, 24 hour format)
print sun.getSunriseTime( coords )['decimal']

# Sunset time UTC (decimal, 24 hour format)
print sun.getSunsetTime( coords )['decimal']