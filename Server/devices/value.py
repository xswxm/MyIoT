#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading
import RPi.GPIO as GPIO

# System
import os
class CPUTemp:
    _lock = threading.RLock()
    def __init__(self, title, id = 1000):
        self.id = id
        self.title = title
        self.type = 'Value'
        self.isThread = False
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['type'] = self.type
        message['value'] = self.getValue()
        return message
    def getValue(self):
        try:
            with CPUTemp._lock:
                res = os.popen('vcgencmd measure_temp').readline()
            return res.replace("temp=","").replace("'C\n","") + " 'C"
        except Exception as e:
            return str(e)

# Sensors
import smbus
import sensors.bh1750fvi
class BH1750FVI:
    _lock = threading.RLock()
    def __init__(self, title, addr, id = 1000):
        self.id = id
        self.title = title
        self.addr = addr
        self.type = 'Value'
        self.isThread = False
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['type'] = self.type
        message['value'] = self.getValue()
        return message
    def getValue(self):
        with BH1750FVI._lock:
            lux = sensors.bh1750fvi.get(self.addr)
        return str("%.1f" % lux) + " Lux"

import sensors.dh11
_dh11Lock = threading.RLock()
class DH11Temp:
    global _dh11Lock
    def __init__(self, title, port, id = 1000):
        self.id = id
        self.title = title
        self.port = port
        self.type = 'Value'
        self.isThread = False
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['type'] = self.type
        message['value'] = self.getValue()
        return message
    def getValue(self):
        with _dh11Lock:
            return str(sensors.dh11.getTemp(self.port)) + " 'C"
class DH11Humidity:
    global _dh11Lock
    def __init__(self, title, port, id = 1000):
        self.id = id
        self.title = title
        self.port = port
        self.type = 'Value'
        self.isThread = False
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['type'] = self.type
        message['value'] = self.getValue()
        return message
    def getValue(self):
        with _dh11Lock:
            return str(sensors.dh11.getHumidity(self.port)) + " %"