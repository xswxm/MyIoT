#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading, smbus
import sensors.bh1750fvi

class BH1750FVI:
    _lock = threading.RLock()
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
        with BH1750FVI._lock:
            lux = sensors.bh1750fvi.get(self.port)
        return str("%.1f" % lux) + " Lux"