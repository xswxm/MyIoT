#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading, smbus
import sensors.bh1750fvi

class BH1750FVI:
    _lock = threading.RLock()
    def __init__(self, title, addr, id = 1000):
        self.id = id
        self.title = title
        self.addr = addr
        self.type = 'Value'
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