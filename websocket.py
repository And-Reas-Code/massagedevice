#!/usr/bin/env python

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import websockets

import RPi.GPIO as GPIO
import time
import random

# Inputs / Outputs
pin_button_on_off = 17
pin_button_lang = 18
pin_button_increase = 22
pin_button_decrease = 23
pin_button_mode = 24
pin_button_time = 27
pin_status = 10

# GPIO definitionen
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pin_button_on_off,GPIO.OUT)
GPIO.setup(pin_button_lang,GPIO.OUT)
GPIO.setup(pin_button_increase,GPIO.OUT)
GPIO.setup(pin_button_decrease,GPIO.OUT)
GPIO.setup(pin_button_mode,GPIO.OUT)
GPIO.setup(pin_button_time,GPIO.OUT)
GPIO.setup(pin_status,GPIO.IN,pull_up_down=GPIO.PUD_UP)

class MassageDevice:

    def bt_on_off(self):
        GPIO.output(pin_button_on_off,GPIO.HIGH)
        time.sleep(.2)
        GPIO.output(pin_button_on_off,GPIO.LOW)
        time.sleep(.2)

    def bt_lang(self):
        GPIO.output(pin_button_lang,GPIO.HIGH)
        time.sleep(.2)
        GPIO.output(pin_button_lang,GPIO.LOW)
        time.sleep(.2)

    def bt_increase(self):
        GPIO.output(pin_button_increase,GPIO.HIGH)
        time.sleep(.2)
        GPIO.output(pin_button_increase,GPIO.LOW)
        time.sleep(.2)

    def bt_decrease(self):
        GPIO.output(pin_button_decrease,GPIO.HIGH)
        time.sleep(.2)
        GPIO.output(pin_button_decrease,GPIO.LOW)
        time.sleep(.2)

    def bt_mode(self):
        GPIO.output(pin_button_mode,GPIO.HIGH)
        time.sleep(.2)
        GPIO.output(pin_button_mode,GPIO.LOW)
        time.sleep(.2)

    def bt_time(self):
        GPIO.output(pin_button_time,GPIO.HIGH)
        time.sleep(.2)
        GPIO.output(pin_button_time,GPIO.LOW)
        time.sleep(.2)

    def display_is_on(self):
        if GPIO.input(pin_status)==1:
            return False
        if GPIO.input(pin_status)==0:
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

#   def programmRandom(self):
#       # Immer zuerst abstellen, da dann das Device initialisiert ist!
#       rand_mode = random.randint(1,7)
#       rand_level = random.randint(self.min_level,self.max_level)
#       print("Mode: " + str(rand_mode) + "; Level: " + str(rand_level))
#       self.off()
#       self.on()
#       self.set_mode(rand_mode)
#       self.set_level(rand_level)
 
device = MassageDevice()

class MassageDeviceControl:

    def __init__(self):
        self.powerOn = False
        self.mode = 1
        self.liveMode = 1
        self.electricityLevel = 0
        self.electricityLiveLevel = 0
        self.time = 15
        self.min_level = 1
        self.max_level = 15

    def get_power_state(self):
        return self.powerOn

    def set_mode(self):
        if self.mode < 8:
            self.mode = self.mode + 1
        else:
            self.mode = self.mode = 1
        return self.mode

    def get_mode(self):
        return self.mode

    def set_live_mode(self,mode):
        self.liveMode = mode

    def get_live_mode(self):
        return self.liveMode

    def set_level_increase(self):
        self.electricityLevel = self.electricityLevel + 1
        if self.electricityLevel > 15:
            self.electricityLevel = 15

    def set_level_decrease(self):
        self.electricityLevel = self.electricityLevel - 1
        if self.electricityLevel < 0:
            self.electricityLevel = 0

    def get_level(self):
        return self.electricityLevel

    def set_live_level(self,level):
        self.electricityLiveLevel = level

    def get_live_level(self):
        return self.electricityLiveLevel

    def set_max_level(self,max_level_nr):
        if max_level_nr > 15:
            max_level_nr = 15
        if max_level_nr < self.min_level:
            max_level_nr = self.min_level
        self.max_level = max_level_nr

    def set_min_level(self,min_level_nr):
        if min_level_nr > self.max_level:
            min_level_nr = self.max_level
        if min_level_nr < 1:
            min_level_nr = 1
        self.min_level = min_level_nr

    def get_max_level(self):
        return self.max_level

    def get_min_level(self):
        return self.min_level

    def start(self):
        self.powerOn = True
        self.liveMode = self.mode
        self.electricityLiveLevel = self.electricityLevel
        self.time = 30

    def stop(self):
        self.powerOn = False
        self.electricityLiveLevel = 0
        self.liveMode = 1
        



