#!/usr/bin/python
# -*- encoding: utf-8 -*-

import random
import threading

class Device:
    def __init__(self, title, type, value, id = 2000):
        self.id = id
        self.title = title
        self.type = type
        self.value = value
        self.sid = sid
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['type'] = self.type
        message['value'] = self.value
        return message

class RandomValue:
    _lock = threading.RLock()
    def __init__(self, title, id = 1000):
        self.id = id
        self.title = title
        self.type = 'Value'
    def description(self):
        message = {}
        message['id'] = self.id
        message['title'] = self.title
        message['type'] = self.type
        message['value'] = str(self.getValue(100))
        return message
    def getValue(self, value = 100):
        with RandomValue._lock:
            return str(random.randrange(0, value + 1, 2))
