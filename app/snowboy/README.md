## Snowboy setup on Raspberry Pi 3

https://github.com/Kitt-AI/snowboy
</br>
https://github.com/wanleg/snowboyPi 
</br>
https://snowboy.kitt.ai
</br>
http://docs.kitt.ai/snowboy/
</br>

### 1. Installation:

- Start with a fresh install of Raspbian (Lite or Regular, this guide assumes Lite)

       >> sudo apt update && sudo apt -y upgrade && sudo apt-get -y auto-remove && sudo reboot

- Install dependencies:

       >> sudo apt -y install python-pyaudio python3-pyaudio sox python3-pip python-pip libatlas-base-dev

</br>

#### ERROR: Command 'arm-linux-gnueabihf-gcc' failed with exit status 1

- install portaudio first (https://github.com/jgarff/rpi_ws281x/issues/294)

       >>  sudo apt-get install portaudio19-dev

</br>

--------------
--------------

</br>

### 2. Sound settings:

- create ".asoundrc" in your home folder with correct hw settings (see example file in https://github.com/wanleg/snowboyPi)
- "aplay -l" & "arecord -l" to find out hw cards (e.g "card 0, device 0" is "hw:0,0")
- "speaker-test -c 2" to test audio out
- "arecord -d 3 test.wav" to record a 3 second test clip 
- "aplay test.wav" to verify

</br>

--------------
--------------

</br>

### 3. Snowboy:

- extract the pre-packaged Snowboy binaries (https://github.com/Kitt-AI/snowboy) and rename directory to "snowboy"
- copy the files of the raspi-version (https://github.com/wanleg/snowboyPi) in the same folder
- go into the "snowboy" folder
- change the path settings of the resources folder in "snowboy.py"
- start "python3 snowboy.py"
- default hotwords are >> snowboy << and >> smart mirror << 

</br>

#### ERROR: ImportError: dynamic module does not define module export function (PyInit__snowboydetect)

- create snowboydetect again (https://github.com/Kitt-AI/snowboy)
- install swig (https://github.com/Yadoms/yadoms/wiki/Build-on-RaspberryPI)

       >> wget http://prdownloads.sourceforge.net/swig/swig-3.0.12.tar.gz
       >> tar xzf swig-3.0.12.tar.gz
       >> cd swig-3.0.12
       >> ./configure
       >> make
       >> sudo make install

- copy the python3 swig files into "snowboy/swig"
- go into the "swig" folder and start "make" in console 
- replace the old files of the parent dictionary

</br>

#### ERROR: ALSA lib confmisc.c:1281:(snd_func_refer) Unable to find definition 'cards.bcm2835_alsa.pcm.front.0:CARD=0'

- if you got many ALBA errors reinstall raspian

</br>

--------------
--------------

</br>

### 4. Create Snowboy hotwords

- log into https://snowboy.kitt.ai
- create a new hotword 
- copy the downloaded file into the folder ~/resources/ on your raspberry pi
- add the new hotword and action in "snowboy.py"
- run  "snowboy.py" and test the new hotword

</br>

--------------
--------------

</br>

### 5. Autostart Snowboy:

- copy "snowboy.service" to "/lib/systemd/system/"
- you may need to run this:

       >> sudo systemctl daemon-reload 

- start the "snowboy.service" to make sure everything is working:

       >> sudo systemctl start snowboy.service
