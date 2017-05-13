#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading
import pigpio

class PWMSignal(threading.Thread):
    _lock = threading.RLock()
    def __init__(self, id, title, port, feasible = True):
        self._stopevent = threading.Event()
        self._sleepperiod = 0.05
        threading.Thread.__init__(self)
        self.id = id
        self.title = title
        self.port = port
        self.pi = pigpio.pi()
        self.pi.set_PWM_frequency(self.port, 50)  # frequency 50Hz
        self.pi.set_PWM_range(self.port, 100)    # set range 100
        # Read current value of this port
        self.value = self.pi.get_PWM_dutycycle(self.port)
        self.feasible = feasible
        self.category = 'SeekBar'
    def run(self):
        pwm_rate_curr = self.pi.get_PWM_dutycycle(self.port)
        pwm_rate_new = self.value
        while not self._stopevent.isSet():
            pwm_rate_new = int(self.value)
            if (pwm_rate_curr != pwm_rate_new):
                if (pwm_rate_curr > pwm_rate_new):
                    # Set the total waiting period to 0.168 second
                    waitperiod = 0.168 / (pwm_rate_curr - pwm_rate_new)
                    for i in xrange(pwm_rate_curr, pwm_rate_new, -1):
                        self.pi.set_PWM_dutycycle(self.port, i)
                        self._stopevent.wait(waitperiod)
                else:
                    waitperiod = 0.168 / (pwm_rate_new - pwm_rate_curr)
                    for i in xrange(pwm_rate_curr, pwm_rate_new, 1):
                        self.pi.set_PWM_dutycycle(self.port, i)
                        self._stopevent.wait(waitperiod)
                pwm_rate_curr = pwm_rate_new
            self.pi.set_PWM_dutycycle(self.port, pwm_rate_curr)
            self._stopevent.wait(self._sleepperiod)
    def join(self, timeout = None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['port'] = self.port
        message['category'] = self.category
        message['value'] = self.getValue()
        message['feasible'] = self.feasible
        return message
    def getValue(self):
        return str(self.value) + " %"
    def setValue(self, value):
        with PWMSignal._lock:
            self.value = value
            if not self.isAlive():
                self.start()
                self.title = self.title
            return str(self.value) + " %"

class SOSLight(threading.Thread):
    _lock = threading.RLock()
    def __init__(self, id, title, port, feasible = True):
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        self.id = id
        self.title = title
        self.port = port
        self.pi = pigpio.pi()
        # Turn off the light
        self.pi.write(self.port, 0)
        self.feasible = feasible
        self.category = 'Switch'
    def run(self):
        while not self._stopevent.isSet():
            for i in range(3):
                self.pi.write(self.port, 1)
                self._stopevent.wait(0.5)
                self.pi.write(self.port, 0)
                self._stopevent.wait(0.2)
            self._stopevent.wait(0.4)
            for i in range(3):
                self.pi.write(self.port, 1)
                self._stopevent.wait(1.0)
                self.pi.write(self.port, 0)
                self._stopevent.wait(0.4)
            self._stopevent.wait(0.2)
            for i in range(3):
                self.pi.write(self.port, 1)
                self._stopevent.wait(0.5)
                self.pi.write(self.port, 0)
                self._stopevent.wait(0.2)
            self._stopevent.wait(0.8)
    def join(self, timeout = None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['port'] = self.port
        message['category'] = self.category
        message['value'] = self.isAlive()
        message['feasible'] = self.feasible
        return message
    def setValue(self, value):
        with SOSLight._lock:
            if value:
                self.start()
                self.title = self.title
            else:
                self.join()
        return value

class BreathLight(threading.Thread):
    _lock = threading.RLock()
    def __init__(self, id, title, port, feasible = True):
        self._stopevent = threading.Event()
        self._sleepperiod = 0.005
        threading.Thread.__init__(self)
        self.id = id
        self.title = title
        self.port = port
        self.pi = pigpio.pi()
        self.pi.set_PWM_frequency(self.port, 50)  # frequency 50Hz
        self.pi.set_PWM_range(self.port, 1000)    # set range 1000
        # Turn off the light
        self.pi.write(self.port, 0)
        self.feasible = feasible
        self.category = 'Switch'
    def run(self):
        # change variables as neceaasry
        while not self._stopevent.isSet():
            for i in xrange(0, 1000, 1):
                self.pi.set_PWM_dutycycle(self.port, i)
                self._stopevent.wait(self._sleepperiod)
            self._stopevent.wait(0.30)
            for i in xrange(999, -1, -1):
                self.pi.set_PWM_dutycycle(self.port, i)
                self._stopevent.wait(self._sleepperiod)
            self._stopevent.wait(0.20)
    def join(self, timeout = None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['port'] = self.port
        message['category'] = self.category
        message['value'] = self.isAlive()
        message['feasible'] = self.feasible
        return message
    def setValue(self, value):
        with BreathLight._lock:
            if value:
                self.start()
                self.title = self.title
            else:
                self.join()
        return value
