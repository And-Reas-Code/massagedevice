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

    def __init__(self):
        self.powerOn = False
        self.electricityLevel = 0
        self.max_level = 15
        self.min_level = 1
        self.mode = 1
        self.time = 15

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

    def get_power_state(self):
        return self.powerOn

    def get_level(self):
        return self.electricityLevel

    def get_mode(self):
        return self.mode

    def get_max_level(self):
        return self.max_level

    def get_min_level(self):
        return self.min_level

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
        self.electricityLevel = self.electricityLevel + 1
        if self.electricityLevel > 15:
            self.electricityLevel = 15

    def bt_decrease(self):
        GPIO.output(pin_button_decrease,GPIO.HIGH)
        time.sleep(.2)
        GPIO.output(pin_button_decrease,GPIO.LOW)
        time.sleep(.2)
        self.electricityLevel = self.electricityLevel - 1
        if self.electricityLevel < 0:
            self.electricityLevel = 0

    def bt_mode(self):
        GPIO.output(pin_button_mode,GPIO.HIGH)
        time.sleep(.2)
        GPIO.output(pin_button_mode,GPIO.LOW)
        time.sleep(.2)
        self.mode = self.mode + 1
        if self.mode > 7:
            self.mode = 1
        self.electricityLevel = 0

    def bt_time(self):
        GPIO.output(pin_button_time,GPIO.HIGH)
        time.sleep(.2)
        GPIO.output(pin_button_time,GPIO.LOW)
        time.sleep(.2)
        self.time = self.time + 5
        if self.time > 30:
            self.time = 0

    def display_is_on(self):
        if GPIO.input(pin_status)==1:
            return False
        if GPIO.input(pin_status)==0:
            return True
        return powerOn

    def on(self):
        self.bt_lang()
        if not self.display_is_on():
            self.bt_on_off()
            for x in range(3):
                self.bt_time()
        self.powerOn = True

    def off(self):
        self.bt_lang()
        if self.display_is_on():
            self.bt_on_off()
        self.powerOn = False
        self.electricityLevel = 0
        self.mode = 1
        self.time = 15

    def set_mode(self, mode_nr):
        self.electricityLevel = 0
        for x in range(mode_nr - 1):
            self.bt_mode()

    def set_mode2(self, mode_nr):
        self.off()
        self.on()
        self.set_mode(mode_nr)

    def set_level(self, level_nr):
        if level_nr > self.max_level:
            level_nr = self.max_level
        if level_nr < self.min_level:
            level_nr = self.min_level
        for x in range(level_nr):
            self.bt_increase()
            time.sleep(.3)

    def programm(self,mode,level):
        # Immer zuerst abstellen, da dann das Device initialisiert ist!
        self.off()
        self.on()
        self.set_mode(mode)
        self.set_level(level)

    def programmRandom(self):
        # Immer zuerst abstellen, da dann das Device initialisiert ist!
        rand_mode = random.randint(1,7)
        rand_level = random.randint(self.min_level,self.max_level)
        print("Mode: " + str(rand_mode) + "; Level: " + str(rand_level))
        self.off()
        self.on()
        self.set_mode(rand_mode)
        self.set_level(rand_level)


device = MassageDevice()
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
    return json.dumps({"type": "power", "value": device.get_power_state()})

def level_event():
    return json.dumps({"type": "level", "value": device.get_level()})

def randMin_event():
    return json.dumps({"type": "levelRandMin", "value": device.get_min_level()})

def randMax_event():
    return json.dumps({"type": "levelRandMax", "value": device.get_max_level()})

def mode_event():
    return json.dumps({"type": "mode", "value": device.get_mode()})


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


async def register(websocket):
    USERS.add(websocket)
    await notify_users()
    await notify_power()
    await notify_level()
    await notify_randMin()
    await notify_randMax()
    await notify_mode()


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
                device.on()
                await notify_power()
            elif data["action"] == "btnPowerOff":
                device.off()
                await notify_level()
                await notify_mode()
                await notify_power()

            elif data["action"] == "btnElectricityPlus":
                device.bt_increase()
                await notify_level()
            elif data["action"] == "btnElectricityMinus":
                device.bt_decrease()
                await notify_level()

            elif data["action"] == "btnRandMinMinus":
                device.set_min_level(device.get_min_level() - 1)
                await notify_randMin()
            elif data["action"] == "btnRandMinPlus":
                device.set_min_level(device.get_min_level() + 1)
                await notify_randMin()

            elif data["action"] == "btnRandMaxMinus":
                device.set_max_level(device.get_max_level() - 1)
                await notify_randMax()
            elif data["action"] == "btnRandMaxPlus":
                device.set_max_level(device.get_max_level() + 1)
                await notify_randMax()

            elif data["action"] == "btnMode":
                device.bt_mode()
                await notify_mode()
                await notify_level()

            elif data["action"] == "selectModeDep":
                mode = int(data["value"])
                print("MODE: " + str(mode))
                if not mode == 8:
                    device.set_mode2(mode)
                else:
                    print("Random ...")
                await notify_level()
                await notify_power()
                await notify_mode()
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)


start_server = websockets.serve(counter, "192.168.1.133", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
