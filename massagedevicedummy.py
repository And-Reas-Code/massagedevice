import time
#import RPi.GPIO as GPIO
#
## Inputs / Outputs
#pin_button_on_off = 17
#pin_button_lang = 18
#pin_button_increase = 22
#pin_button_decrease = 23
#pin_button_mode = 24
#pin_button_time = 27
#pin_status = 10
#
## GPIO definitionen
#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
#GPIO.setup(pin_button_on_off,GPIO.OUT)
#GPIO.setup(pin_button_lang,GPIO.OUT)
#GPIO.setup(pin_button_increase,GPIO.OUT)
#GPIO.setup(pin_button_decrease,GPIO.OUT)
#GPIO.setup(pin_button_mode,GPIO.OUT)
#GPIO.setup(pin_button_time,GPIO.OUT)
#GPIO.setup(pin_status,GPIO.IN,pull_up_down=GPIO.PUD_UP)

class MassageDevice():
    def bt_on_off(self):
    #    GPIO.output(pin_button_on_off,GPIO.HIGH)
        time.sleep(.2)
    #    GPIO.output(pin_button_on_off,GPIO.LOW)
        time.sleep(.2)
    def bt_lang(self):
    #    GPIO.output(pin_button_lang,GPIO.HIGH)
        time.sleep(.2)
    #    GPIO.output(pin_button_lang,GPIO.LOW)
        time.sleep(.2)
    def bt_increase(self):
    #    GPIO.output(pin_button_increase,GPIO.HIGH)
        time.sleep(.2)
    #    GPIO.output(pin_button_increase,GPIO.LOW)
        time.sleep(.2)
    def bt_decrease(self):
    #    GPIO.output(pin_button_decrease,GPIO.HIGH)
        time.sleep(.2)
    #    GPIO.output(pin_button_decrease,GPIO.LOW)
        time.sleep(.2)
    def bt_mode(self):
    #    GPIO.output(pin_button_mode,GPIO.HIGH)
        time.sleep(.2)
    #    GPIO.output(pin_button_mode,GPIO.LOW)
        time.sleep(.2)
    def bt_time(self):
    #    GPIO.output(pin_button_time,GPIO.HIGH)
        time.sleep(.2)
    #    GPIO.output(pin_button_time,GPIO.LOW)
        time.sleep(.2)
    def display_is_on(self):
    #    if GPIO.input(pin_status)==1:
    #        return False
    #    if GPIO.input(pin_status)==0:
    #        return True
        return True
    def on(self):
        self.bt_lang()
        if not self.display_is_on():
            self.bt_on_off()
            for x in range(3):
                self.bt_time()
    def off(self):
        self.bt_lang()
        if self.display_is_on():
            self.bt_on_off()
    def set_mode(self, mode_nr):
        for x in range(mode_nr - 1):
            self.bt_mode()
    def set_level(self, level_nr):
        if level_nr >= 15:
            level_nr = 15
        if level_nr < 0:
            level_nr = 0
        for x in range(level_nr):
            self.bt_increase()
            time.sleep(.3)
    def programm(self,mode,level):
        # Immer zuerst abstellen, da dann das Device initialisiert ist!
        self.off()
        self.on()
        self.set_mode(mode)
        self.set_level(level)
    