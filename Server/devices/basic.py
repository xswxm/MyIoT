#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading
import RPi.GPIO as GPIO

class BasicButton:
    def __init__(self, id, title, port, accessible = True):
        self.id = id
        self.title = title
        self.port = port
        self.accessible = accessible
        self.category = 'Button'
        GPIO.setup(self.port, GPIO.OUT)
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['category'] = self.category
        message['value'] = self.getValue()
        message['accessible'] = self.accessible
        return message
    def getValue(self):
        if (GPIO.input(self.port) == 1):
            return True
        else:
            return False
    def setValue(self, value):
        GPIO.output(self.port, value)
        return value

class BasicSwitch:
    def __init__(self, id, title, port, accessible = True):
        self.id = id
        self.title = title
        self.port = port
        self.accessible = accessible
        self.category = 'Switch'
        GPIO.setup(self.port, GPIO.OUT)
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['category'] = self.category
        message['value'] = self.getValue()
        message['accessible'] = self.accessible
        return message
    def getValue(self):
        if (GPIO.input(self.port) == 1):
            return True
        else:
            return False
    def setValue(self, value):
        GPIO.output(self.port, value)
        return value

class PWMSignal(threading.Thread):
    _lock = threading.RLock()
    def __init__(self, id, title, port, accessible = True):
        self._stopevent = threading.Event()
        self._sleepperiod = 0.05
        threading.Thread.__init__(self)
        self.id = id
        self.title = title
        self.port = port
        self.value = 0
        self.accessible = accessible
        self.category = 'SeekBar'
    def run(self):
        GPIO.setup(self.port, GPIO.OUT)
        pwm = GPIO.PWM(self.port, 80)
        pwm.start(0)
        pwm_rate_curr = 0
        pwm_rate_new = int(self.value)
        while not self._stopevent.isSet():
            pwm_rate_new = int(self.value)
            if (pwm_rate_curr != pwm_rate_new):
                if (pwm_rate_curr > pwm_rate_new):
                    for i in xrange(pwm_rate_curr, pwm_rate_new, -1):
                        pwm.ChangeDutyCycle(i)
                        self._stopevent.wait(0.01)
                else:
                    for i in xrange(pwm_rate_curr, pwm_rate_new, 1):
                        pwm.ChangeDutyCycle(i)
                        self._stopevent.wait(0.01)
                pwm_rate_curr = pwm_rate_new
            pwm.ChangeDutyCycle(i)
            self._stopevent.wait(self._sleepperiod)
    def join(self, timeout = None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['category'] = self.category
        message['value'] = self.getValue()
        message['accessible'] = self.accessible
        return message
    def getValue(self):
        return str(int(self.value)) + " %"
    def setValue(self, value):
        with PWMSignal._lock:
            if (value == 0):
                if (self.value == 0):
                    return str(int(self.value)) + " %"
                else:
                    self.value = float(value)
                    self.join()
            else:
                self.value = float(value)
                if (not self.isAlive()):
                    self.start()
                    self.title = self.title
            return str(int(self.value)) + " %"

class SOSLight(threading.Thread):
    _lock = threading.RLock()
    def __init__(self, id, title, port, accessible = True):
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        self.id = id
        self.title = title
        self.port = port
        self.accessible = accessible
        self.category = 'Switch'
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
        message['category'] = self.category
        message['value'] = self.isAlive()
        message['accessible'] = self.accessible
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
    def __init__(self, id, title, port, accessible = True):
        self._stopevent = threading.Event()
        self._sleepperiod = 0.05
        threading.Thread.__init__(self)
        self.id = id
        self.title = title
        self.port = port
        self.accessible = accessible
        self.category = 'Switch'
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
        message['category'] = self.category
        message['value'] = self.isAlive()
        message['accessible'] = self.accessible
        return message
    def setValue(self, value):
        with BreathLight._lock:
            if (value):
                self.start()
                self.title = self.title
            else:
                self.join()
        return value
