#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading, os

class CPUTemp:
    _lock = threading.RLock()
    def __init__(self, id, title, accessible = True):
        self.id = id
        self.title = title
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
        try:
            with CPUTemp._lock:
                res = os.popen('vcgencmd measure_temp').readline()
            return res.replace("temp=", "").replace("'C\n", "") + " °C"
        except Exception as e:
            return str(e)
