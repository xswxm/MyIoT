#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading
import sensors.dh11

_dh11Lock = threading.RLock()
class DH11Temp:
    global _dh11Lock
    def __init__(self, id, title, port, feasible = True):
        self.id = id
        self.title = title
        self.port = port
        self.feasible = feasible
        self.category = 'Value'
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
        with _dh11Lock:
            return str(sensors.dh11.getTemp(self.port)) + " °C"

class DH11Humidity:
    global _dh11Lock
    def __init__(self, id, title, port, feasible = True):
        self.id = id
        self.title = title
        self.port = port
        self.feasible = feasible
        self.category = 'Value'
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
        with _dh11Lock:
            return str(sensors.dh11.getHumidity(self.port)) + " %"