deviceControl = MassageDeviceControl()


#device.set_max_level(3)
#device.set_min_level(2)

#device.programm(2,4)
#exit(0)

#start = 1
#stop = 7
#while start <= stop:
##    print("Programzyklus: " + str(start) + " von " + str(stop) + ":")
##    device.programmRandom()
##    time.sleep(15)
##    device.off()
##    time.sleep(5)
##    start = start + 1

#device.off()
#exit(0)

logging.basicConfig()

STATE ={"value": 0}

USERS = set()

def state_event():
    return json.dumps({"type": "state", **STATE})

def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})

def power_event():
    return json.dumps({"type": "power", "value": deviceControl.get_power_state()})

def level_event():
    return json.dumps({"type": "level", "value": deviceControl.get_level()})

def live_level_event():
    return json.dumps({"type": "live-level", "value": deviceControl.get_live_level()})

def randMin_event():
    return json.dumps({"type": "levelRandMin", "value": deviceControl.get_min_level()})

def randMax_event():
    return json.dumps({"type": "levelRandMax", "value": deviceControl.get_max_level()})

def mode_event():
    return json.dumps({"type": "mode", "value": deviceControl.get_mode()})

def live_mode_event():
    return json.dumps({"type": "live-mode", "value": deviceControl.get_live_mode()})



async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_power():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = power_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_level():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = level_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_live_level():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = live_level_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_randMin():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = randMin_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_randMax():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = randMax_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_mode():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = mode_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def notify_live_mode():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = live_mode_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.add(websocket)
    await notify_users()
    await notify_power()
    await notify_mode()
    await notify_live_mode()
    await notify_level()
    await notify_live_level()
    await notify_randMin()
    await notify_randMax()


async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)

            if data["action"] == "btnPowerOn":
                deviceControl.start()
                device.programm(deviceControl.get_mode(),deviceControl.get_level())
                await notify_live_level()
                await notify_live_mode()
                await notify_power()
            elif data["action"] == "btnPowerOff":
                deviceControl.stop()
                await notify_live_level()
                await notify_live_mode()
                await notify_power()

            elif data["action"] == "btnElectricityPlus":
                if deviceControl.get_power_state():
                    device.bt_increase()
                deviceControl.set_level_increase()
                await notify_live_level()
                await notify_level()
            elif data["action"] == "btnElectricityMinus":
                if deviceControl.get_power_state():
                    device.bt_decrease()
                deviceControl.set_level_decrease()
                await notify_live_level()
                await notify_level()

            elif data["action"] == "btnRandMinMinus":
                deviceControl.set_min_level(deviceControl.get_min_level() - 1)
                await notify_randMin()
            elif data["action"] == "btnRandMinPlus":
                deviceControl.set_min_level(deviceControl.get_min_level() + 1)
                await notify_randMin()

            elif data["action"] == "btnRandMaxMinus":
                deviceControl.set_max_level(deviceControl.get_max_level() - 1)
                await notify_randMax()
            elif data["action"] == "btnRandMaxPlus":
                deviceControl.set_max_level(deviceControl.get_max_level() + 1)
                await notify_randMax()

            elif data["action"] == "btnMode":
                deviceControl.set_mode()
                await notify_mode()
                await notify_live_mode()
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)


start_server = websockets.serve(counter, "192.168.1.133", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
