## snowboy setup on raspberry pi 
https://github.com/Kitt-AI/snowboy
</br>
https://github.com/wanleg/snowboyPi 
</br>
https://snowboy.kitt.ai
</br>

### 1. Installation:

- Start with a fresh install of Raspbian (Lite or Regular, this guide assumes Lite)

       >> sudo apt update && sudo apt -y upgrade && sudo apt-get -y auto-remove && sudo reboot

- Install dependencies:

       >> sudo apt -y install python-pyaudio python3-pyaudio sox python3-pip python-pip libatlas-base-dev
       >> sudo apt-get install portaudio19-dev (if an error occurs during the installation of pyaudio)

</br>

--------------
--------------

</br>

### 2. Sound settings:

- create ".asoundrc" in your home folder with correct hw settings (see example file in the folder support)
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
- start "python3 snowboy.py"
- default hotword is >> snowboy <<

</br>

#### ERROR: ImportError: dynamic module does not define module export function (PyInit__snowboydetect)

- create snowboydetect again (https://github.com/Yadoms/yadoms/wiki/Build-on-RaspberryPI)
- install swig

       >> wget http://prdownloads.sourceforge.net/swig/swig-3.0.12.tar.gz
       >> tar xzf swig-3.0.12.tar.gz
       >> cd swig-3.0.12
       >> ./configure
       >> make
       >> sudo make install

- copy the python3 swig files from "snowboy/support/swig" into "snowboy/swig"
- start "make" in console 
- replace the old files of the parent dictionary

</br>

#### Error: ALSA lib confmisc.c:1281:(snd_func_refer) Unable to find definition 'cards.bcm2835_alsa.pcm.front.0:CARD=0'

- if you got many ALBA errors reinstall raspian

--------------
--------------

</br>

### 4. Create Snowboy hotwords

- log into https://snowboy.kitt.ai
- click on “Profile settings”, and copy your API token
- change the appropriate fields (token, hotword, etc.) in "training_service.py"
- use the following to record 3 wav files of your hotword to the same directory:

       >> rec -r 16000 -c 1 -b 16 -e signed-integer FILENAME.wav
          (aboard recording manually)

- go to the SnowBoy dictionary and run the following to generate a pmdl:

       >> python3 training_service.py 1.wav 2.wav 3.wav saved_model.pmdl

- move "saved_model.pmdl" to ~/resources/ (rename for easier recall later)
- run the demo to make sure everything is working:

       >> python3 demo.py ~/snowboy/resources/saved_model.pmdl

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
