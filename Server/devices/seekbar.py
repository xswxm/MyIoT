#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading
import RPi.GPIO as GPIO

class PWMSignal(threading.Thread):
    _lock = threading.RLock()
    def __init__(self, title, port, id = 1000):
        self._stopevent = threading.Event()
        self._sleepperiod = 0.05
        threading.Thread.__init__(self)
        self.id = id
        self.title = title
        self.port = port
        self.pwm_rate = 0
        self.type = 'SeekBar'
        self.cname = 'PWMSignal'
        self.isThread = True
    def run(self):
        GPIO.setup(self.port, GPIO.OUT)
        pwm = GPIO.PWM(self.port, 80)
        pwm.start(0)
        pwm_rate_curr = 0
        pwm_rate_new = int(self.pwm_rate)
        while not self._stopevent.isSet():
            pwm_rate_new = int(self.pwm_rate)
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
        message['type'] = self.type
        message['value'] = self.getValue()
        return message
    def getValue(self):
        return str(int(self.pwm_rate)) + " %"
    def setValue(self, value):
        with PWMSignal._lock:
            if (value == 0):
                if (self.pwm_rate == 0):
                    return str(int(self.pwm_rate)) + " %"
                else:
                    self.pwm_rate = float(value)
                    self.join()
            else:
                self.pwm_rate = float(value)
                if (not self.isAlive()):
                    self.start()
                    self.title = self.title
            return str(int(self.pwm_rate)) + " %"
