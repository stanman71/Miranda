
from app import app
from app.components.file_management import WRITE_LOGFILE_SYSTEM

def MICROPHONE_LED_CONTROL(led_type, led_setting):


    """ ####################### """
    """ ReSpeaker 2-Mics Pi HAT """
    """ ####################### """

    """
    https://github.com/respeaker/mic_hat
    https://github.com/respeaker/mic_hat/blob/master/pixels.py

    """

    if led_type == "ReSpeaker 2-Mics Pi HAT":
        pass



    """ ####################################### """
    """ ReSpeaker Mic 4 Array v2.0 - Pixel Ring """
    """ ####################################### """

    """
    https://github.com/respeaker
    https://github.com/respeaker/pixel_ring/blob/master/pixel_ring/usb_pixel_ring_v2.py

    ----------
    IMPORTANT:
    ----------

    INSTALL: "sudo apt install python3-usb" 

    (https://forum.micropython.org/viewtopic.php?t=4849)

    """

    import usb.core
    import usb.util

    if led_type == "ReSpeaker Mic 4 Array v2.0":

        class PixelRing:
            TIMEOUT = 8000    
            
            def __init__(self, dev):
                self.dev = dev

            def trace(self):
                self.write(0)

            def mono(self, color):
                self.write(1, [(color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF, 0])
            
            def set_color(self, rgb=None, r=0, g=0, b=0):
                if rgb:
                    self.mono(rgb)
                else:
                    self.write(1, [r, g, b, 0])

            def off(self):
                self.mono(0)

            def listen(self, direction=None):
                self.write(2)

            wakeup = listen

            def speak(self):
                self.write(3)

            def think(self):
                self.write(4)

            wait = think

            def spin(self):
                self.write(5)

            def show(self, data):
                self.write(6, data)

            customize = show
                
            def set_brightness(self, brightness):
                self.write(0x20, [brightness])
            
            def set_color_palette(self, a, b):
                self.write(0x21, [(a >> 16) & 0xFF, (a >> 8) & 0xFF, a & 0xFF, 0, (b >> 16) & 0xFF, (b >> 8) & 0xFF, b & 0xFF, 0])

            def set_vad_led(self, state):
                self.write(0x22, [state])

            def set_volume(self, volume):
                self.write(0x23, [volume])

            def change_pattern(self, pattern):
                if pattern == 'echo':
                    self.write(0x24, [1])
                else:
                    self.write(0x24, [0])

            def write(self, cmd, data=[0]):
                self.dev.ctrl_transfer(
                    usb.util.CTRL_OUT | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE,
                    0, cmd, 0x1C, data, self.TIMEOUT)

            @property
            def version(self):
                return self.dev.ctrl_transfer(
                    usb.util.CTRL_IN | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE,
                    0, 0x80 | 0x40, 0x1C, 24, self.TIMEOUT).tostring()

            def close(self):
                usb.util.dispose_resources(self.dev)


        try:
            def find(vid=0x2886, pid=0x0018):
                dev = usb.core.find(idVendor=vid, idProduct=pid)
                if not dev:
                    return ("PixelRing nicht gefunden")

                return PixelRing(dev)    
            
            pixel_ring = find()
            
            if led_setting == "on":
                pixel_ring.wakeup()
            if led_setting == "off":
                pixel_ring.off()

        except Exception as e:
            WRITE_LOGFILE_SYSTEM("ERROR", "Microphone LED Control | " + str(e)) 