#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading
import sensors.dh11

_dh11Lock = threading.RLock()
class DH11Temp:
    global _dh11Lock
    def __init__(self, title, port, id = 1000):
        self.id = id
        self.title = title
        self.port = port
        self.type = 'Value'
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
