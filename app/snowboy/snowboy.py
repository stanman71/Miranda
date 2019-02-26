from app import app

from app.snowboy import snowboydetect
from app.snowboy import snowboydecoder
from app.components import led_control

import sys
import signal

interrupted = False

def signal_handler(signal, frame):
   global interrupted
   interrupted = True

def interrupt_callback():
   global interrupted
   return interrupted


def SNOWBOY_START():

     signal.signal(signal.SIGINT, signal_handler)

     # voice models here:
     models = ['/home/pi/Python/SmartHome/app/snowboy/resources/snowboy.umdl',
               '/home/pi/Python/SmartHome/app/snowboy/resources/smart_mirror.umdl',
               '/home/pi/Python/SmartHome/app/snowboy/resources/nordlichter.pmdl',
               '/home/pi/Python/SmartHome/app/snowboy/resources/mediterran.pmdl',
               '/home/pi/Python/SmartHome/app/snowboy/resources/hexenwerk.pmdl',
               '/home/pi/Python/SmartHome/app/snowboy/resources/entertainment.pmdl',
               '/home/pi/Python/SmartHome/app/snowboy/resources/relax.pmdl',
               '/home/pi/Python/SmartHome/app/snowboy/resources/default.pmdl']

     # modify sensitivity for better detection / accuracy
     detector = snowboydecoder.HotwordDetector(models, sensitivity=0.5)

     # put what should happen when snowboy detects hotword here:
     callbacks = [lambda: print("HOTWORD_1"), 
                  lambda: print("HOTWORD_2"),
                  lambda: led_control.LED_SET_SCENE(6),  
                  lambda: led_control.LED_SET_SCENE(7),
                  lambda: led_control.LED_SET_SCENE(8),  
                  lambda: led_control.LED_SET_SCENE(9),
                  lambda: led_control.LED_SET_SCENE(10), 
                  lambda: led_control.LED_SET_SCENE(99)]
                
     #without "lambda", callback will run immediately on startup, 
     #and then after each hotword detection:
     #callbacks = [os.system("/home/pi/test.sh")]

     print('Listening...')

     # main loop
     detector.start(detected_callback=callbacks,
                    interrupt_check=interrupt_callback,
                    sleep_time=0.03)

     detector.terminate()

