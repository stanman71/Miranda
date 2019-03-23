##  SmartHome

This project creates a smart home environment.

!!! WORK IN PROGRESS !!!


### Features

- flask server 
- control Philips Hue LEDs
- voice control 
- provide a simple script system to create light shows
- read sensors
- share data with ESP8266 moduls by using MQTT
- taskmanagement to automate processes
- watering plants
- SQL-lite database 
- user management and user rights
- smartphone view

------------

### Install the program on Raspberry Pi and setup autostart

- copy all SmartHome files into the folder "/home/pi/SmartHome"
- install the required modules by using sudo rights
- open the autostart-file: "sudo nano /etc/rc.local"
- insert "sudo python3 /home/pi/SmartHome/run.py &" before line "exit 0"
- save the file

------------

### Optional: Install snowboy

- 



------------
 
### Flask server control

- stop the program manually: 

  >>> sudo killall python3

- restart the program manually:

  >>> sudo python3 /home/pi/SmartHome/run.py

