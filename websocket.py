#!/usr/bin/env python3

# Verion 06 Massagedevice
#       - Shell-Script start.sh
#       - Bugfixes

# Verion 05 Massagedevice
# Funktionen: GUI Okay, inkl. Random-Mode
#       - Strat / Stop Device
#       - Level einstellen
#       - Mode einstellen
#       - Random-Mode mit mehreren Iterationen
#       - Random Duration einstellbar
#       - Randem Max / Min Level einstellbar

import asyncio
import json
import logging
import websockets

import RPi.GPIO as GPIO
import time
import random
import threading

from http.server import HTTPServer, CGIHTTPRequestHandler
import os
import socketserver

import abc

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


class ProgrammTask:
    def __init__(self, deviceControl, device):
        self._running = True
        self.device = device
        self.deviceControl = deviceControl

    def terminate(self): 
        self._running = False
      
    def run(self):
        print("Start Thread ...")
        i = 1 
        while self._running and i <= self.deviceControl.repetition:
            self.deviceControl.startProgrammRandom()
            self.deviceControl.liveMode = self.deviceControl.rand_mode
            self.deviceControl.electricityLiveLevel = self.deviceControl.rand_level
            self.deviceControl.electricityLevel = self.deviceControl.electricityLiveLevel
            self.deviceControl.subject_state("FIRE")
            time.sleep(self.deviceControl.duration)
            self.device.off() ##########
            i += 1
            time.sleep(self.deviceControl.pause)
        print("End Thread ...")


class MassageDeviceControl:

    def __init__(self, device):
        self.device = device
        self.powerOn = False
        self.mode = 1
        self.liveMode = 1
        self.electricityLevel = 0
        self.electricityLiveLevel = 0
        self.time = 15
        self.min_level = 1
        self.max_level = 15
        self.rand_mode = 1
        self.rand_level = 0
        self.programTask = 0
        self.thread = 0 
        self.repetition = 1
        self.duration = 10
        self.pause = 10
        # Subject vars:
        self._observers = set()
        self._subject_state = None

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
        if self.powerOn == True:
            self.device.bt_increase() ##########
        self.electricityLevel = self.electricityLevel + 1
        if self.electricityLevel > 15:
            self.electricityLevel = 15
        if self.powerOn == True:
            self.set_live_level(self.electricityLevel)

    def set_level_decrease(self):
        if self.powerOn == True:
            self.device.bt_decrease() ##########
        self.electricityLevel = self.electricityLevel - 1
        if self.electricityLevel < 0:
            self.electricityLevel = 0
        if self.powerOn == True:
            self.set_live_level(self.electricityLevel)

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

    def set_repetition_increase(self):
        self.repetition = self.repetition + 1
        if self.repetition > 20:
            self.repetition = 20

    def set_repetition_decrease(self):
        self.repetition = self.repetition - 1
        if self.repetition < 1:
            self.repetition = 1

    def get_repetition(self):
        return self.repetition

    def set_duration_increase(self):
        self.duration = self.duration + 10
        if self.duration > 120:
            self.duration = 120

    def set_duration_decrease(self):
        self.duration = self.duration - 10
        if self.duration < 10:
            self.duration = 10

    def get_duration(self):
        return self.duration

    def start(self):
        self.powerOn = True
        if self.mode == 8:
            #self.thread = threading.Thread(target=self.thread_function)
            self.programTask = ProgrammTask(self, self.device)
            self.thread = threading.Thread(target=self.programTask.run)
            self.thread.start()
            #self.startProgrammRandom()
            #self.liveMode = self.rand_mode
            #self.electricityLiveLevel = self.rand_level
            #self.electricityLevel = self.electricityLiveLevel
        else:
            self.startProgramm()
            self.liveMode = self.mode 
            self.electricityLiveLevel = self.electricityLevel

    def stop(self):
        if self.mode == 8:
            self.programTask.terminate()
            self.device.off() ##########
            self.powerOn = False
            self.electricityLiveLevel = 0
            self.liveMode = 1
        else:
            self.device.off() ##########
            self.powerOn = False
            self.electricityLiveLevel = 0
            self.liveMode = 1
        
    def startProgramm(self):
        self.programm(self.mode,self.electricityLevel)

    def programm(self,mode,level):
        print("Mode: " + str(mode) + "; Level: " + str(level))
        self.device.programm(mode,level) ##########

    def startProgrammRandom(self):
        self.rand_mode = random.randint(1,7)
        self.rand_level = random.randint(self.min_level,self.max_level)
        self.programm(self.rand_mode,self.rand_level)
    
    """
    Know its observers. Any number of Observer objects may observe a
    subject.
    Send a notification to its observers when its state changes.
    """
    def attach(self, observer):
        observer._subject = self
        self._observers.add(observer)

    def detach(self, observer):
        observer._subject = None
        self._observers.discard(observer)

    def _notify(self):
        for observer in self._observers:
            observer.update(self._subject_state)

    @property
    def subject_state(self):
        return self._subject_state

    @subject_state.setter
    def subject_state(self, arg):
        self._subject_state = arg
        self._notify()

#logging.basicConfig()

class Observer(metaclass=abc.ABCMeta):
    """
    Define an updating interface for objects that should be notified of
    changes in a subject.
    """

    def __init__(self):
        self._subject = None
        self._observer_state = None

    @abc.abstractmethod
    def update(self, arg):
        pass

