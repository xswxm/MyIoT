#!/usr/bin/python
# -*- encoding: utf-8 -*-

import threading, os

class CPUTemp:
    _lock = threading.RLock()
    def __init__(self, id, title, feasible = True):
        self.id = id
        self.title = title
        self.feasible = feasible
        self.category = 'Value'
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['category'] = self.category
        message['value'] = self.getValue()
        message['feasible'] = self.feasible
        return message
    def getValue(self):
        try:
            with CPUTemp._lock:
                res = os.popen('vcgencmd measure_temp').readline()
            return res.replace("temp=", "").replace("'C\n", "") + " °C"
        except Exception as e:
            return str(e)

class MemUse:
    _lock = threading.RLock()
    def __init__(self, id, title, feasible = True):
        self.id = id
        self.title = title
        self.feasible = feasible
        self.category = 'Value'
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['category'] = self.category
        message['value'] = self.getValue()
        message['feasible'] = self.feasible
        return message
    def getValue(self):
        try:
            with CPUTemp._lock:
                mem = os.popen("cat /proc/meminfo | awk '/Mem/ {print $2}'")
                memTotal = int(mem.readline()) / 1000
                memFree = int(mem.readline()) / 1000
                memUsed = memTotal - memFree
            return '{0:d}MB/{1:d}MB'.format(memUsed, memTotal)
        except Exception as e:
            return str(e)
