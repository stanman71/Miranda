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

</br>
------------
</br>

### Install the program on Raspberry Pi and setup autostart

- copy all SmartHome files into the folder "/home/pi/SmartHome"
- install the required modules by using sudo rights
- open the autostart-file: "sudo nano /etc/rc.local"
- insert "sudo python3 /home/pi/SmartHome/run.py &" before line "exit 0"
- save the file

</br>
------------
</br>

### Flask server control

- stop the program manually: 

       >>> sudo killall python3

- restart the program manually:

       >>> sudo python3 /home/pi/SmartHome/run.py


</br>
------------
</br>

### Optional: Install MQTT - Mosquitto 

https://smarthome-blogger.de/tutorial/mqtt-raspberry-pi-einfuehrung/
</br>
https://forum-raspberrypi.de/forum/thread/31959-mosquitto-autostart/
</br>

- install mosquitto

       >>> sudo apt-get update
       >>> sudo apt-get upgrade -y
       >>> sudo apt-get install mosquitto mosquitto-clients -y

- subscribe a channel

       >>> mosquitto_sub -d -h localhost -p 1883 -t "/SmartHome/data"

- test the channel

       >>> mosquitto_pub -d -h localhost -p 1883 -t "/SmartHome/data" -m "Hello"

- create an autostart-file

       >>> sudo nano /etc/systemd/system/Mosquitto.service

- insert and save:

       [Unit]</br>
       Description=MQTT Broker</br>
       After=network.target</br>

       [Service]</br>
       ExecStart=/usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf</br>
       Restart=always</br>

       [Install]</br>
       WantedBy=multi-user.target</br>

- activate the new autostart-file: "sudo systemctl enable Mosquitto.service"

</br>
------------
</br>


### Optional: Install snowboy

https://github.com/Kitt-AI/snowboy
</br>
https://github.com/wanleg/snowboyPi 
</br>
https://snowboy.kitt.ai
</br>
http://docs.kitt.ai/snowboy/
</br>
https://pimylifeup.com/raspberry-pi-snowboy/
</br>
</br>

#### 1. Installation

- Start with a fresh install of Raspbian (Lite or Regular, this guide assumes Lite)

       >>> sudo apt update && sudo apt -y upgrade && sudo apt-get -y auto-remove && sudo reboot

- Install dependencies:

       >>> sudo apt -y install python-pyaudio python3-pyaudio sox python3-pip python-pip libatlas-base-dev

</br>

##### ERROR: Command 'arm-linux-gnueabihf-gcc' failed with exit status 1

- install portaudio first (https://github.com/jgarff/rpi_ws281x/issues/294)

       >>> sudo apt-get install portaudio19-dev

</br>

#### 2. Sound settings

- create ".asoundrc" in your home folder with correct hw settings (see example file in https://github.com/wanleg/snowboyPi or /snowboy/support)

       >>> "aplay -l" & "arecord -l" to find out hw cards (e.g "card 0, device 0" is "hw:0,0")
       >>> "speaker-test -c 2" to test audio out
       >>> "arecord -d 3 test.wav" to record a 3 second test clip 
       >>> "aplay test.wav" to verify

</br>

#### 3. Snowboy

- activate snowboy in the system settings

</br>

##### ERROR: ImportError: dynamic module does not define module export function (PyInit__snowboydetect)

- create snowboydetect again (https://github.com/Kitt-AI/snowboy)
- install swig (https://github.com/Yadoms/yadoms/wiki/Build-on-RaspberryPI)

       >>> wget http://prdownloads.sourceforge.net/swig/swig-3.0.12.tar.gz
       >>> tar xzf swig-3.0.12.tar.gz
       >>> cd swig-3.0.12
       >>> ./configure
       >>> make
       >>> sudo make install

- copy the python3 swig files into "snowboy/swig"
- go into the "swig" folder and start "make" in console 
- replace the old files of the parent dictionary

</br>

##### ERROR: ALSA lib pcm.c:2239:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.<blah blah>

- edit alsa.conf: "sudo nano /usr/share/alsa/alsa.conf" (https://www.raspberrypi.org/forums/viewtopic.php?t=136974)
       
       >>> replace "pcm.front cards.pcm.front" with "pcm.front cards.pcm.default" (app. 15 times)
       >>> fixed "alsa.conf" file in folder support
       
</br>

##### ERROR: ALSA lib confmisc.c:1281:(snd_func_refer) Unable to find definition 'cards.bcm2835_alsa.pcm.front.0:CARD=0'

- if you got many ALBA errors like above and snowboy doesn't work reinstall raspian

</br>

#### 4. Create new Snowboy hotwords

- log into https://snowboy.kitt.ai
- create a new hotword (try to find hotwords as different as possible)
- copy the downloaded file into the folder ~/resources/ on your raspberry pi
- add the new hotword and action in your system settings