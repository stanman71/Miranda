##  Miranda

This project creates a smarthome environment.

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

### Install Miranda

#### 1. Installation 

- copy all Miranda files into the folder "/home/pi/miranda"
- install the required modules by using sudo rights

</br>

#### 2. Autostart

https://www.raspberrypi-spy.co.uk/2015/02/how-to-autorun-a-python-script-on-raspberry-pi-boot/
</br>
</br>

- open file profile

       >>> sudo nano /etc/profile

- scroll to the bottom and add the following line :

       >>> sudo python3 /home/pi/miranda/run.py &
	  
- enable the Pi to login automatically without requiring any user intervention

       >>> sudo raspi-config
       >>> Select “Boot Options” then “Desktop/CLI” then “Console Autologin”	   

</br>

#### 3. Manually Control 

- stop the program 

       >>> sudo killall python3

- restart the program 

       >>> sudo python3 /home/pi/miranda/run.py


</br>
------------
</br>

### Optional: Install Mosquitto (MQTT)

https://smarthome-blogger.de/tutorial/mqtt-raspberry-pi-einfuehrung/
</br>
https://forum-raspberrypi.de/forum/thread/31959-mosquitto-autostart/
</br>

#### 1. Installation

       >>> sudo apt-get update
       >>> sudo apt-get upgrade -y
       >>> sudo apt-get install mosquitto mosquitto-clients -y

</br>

#### 2. Test

- subscribe a channel

       >>> mosquitto_sub -d -h localhost -p 1883 -t "/SmartHome/data"

- send a message

       >>> mosquitto_pub -d -h localhost -p 1883 -t "/SmartHome/data" -m "Hello"

</br>

#### 3. Autostart

- create an autostart-file

       >>> sudo nano /etc/systemd/system/Mosquitto.service

       [Unit]
       Description=MQTT Broker
       After=network.target

       [Service]
       ExecStart=/usr/sbin/mosquitto -c /etc/mosquitto/mosquitto.conf
       Restart=always

       [Install]
       WantedBy=multi-user.target

- enable autostart

       >>> sudo systemctl enable Mosquitto.service

- start service

       >>> sudo systemctl start Mosquitto

- show status

       >>> systemctl status Mosquitto.service

- stop service

       >>> sudo systemctl stop Mosquitto


</br>
------------
</br>

### Optional: Install ZigBee2MQTT

https://gadget-freakz.com/diy-zigbee-gateway/
</br>
https://www.zigbee2mqtt.io/
</br>

#### 1. Installation

- install Node.js

       >>> sudo curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
       >>> sudo apt-get install -y nodejs git make g++ gcc

- verify that the correct nodejs and npm (automatically installed with nodejs)

       >>> node --version  # Should output v10.X
       >>> npm  --version  # Should output 6.X

- clone zigbee2mqtt repository

       >>> sudo git clone https://github.com/Koenkk/zigbee2mqtt.git /opt/zigbee2mqtt
       >>> sudo chown -R pi:pi /opt/zigbee2mqtt

- install zigbee2mqtt 

       >>> cd /opt/zigbee2mqtt
       >>> npm install
	   
	   >>> Note that the npm install produces some warning which can be ignored.

</br>

#### 2. Configuration

- edit configuration.yaml

       >>> nano /opt/zigbee2mqtt/data/configuration.yaml

       # MQTT settings
       mqtt:
       # MQTT base topic for zigbee2mqtt MQTT messages
       base_topic: /SmartHome/zigbee2mqtt
       # MQTT server URL
       server: 'mqtt://localhost'
       # MQTT server authentication, uncomment if required:
       # user: my_user
       # password: my_password

</br>

#### 3. Bridge Software

- start command

       >>> cd /opt/zigbee2mqtt
       >>> npm start

- stop command

       >>> sudo systemctl stop zigbee2mqtt

- view the log of zigbee2mqtt

       >>> sudo journalctl -u zigbee2mqtt.service -f

- backup configuration

       >>> cp -R data data-backup

</br>

#### 4. Pairing

- bridge software must be running to pairing new devices automatically
- zigbee2mqtt setting: {permit_join: true}

</br>

#### 5. Autostart

- run zigbee2mqtt as daemon in the background automaticly when booting

       >>> sudo nano /etc/systemd/system/zigbee2mqtt.service

       [Unit]
       Description=zigbee2mqtt
       After=network.target

       [Service]
       ExecStart=/usr/bin/npm start
       WorkingDirectory=/opt/zigbee2mqtt
       StandardOutput=inherit
       StandardError=inherit
       Restart=always
       User=pi

       [Install]
       WantedBy=multi-user.target

- enable autostart

       >>> sudo systemctl enable zigbee2mqtt.service

- start service

       >>> sudo systemctl start zigbee2mqtt

- show status

       >>> systemctl status zigbee2mqtt.service

- stop service

       >>> sudo systemctl stop zigbee2mqtt


</br>
------------
</br>

### Optional: Zigbee2MQTT Hardware

https://www.zigbee2mqtt.io/getting_started/flashing_the_cc2531.html
</br>
https://www.zigbee2mqtt.io/information/connecting_cc2530.html
</br>
https://github.com/Koenkk/zigbee2mqtt/issues/1437
</br>
https://github.com/Koenkk/zigbee2mqtt/issues/489


</br>
------------
</br>

### Optional: Install Snowboy

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

- update raspbian 

       >>> sudo apt update && sudo apt -y upgrade && sudo apt-get -y auto-remove && sudo reboot

- install dependencies

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

- activate snowboy in the SmartHome system settings
- restart SmartHome

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


</br>
------------
</br>

### Optional: Spotipy

https://stackoverflow.com/questions/47028093/attributeerror-spotify-object-has-no-attribute-current-user-saved-tracks
</br>
</br>

- Error:    AttributeError: 'Spotify' object has no attribute 'devices'
</br>
- Solution: Replace the old client.py file 

       >>> new client.py file is in /miranda/support
       >>> destination linux_path: /usr/local/lib/python3.7/dist-packages/spotipy
       >>> sudo cp /home/pi/miranda/support/Spotipy/client.py /usr/local/lib/python3.7/dist-packages/spotipy/client.py

</br>
------------
</br>

### Optional: piCorePlayer & LMS (Logitech Media Server)

https://www.picoreplayer.org/
</br>
https://www.basecube.de/2018/03/17/download/
</br>
</br>

#### 1. General Settings piCorePlayer

change settings option to beta (options are at the bottom corner)
</br>

- main page

       >>> expand filesystem to 200mb
       >>> set a static ip-address

- wifi settings

       >>> activate wlan

</br>

#### 2. Settings piCorePlayer - Player

- squeezelite settings

       >>> IQaudIO DAC+ (X400)

- tweaks

       >>> activate squeezelite autostart


</br>

#### 3. Settings piCorePlayer - LMS 

- LMS

       >>> install LMS
       >>> start LMS


</br>

#### 4. LMS 

- LMS IP-address:

       >>> same as piCorePlayer, defaultport = 9000

- Logitech Account

       >>> not necessary, just skip it

- settings

       >>> plugins >>> install Spotty

- config spotty

       >>> add premium account 
       >>> activate player at spotify connect
       >>> the new player is now selectable in spotify

- synchronize player

       >>> set the player-groups on the main page in the upper-right corner 
           (Squeezelite must be installed on the clients)
       >>> synchronized groups appears as selectable devices in spotify


</br>

#### 5. Squeezelite - Client

- Windows 10

       >>> microsoft store >>> Squeezelite-X



