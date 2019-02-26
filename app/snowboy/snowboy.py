import snowboydecoder
import sys
import signal



interrupted = False

def signal_handler(signal, frame):
   global interrupted
   interrupted = True

def interrupt_callback():
   global interrupted
   return interrupted

#don't need this warning when calling pmdl programmatically:
#if len(sys.argv) == 1:
#    print("Error: need to specify model name")
#    print("Usage: python demo.py your.model")
#    sys.exit(-1)

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

#original line from kitt.ai/snowboy:
#model = sys.argv[1]
#Add custom voice models here:
models = ['/home/pi/Python/SmartHome/app/snowboy/resources/snowboy.umdl',
          '/home/pi/Python/SmartHome/app/snowboy/resources/smart_mirror.umdl',
          '/home/pi/Python/SmartHome/app/snowboy/resources/nordlichter.pmdl',
          '/home/pi/Python/SmartHome/app/snowboy/resources/mediterran.pmdl',
          '/home/pi/Python/SmartHome/app/snowboy/resources/hexenwerk.pmdl',
          '/home/pi/Python/SmartHome/app/snowboy/resources/entertainment.pmdl',
          '/home/pi/Python/SmartHome/app/snowboy/resources/relax.pmdl',
          '/home/pi/Python/SmartHome/app/snowboy/resources/default.pmdl']

#original line from kitt.ai/snowboy:
#detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
#use this so you don't need to specify voice model when calling this script
detector = snowboydecoder.HotwordDetector(models, sensitivity=0.7)

#put what should happen when snowboy detects hotword here:
callbacks = [lambda: print("HOTWORD_1"), lambda: print("HOTWORD_2"),
             lambda: print("HOTWORD_3"), lambda: print("HOTWORD_4"),
             lambda: print("HOTWORD_5"), lambda: print("HOTWORD_6"),
             lambda: print("HOTWORD_7"), lambda: print("HOTWORD_8")]
           
#without "lambda", callback will run immediately on startup, 
#and then after each hotword detection:
#callbacks = [os.system("/home/pi/test.sh")]

print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=callbacks,
           interrupt_check=interrupt_callback,
           sleep_time=0.03)

detector.terminate()