class WsWebsocket(Observer):

    def __init__(self, deviceControl):
        self.deviceControl = deviceControl
        self.STATE ={"value": 0}
        self.USERS = set()

    def update(self, arg):
        self._observer_state = arg
        print("Observer infomiert, message: " + str(arg))
        #await self.notify_live_level()
        #await self.notify_live_mode()
        #await self.notify_level()

    def state_event(self):
        return json.dumps({"type": "state", **self.STATE})

    def users_event(self):
        return json.dumps({"type": "users", "count": len(self.USERS)})

    def power_event(self):
        return json.dumps({"type": "power", "value": self.deviceControl.get_power_state()})

    def level_event(self):
        return json.dumps({"type": "level", "value": self.deviceControl.get_level()})

    def live_level_event(self):
        return json.dumps({"type": "live-level", "value": self.deviceControl.get_live_level()})

    def randMin_event(self):
        return json.dumps({"type": "levelRandMin", "value": self.deviceControl.get_min_level()})

    def randMax_event(self):
        return json.dumps({"type": "levelRandMax", "value": self.deviceControl.get_max_level()})

    def mode_event(self):
        return json.dumps({"type": "mode", "value": self.deviceControl.get_mode()})

    def live_mode_event(self):
        return json.dumps({"type": "live-mode", "value": self.deviceControl.get_live_mode()})

    def repetition_event(self):
        return json.dumps({"type": "labRepetition", "value": self.deviceControl.get_repetition()})

    def duration_event(self):
        return json.dumps({"type": "labRepDur", "value": self.deviceControl.get_duration()})

    async def notify_state(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.state_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify_users(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.users_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify_power(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.power_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify_level(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.level_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify_live_level(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.live_level_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify_randMin(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.randMin_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify_randMax(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.randMax_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify_mode(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.mode_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify_live_mode(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.live_mode_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify_repetition(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.repetition_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify_duration(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.duration_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def register(self, websocket):
        self.USERS.add(websocket)
        await self.notify_users()
        await self.notify_power()
        await self.notify_mode()
        await self.notify_live_mode()
        await self.notify_level()
        await self.notify_live_level()
        await self.notify_randMin()
        await self.notify_randMax()
        await self.notify_repetition()
        await self.notify_duration()

    async def unregister(self, websocket):
        self.USERS.remove(websocket)
        await self.notify_users()

    async def counter(self, websocket, path):
        # register(websocket) sends user_event() to websocket
        await self.register(websocket)
        try:
            await websocket.send(self.state_event())
            async for message in websocket:
                data = json.loads(message)

                if data["action"] == "btnPowerOn":
                    self.deviceControl.start()
                    await self.notify_live_level()
                    await self.notify_live_mode()
                    await self.notify_level()
                    await self.notify_power()
                elif data["action"] == "btnPowerOff":
                    self.deviceControl.stop()
                    await self.notify_live_level()
                    await self.notify_live_mode()
                    await self.notify_power()

                elif data["action"] == "btnElectricityPlus":
                    self.deviceControl.set_level_increase()
                    await self.notify_live_mode()
                    await self.notify_live_level()
                    await self.notify_level()
                elif data["action"] == "btnElectricityMinus":
                    self.deviceControl.set_level_decrease()
                    await self.notify_live_mode()
                    await self.notify_live_level()
                    await self.notify_level()

                elif data["action"] == "btnRandMinMinus":
                    self.deviceControl.set_min_level(self.deviceControl.get_min_level() - 1)
                    await self.notify_randMin()
                elif data["action"] == "btnRandMinPlus":
                    self.deviceControl.set_min_level(self.deviceControl.get_min_level() + 1)
                    await self.notify_randMin()

                elif data["action"] == "btnRandMaxMinus":
                    self.deviceControl.set_max_level(self.deviceControl.get_max_level() - 1)
                    await self.notify_randMax()
                elif data["action"] == "btnRandMaxPlus":
                    self.deviceControl.set_max_level(self.deviceControl.get_max_level() + 1)
                    await self.notify_randMax()

                elif data["action"] == "btnMode":
                    self.deviceControl.set_mode()
                    await self.notify_mode()

                elif data["action"] == "btnRepetitionPlus":
                    self.deviceControl.set_repetition_increase()
                    await self.notify_repetition()
                elif data["action"] == "btnRepetitionMinus":
                    self.deviceControl.set_repetition_decrease()
                    await self.notify_repetition()
                elif data["action"] == "btnRepDurPlus":
                    self.deviceControl.set_duration_increase()
                    await self.notify_duration()
                elif data["action"] == "btnRepDurMinus":
                    self.deviceControl.set_duration_decrease()
                    await self.notify_duration()

                else:
                    #logging.error("unsupported event: {}", data)
                    print("unsupported event: {}", data)
        finally:
            await self.unregister(websocket)


class HttpServerWorker:
    def run(self):
        '''Start a simple webserver serving path on port'''
        print("Start HttpServer ...")
        os.chdir('./wwwroot/')
        httpd = HTTPServer(('', 80), CGIHTTPRequestHandler)
        httpd.serve_forever()
        print("End HttpServer ...")


def main():
    # Start the server in a new thread
    httpServerWorker = HttpServerWorker()
    httpThread = threading.Thread(target=httpServerWorker.run)
    httpThread.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
    httpThread.start()

    device = MassageDevice()
    deviceControl = MassageDeviceControl(device)
    wsWebsocket = WsWebsocket(deviceControl)
    deviceControl.attach(wsWebsocket) # Observer verbinden

    print("Starte Websocket ...")
    start_server = websockets.serve(wsWebsocket.counter, "", 6789)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()
