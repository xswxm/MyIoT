#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading, smbus
import sensors.bh1750fvi

class BH1750FVI:
    _lock = threading.RLock()
    def __init__(self, id, title, port, accessible = True):
        self.id = id
        self.title = title
        self.port = port
        self.accessible = accessible
        self.category = 'Value'
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['category'] = self.category
        message['value'] = self.getValue()
        message['accessible'] = self.accessible
        return message
    def getValue(self):
        with BH1750FVI._lock:
            lux = sensors.bh1750fvi.get(self.port)
        return str("%.1f" % lux) + " Lux"