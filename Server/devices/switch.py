#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading
import RPi.GPIO as GPIO

class Switch:
    _lock = threading.RLock()
    def __init__(self, title, port, id = 1000):
        self.id = id
        self.title = title
        self.port = port
        self.type = 'Switch'
        self.isThread = False
        GPIO.setup(self.port, GPIO.OUT)
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['type'] = self.type
        if (GPIO.input(self.port) == '1'):
            message['value'] = True
        else:
            message['value'] = False
        return message
    def setValue(self, value):
        with Switch._lock:
            GPIO.output(self.port, value)
        return value

class SOSLight(threading.Thread):
    _lock = threading.RLock()
    def __init__(self, title, port, id = 1000):
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        self.id = id
        self.title = title
        self.port = port
        self.type = 'Switch'
        self.cname = 'SOSLight'
        self.isThread = True
    def run(self):
        GPIO.setup(self.port, GPIO.OUT)
        while not self._stopevent.isSet():
            for i in range(3):
                GPIO.output(self.port, GPIO.HIGH)
                self._stopevent.wait(0.5)
                GPIO.output(self.port, GPIO.LOW)
                self._stopevent.wait(0.2)
            self._stopevent.wait(0.4)
            for i in range(3):
                GPIO.output(self.port, GPIO.HIGH)
                self._stopevent.wait(1.0)
                GPIO.output(self.port, GPIO.LOW)
                self._stopevent.wait(0.4)
            self._stopevent.wait(0.2)
            for i in range(3):
                GPIO.output(self.port, GPIO.HIGH)
                self._stopevent.wait(0.5)
                GPIO.output(self.port, GPIO.LOW)
                self._stopevent.wait(0.2)
            self._stopevent.wait(0.8)
    def join(self, timeout = None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['type'] = self.type
        message['value'] = self.isAlive()
        return message
    def setValue(self, value):
        with SOSLight._lock:
            if (value):
                self.start()
                self.title = self.title
            else:
                self.join()
        return value

class BreathLight(threading.Thread):
    _lock = threading.RLock()
    def __init__(self, title, port, id = 1000):
        self._stopevent = threading.Event()
        self._sleepperiod = 0.05
        threading.Thread.__init__(self)
        self.id = id
        self.title = title
        self.port = port
        self.type = 'Switch'
        self.cname = 'BreathLight'
        self.isThread = True
    def run(self):
        GPIO.setup(self.port, GPIO.OUT)
        pwm = GPIO.PWM(self.port, 80)
        pwm.start(0)
        # change variables as neceaasry
        while not self._stopevent.isSet():
            for i in xrange(0, 100, 1):
                pwm.ChangeDutyCycle(i)
                self._stopevent.wait(self._sleepperiod)
            self._stopevent.wait(0.30)
            for i in xrange(99, -1, -1):
                pwm.ChangeDutyCycle(i)
                self._stopevent.wait(self._sleepperiod)
            self._stopevent.wait(0.20)
    def join(self, timeout = None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['type'] = self.type
        message['value'] = self.isAlive()
        return message
    def setValue(self, value):
        with BreathLight._lock:
            if (value):
                self.start()
                self.title = self.title
            else:
                self.join()
        return value
